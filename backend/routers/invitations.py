"""
routers/invitations.py — управление приглашениями в команду
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Invitation, User, Team, UserHackathon
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
    """Получить мои приглашения"""
    invitations = db.query(Invitation).filter(
        Invitation.user_id == current_user.id,
        Invitation.status == status_filter
    ).order_by(Invitation.created_at.desc()).all()
    
    return [InvitationResponse.model_validate(inv) for inv in invitations]


@router.post("/{invitation_id}/accept")
async def accept_invitation(
    invitation_id: int,
    request: InvitationAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принять или отклонить приглашение"""
    
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
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
    
    # Проверяем что приглашение еще не обработано
    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already processed"
        )
    
    if request.accept:
        # Принимаем приглашение
        
        # Проверяем что команда еще открыта
        team = db.query(Team).filter(Team.id == invitation.team_id).first()
        if team.status != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team is no longer accepting members"
            )
        
        # Добавляем пользователя в команду
        from models import TeamMember
        
        team_member = TeamMember(
            team_id=invitation.team_id,
            user_id=current_user.id
        )
        db.add(team_member)
        
        # Обновляем регистрацию пользователя на хакатон
        user_hackathon = db.query(UserHackathon).filter(
            UserHackathon.user_id == current_user.id,
            UserHackathon.hackathon_id == team.hackathon_id
        ).first()
        
        if user_hackathon:
            user_hackathon.team_id = team.id
        
        # Обновляем приглашение
        invitation.status = "accepted"
        invitation.responded_at = datetime.utcnow()
        
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
    
    invitations = db.query(Invitation).filter(
        Invitation.team_id == team_id,
        Invitation.status == "pending"
    ).all()
    
    return [InvitationResponse.model_validate(inv) for inv in invitations]
