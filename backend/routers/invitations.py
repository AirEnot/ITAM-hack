"""
routers/invitations.py — управление приглашениями в команду
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, not_
from database import get_db
from models import Invitation, User, Team, UserHackathon, TeamMember, Hackathon
from schemas import InvitationResponse, InvitationAcceptRequest
from dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/invitations", tags=["invitations"])


@router.get("", response_model=list[InvitationResponse])
async def get_my_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str = "pending"
):
    """Получить мои приглашения и результаты заявок"""
    from datetime import timedelta
    
    # Получаем pending приглашения для пользователя
    # Исключаем заявки пользователя (где sent_by_id == captain_id и user_id == current_user.id)
    # Показываем только реальные приглашения от капитана к пользователю
    pending_invitations = db.query(Invitation).options(
        joinedload(Invitation.team).joinedload(Team.members).joinedload(TeamMember.user),
        joinedload(Invitation.sent_by)
    ).join(Team, Invitation.team_id == Team.id).filter(
        Invitation.user_id == current_user.id,
        Invitation.status == "pending",
        # Исключаем заявки пользователя: если sent_by_id == captain_id и user_id == current_user.id,
        # это заявка пользователя, которую еще не обработал капитан - не показываем её
        ~and_(
            Invitation.sent_by_id == Team.captain_id,
            Invitation.user_id == current_user.id
        )
    ).order_by(Invitation.created_at.desc()).all()
    
    # Получаем недавно обработанные заявки (accepted/declined за последние 7 дней)
    # Это заявки, которые пользователь подал (где sent_by_id == captain_id)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    processed_applications = db.query(Invitation).options(
        joinedload(Invitation.team).joinedload(Team.members).joinedload(TeamMember.user),
        joinedload(Invitation.sent_by)
    ).join(Team, Invitation.team_id == Team.id).filter(
        Invitation.user_id == current_user.id,
        Invitation.status.in_(["accepted", "declined"]),
        Invitation.sent_by_id == Team.captain_id,  # Это была заявка от пользователя
        Invitation.responded_at >= seven_days_ago  # Недавно обработанные
    ).order_by(Invitation.responded_at.desc()).all()
    
    # Объединяем pending приглашения и обработанные заявки
    all_invitations = list(pending_invitations) + list(processed_applications)
    
    result = []
    for inv in all_invitations:
        # Создаем базовый словарь для приглашения
        inv_dict = {
            "id": inv.id,
            "team_id": inv.team_id,
            "user_id": inv.user_id,
            "sent_by_id": inv.sent_by_id,
            "status": inv.status,
            "created_at": inv.created_at,
            "responded_at": inv.responded_at,
        }
        
        # Добавляем данные команды
        if inv.team:
            from schemas import TeamResponse, TeamMemberResponse
            try:
                # Создаем список участников команды
                members_data = []
                if hasattr(inv.team, 'members') and inv.team.members:
                    for member in inv.team.members:
                        if hasattr(member, 'user') and member.user:
                            members_data.append(TeamMemberResponse(
                                id=member.user.id,
                                full_name=member.user.full_name,
                                role_preference=member.user.role_preference,
                                skills=member.user.get_skills() if hasattr(member.user, 'get_skills') else []
                            ))
                
                inv_dict["team"] = TeamResponse(
                    id=inv.team.id,
                    hackathon_id=inv.team.hackathon_id,
                    name=inv.team.name,
                    description=inv.team.description,
                    captain_id=inv.team.captain_id,
                    status=inv.team.status,
                    created_at=inv.team.created_at,
                    members=members_data
                )
            except Exception as e:
                # Если не удалось создать TeamResponse, создаем упрощенную версию
                from schemas import TeamResponse
                inv_dict["team"] = TeamResponse(
                    id=inv.team.id,
                    hackathon_id=inv.team.hackathon_id,
                    name=inv.team.name,
                    description=inv.team.description,
                    captain_id=inv.team.captain_id,
                    status=inv.team.status,
                    created_at=inv.team.created_at,
                    members=[]
                )
        
        # Добавляем данные отправителя
        if inv.sent_by:
            from schemas import UserProfile
            try:
                inv_dict["sent_by"] = UserProfile.model_validate(inv.sent_by)
            except Exception as e:
                # Если не удалось создать UserProfile, создаем упрощенную версию
                inv_dict["sent_by"] = UserProfile(
                    id=inv.sent_by.id,
                    telegram_id=inv.sent_by.telegram_id,
                    telegram_username=inv.sent_by.telegram_username,
                    full_name=inv.sent_by.full_name,
                    bio=inv.sent_by.bio,
                    skills=inv.sent_by.get_skills(),
                    role_preference=inv.sent_by.role_preference,
                    experience_level=inv.sent_by.experience_level,
                    avatar_url=inv.sent_by.avatar_url,
                    created_at=inv.sent_by.created_at
                )
        
        result.append(InvitationResponse(**inv_dict))
    
    return result


@router.post("/{invitation_id}/accept")
async def accept_invitation(
    invitation_id: int,
    request: InvitationAcceptRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принять или отклонить приглашение"""
    
    invitation = db.query(Invitation).options(
        joinedload(Invitation.team)
    ).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    # Проверяем что приглашение адресовано текущему пользователю
    if invitation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is not for you"
        )
    
    # Определяем, это приглашение или заявка.
    # Приглашение: отправитель — капитан команды (sent_by_id == captain_id).
    # Заявка: отправитель — не капитан (sent_by_id != captain_id). Для заявок используется /approve|/reject.
    team = invitation.team
    if team and invitation.sent_by_id != team.captain_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This is an application, not an invitation. Please wait for the captain's response."
        )
    
    # Проверяем что приглашение еще не обработано
    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already processed"
        )
    
    if request.accept:
        # Принимаем приглашение
        try:
            # Используем уже загруженную команду
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Team not found"
                )
            
            if team.status != "open":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team is no longer accepting members"
                )
            
            # Проверяем, что пользователь зарегистрирован на хакатон
            user_hackathon = db.query(UserHackathon).filter(
                UserHackathon.user_id == current_user.id,
                UserHackathon.hackathon_id == team.hackathon_id
            ).first()
            
            if not user_hackathon:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You must register for the hackathon first"
                )
            
            # Проверяем, что пользователь не в другой команде
            if user_hackathon.team_id and user_hackathon.team_id != team.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already in another team for this hackathon"
                )
            
            # Проверяем, что пользователь еще не в этой команде
            from models import TeamMember
            existing_member = db.query(TeamMember).filter(
                TeamMember.team_id == invitation.team_id,
                TeamMember.user_id == current_user.id
            ).first()
            
            if existing_member:
                # Пользователь уже в команде, просто обновляем статус приглашения
                invitation.status = "accepted"
                invitation.responded_at = datetime.utcnow()
            else:
                # Добавляем пользователя в команду
                team_member = TeamMember(
                    team_id=invitation.team_id,
                    user_id=current_user.id
                )
                db.add(team_member)
                
                # Обновляем регистрацию пользователя на хакатон
                user_hackathon.team_id = team.id
                
                # Обновляем приглашение
                invitation.status = "accepted"
                invitation.responded_at = datetime.utcnow()
        except HTTPException:
            raise
        except Exception as e:
            # Логируем ошибку для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error accepting invitation {invitation_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
        
    else:
        # Отклоняем приглашение
        invitation.status = "declined"
        invitation.responded_at = datetime.utcnow()
    
    db.commit()
    
    action = "accepted" if request.accept else "declined"
    return {"message": f"Invitation {action}", "invitation_id": invitation_id}


@router.get("/team/{team_id}/pending", response_model=list[InvitationResponse])
async def get_team_pending_invitations(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список отправленных приглашений команды (для капитана)"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Проверяем что это капитан команды
    if team.captain_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team captain can view invitations"
        )
    
    invitations = db.query(Invitation).options(
        joinedload(Invitation.user),
        joinedload(Invitation.team)
    ).filter(
        Invitation.team_id == team_id,
        Invitation.status == "pending"
    ).all()
    
    result = []
    for inv in invitations:
        inv_dict = {
            "id": inv.id,
            "team_id": inv.team_id,
            "user_id": inv.user_id,
            "sent_by_id": inv.sent_by_id,
            "status": inv.status,
            "created_at": inv.created_at,
            "responded_at": inv.responded_at,
        }
        # Добавляем данные команды
        if inv.team:
            from schemas import TeamResponse
            inv_dict["team"] = TeamResponse.model_validate(inv.team)
        # Добавляем данные пользователя (кто подал заявку)
        if inv.user:
            from schemas import UserProfile
            inv_dict["user"] = UserProfile.model_validate(inv.user)
        # Добавляем данные отправителя
        if inv.sent_by:
            from schemas import UserProfile
            inv_dict["sent_by"] = UserProfile.model_validate(inv.sent_by)
        result.append(InvitationResponse(**inv_dict))
    
    return result


@router.get("/applications", response_model=list[InvitationResponse])
async def get_my_team_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить заявки на вступление в мои команды (для капитана)"""
    
    # Находим все команды, где пользователь является капитаном
    my_teams = db.query(Team).filter(Team.captain_id == current_user.id).all()
    
    if not my_teams:
        return []
    
    team_ids = [team.id for team in my_teams]
    
    # Находим все заявки для этих команд
    # Заявка: sent_by_id == captain_id (чтобы капитан получил уведомление), user_id != captain_id (пользователь подает заявку)
    invitations = db.query(Invitation).options(
        joinedload(Invitation.user),
        joinedload(Invitation.team).joinedload(Team.members).joinedload(TeamMember.user),
        joinedload(Invitation.sent_by)
    ).join(Team, Invitation.team_id == Team.id).filter(
        and_(
            Invitation.team_id.in_(team_ids),
            Invitation.status == "pending",
            Team.captain_id == current_user.id,
            Invitation.sent_by_id == Team.captain_id,  # заявка направлена капитану
            Invitation.user_id != Team.captain_id  # исключаем капитана как получателя (пользователь подает заявку)
        )
    ).all()
    
    result = []
    for inv in invitations:
        inv_dict = {
            "id": inv.id,
            "team_id": inv.team_id,
            "user_id": inv.user_id,
            "sent_by_id": inv.sent_by_id,
            "status": inv.status,
            "created_at": inv.created_at,
            "responded_at": inv.responded_at,
        }
        # Добавляем данные команды
        if inv.team:
            from schemas import TeamResponse, TeamMemberResponse
            try:
                # Создаем список участников команды
                members_data = []
                if hasattr(inv.team, 'members') and inv.team.members:
                    for member in inv.team.members:
                        if hasattr(member, 'user') and member.user:
                            members_data.append(TeamMemberResponse(
                                id=member.user.id,
                                full_name=member.user.full_name,
                                role_preference=member.user.role_preference,
                                skills=member.user.get_skills() if hasattr(member.user, 'get_skills') else []
                            ))
                
                inv_dict["team"] = TeamResponse(
                    id=inv.team.id,
                    hackathon_id=inv.team.hackathon_id,
                    name=inv.team.name,
                    description=inv.team.description,
                    captain_id=inv.team.captain_id,
                    status=inv.team.status,
                    created_at=inv.team.created_at,
                    members=members_data
                )
            except Exception as e:
                # Если не удалось создать TeamResponse, создаем упрощенную версию
                from schemas import TeamResponse
                inv_dict["team"] = TeamResponse(
                    id=inv.team.id,
                    hackathon_id=inv.team.hackathon_id,
                    name=inv.team.name,
                    description=inv.team.description,
                    captain_id=inv.team.captain_id,
                    status=inv.team.status,
                    created_at=inv.team.created_at,
                    members=[]
                )
        # Добавляем данные пользователя (кто подал заявку)
        if inv.user:
            from schemas import UserProfile
            try:
                inv_dict["user"] = UserProfile.model_validate(inv.user)
            except Exception as e:
                # Если не удалось создать UserProfile, создаем упрощенную версию
                inv_dict["user"] = UserProfile(
                    id=inv.user.id,
                    telegram_id=inv.user.telegram_id,
                    telegram_username=inv.user.telegram_username,
                    full_name=inv.user.full_name,
                    bio=inv.user.bio,
                    skills=inv.user.get_skills() if hasattr(inv.user, 'get_skills') else [],
                    role_preference=inv.user.role_preference,
                    experience_level=inv.user.experience_level,
                    avatar_url=inv.user.avatar_url,
                    created_at=inv.user.created_at
                )
        # Добавляем данные отправителя
        if inv.sent_by:
            from schemas import UserProfile
            try:
                inv_dict["sent_by"] = UserProfile.model_validate(inv.sent_by)
            except Exception as e:
                # Если не удалось создать UserProfile, создаем упрощенную версию
                inv_dict["sent_by"] = UserProfile(
                    id=inv.sent_by.id,
                    telegram_id=inv.sent_by.telegram_id,
                    telegram_username=inv.sent_by.telegram_username,
                    full_name=inv.sent_by.full_name,
                    bio=inv.sent_by.bio,
                    skills=inv.sent_by.get_skills() if hasattr(inv.sent_by, 'get_skills') else [],
                    role_preference=inv.sent_by.role_preference,
                    experience_level=inv.sent_by.experience_level,
                    avatar_url=inv.sent_by.avatar_url,
                    created_at=inv.sent_by.created_at
                )
        result.append(InvitationResponse(**inv_dict))
    
    return result


@router.post("/{invitation_id}/approve")
async def approve_application(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принять заявку на вступление в команду (может только капитан)"""
    try:
        invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Проверяем что это приглашение для команды, где пользователь является капитаном
        team = db.query(Team).filter(Team.id == invitation.team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        if team.captain_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team captain can approve applications"
            )
        
        # Проверяем что приглашение еще не обработано
        if invitation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application already processed"
            )
        
        # Проверяем что команда еще открыта
        if team.status != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team is no longer accepting members"
            )
        
        # Проверяем максимальное количество участников
        hackathon = db.query(Hackathon).filter(Hackathon.id == team.hackathon_id).first()
        if hackathon:
            current_members_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
            if current_members_count >= hackathon.max_team_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Team is full. Maximum team size is {hackathon.max_team_size}"
                )
        
        # Проверяем, что пользователь зарегистрирован на хакатон
        user_hackathon = db.query(UserHackathon).filter(
            UserHackathon.user_id == invitation.user_id,
            UserHackathon.hackathon_id == team.hackathon_id
        ).first()
        
        if not user_hackathon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must register for the hackathon first"
            )
        
        # Проверяем, что пользователь не в другой команде
        if user_hackathon.team_id and user_hackathon.team_id != team.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already in another team for this hackathon"
            )
        
        # Проверяем, что пользователь еще не в этой команде
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == invitation.team_id,
            TeamMember.user_id == invitation.user_id
        ).first()
        
        if existing_member:
            # Пользователь уже в команде, просто обновляем статус приглашения
            invitation.status = "accepted"
            invitation.responded_at = datetime.utcnow()
        else:
            # Добавляем пользователя в команду
            team_member = TeamMember(
                team_id=invitation.team_id,
                user_id=invitation.user_id
            )
            db.add(team_member)
            
            # Обновляем регистрацию пользователя на хакатон
            user_hackathon.team_id = team.id
            
            # Обновляем приглашение
            invitation.status = "accepted"
            invitation.responded_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Application approved", "invitation_id": invitation_id}
    except HTTPException:
        # Пробрасываем HTTP ошибки как есть
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error approving application {invitation_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving application: {str(e)}"
        )


@router.post("/{invitation_id}/reject")
async def reject_application(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отклонить заявку на вступление в команду (может только капитан)"""
    
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    # Проверяем что это приглашение для команды, где пользователь является капитаном
    team = db.query(Team).filter(Team.id == invitation.team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if team.captain_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team captain can reject applications"
        )
    
    # Проверяем что приглашение еще не обработано
    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application already processed"
        )
    
    # Отклоняем приглашение
    invitation.status = "declined"
    invitation.responded_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Application rejected", "invitation_id": invitation_id}
