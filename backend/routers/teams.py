"""
routers/teams.py — управление командами
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Team, TeamMember, User, Invitation, UserHackathon, Hackathon
from schemas import TeamCreate, TeamResponse, TeamDetailResponse, MyTeamItem, TeamMemberResponse, UserProfile
from dependencies import get_current_user

router = APIRouter(prefix="/api/teams", tags=["teams"])


def team_to_response(team: Team) -> TeamResponse:
    """Преобразовать объект Team в TeamResponse с загруженными данными пользователей"""
    members_data = []
    for member in team.members:
        user = member.user
        members_data.append(TeamMemberResponse(
            id=user.id,
            full_name=user.full_name,
            role_preference=user.role_preference,
            skills=user.get_skills()
        ))
    
    return TeamResponse(
        id=team.id,
        hackathon_id=team.hackathon_id,
        name=team.name,
        description=team.description,
        captain_id=team.captain_id,
        status=team.status,
        created_at=team.created_at,
        members=members_data
    )


@router.post("", response_model=TeamResponse)
async def create_team(
    request: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новую команду"""
    
    # Проверяем что хакатон существует
    hackathon = db.query(Hackathon).filter(Hackathon.id == request.hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем что пользователь зарегистрирован на хакатон
    registration = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.hackathon_id == request.hackathon_id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must register for the hackathon first"
        )
    
    # Проверяем что пользователь еще не создал команду как капитан для этого хакатона
    existing_captain_team = db.query(Team).filter(
        Team.captain_id == current_user.id,
        Team.hackathon_id == request.hackathon_id
    ).first()
    
    if existing_captain_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already created a team for this hackathon. One user can create only one team per hackathon."
        )
    
    # Проверяем что пользователь еще не в команде этого хакатона (как участник)
    existing_team = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.hackathon_id == request.hackathon_id,
        UserHackathon.team_id != None
    ).first()
    
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in a team for this hackathon"
        )
    
    # Создаем команду
    team = Team(
        hackathon_id=request.hackathon_id,
        name=request.name,
        description=request.description,
        captain_id=current_user.id
    )
    
    db.add(team)
    db.flush()  # Чтобы получить ID
    
    # Добавляем капитана в команду
    team_member = TeamMember(
        team_id=team.id,
        user_id=current_user.id
    )
    
    db.add(team_member)
    
    # Обновляем регистрацию пользователя
    registration.team_id = team.id
    
    db.commit()
    
    # Загружаем команду с связанными данными пользователей
    team = db.query(Team).options(
        joinedload(Team.members).joinedload(TeamMember.user)
    ).filter(Team.id == team.id).first()
    
    return team_to_response(team)


@router.get("/can-create/{hackathon_id}")
async def can_create_team(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Проверить, может ли пользователь создать команду для данного хакатона.
    Возвращает информацию о возможности создания команды.
    """
    # Проверяем что хакатон существует
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not hackathon:
        return {
            "can_create": False,
            "reason": "Hackathon not found"
        }
    
    # Проверяем что пользователь зарегистрирован на хакатон
    registration = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.hackathon_id == hackathon_id
    ).first()
    
    if not registration:
        return {
            "can_create": False,
            "reason": "You must register for the hackathon first"
        }
    
    # Проверяем что пользователь еще не создал команду как капитан
    existing_captain_team = db.query(Team).filter(
        Team.captain_id == current_user.id,
        Team.hackathon_id == hackathon_id
    ).first()
    
    if existing_captain_team:
        return {
            "can_create": False,
            "reason": "You have already created a team for this hackathon"
        }
    
    # Проверяем что пользователь еще не в команде этого хакатона
    if registration.team_id is not None:
        return {
            "can_create": False,
            "reason": "You are already in a team for this hackathon"
        }
    
    return {
        "can_create": True,
        "reason": None
    }


@router.get("/my", response_model=list[MyTeamItem])
async def get_my_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список команд, в которых состоит текущий пользователь,
    вместе с информацией о хакатоне.
    """
    # Находим все записи участия пользователя в хакатонах, где задана команда
    user_hackathons = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.team_id != None
    ).all()

    if not user_hackathons:
        return []

    team_ids = {uh.team_id for uh in user_hackathons if uh.team_id is not None}

    if not team_ids:
        return []

    teams = db.query(Team).join(Hackathon, Team.hackathon_id == Hackathon.id).filter(
        Team.id.in_(team_ids)
    ).all()

    result: list[MyTeamItem] = []
    for team in teams:
        result.append(
            MyTeamItem(
                id=team.id,
                name=team.name,
                description=team.description,
                hackathon_id=team.hackathon_id,
                hackathon_name=team.hackathon.name if team.hackathon else "",
                status=team.status,
            )
        )

    return result


@router.post("/{team_id}/apply")
async def apply_to_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Подать заявку на вступление в команду (создает приглашение от пользователя к капитану)"""
    
    team = db.query(Team).options(
        joinedload(Team.members),
        joinedload(Team.hackathon)
    ).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Проверяем что команда открыта
    if team.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is not accepting new members"
        )
    
    # Проверяем что пользователь не капитан
    if team.captain_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are the captain of this team"
        )
    
    # Проверяем максимальное количество участников
    hackathon = team.hackathon
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hackathon not found for this team"
        )
    
    current_members_count = len(team.members) if team.members else 0
    if current_members_count >= hackathon.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is full. Maximum team size is {hackathon.max_team_size}"
        )
    
    # Проверяем что пользователь зарегистрирован на хакатон
    user_hackathon = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.hackathon_id == team.hackathon_id
    ).first()
    
    if not user_hackathon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must register for the hackathon first"
        )
    
    # Проверяем что пользователь не в другой команде
    if user_hackathon.team_id and user_hackathon.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in another team for this hackathon"
        )
    
    # Проверяем что пользователь не в этой команде
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this team"
        )
    
    # Проверяем что нет активного приглашения
    existing_invitation = db.query(Invitation).filter(
        Invitation.team_id == team_id,
        Invitation.user_id == current_user.id,
        Invitation.status == "pending"
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending invitation to this team"
        )
    
    # Создаем заявку: отправитель — сам пользователь (applicant)
    invitation = Invitation(
        team_id=team_id,
        user_id=current_user.id,
        sent_by_id=current_user.id
    )
    
    db.add(invitation)
    db.commit()
    
    return {
        "message": "Application sent. The team captain will review your request.",
        "invitation_id": invitation.id
    }


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о команде"""
    team = db.query(Team).options(
        joinedload(Team.members).joinedload(TeamMember.user),
        joinedload(Team.captain),
        joinedload(Team.hackathon)
    ).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Преобразуем в TeamResponse
    team_response = team_to_response(team)
    
    # Добавляем данные капитана для TeamDetailResponse
    captain = team.captain
    captain_profile = UserProfile(
        id=captain.id,
        telegram_id=captain.telegram_id,
        telegram_username=captain.telegram_username,
        full_name=captain.full_name,
        bio=captain.bio,
        skills=captain.get_skills(),
        role_preference=captain.role_preference,
        experience_level=captain.experience_level,
        avatar_url=captain.avatar_url,
        created_at=captain.created_at
    )
    
    team_dict = team_response.model_dump()
    team_dict["captain"] = captain_profile
    
    # Добавляем информацию о хакатоне
    if team.hackathon:
        from schemas import HackathonResponse
        team_dict["hackathon"] = HackathonResponse.model_validate(team.hackathon)
        team_dict["max_team_size"] = team.hackathon.max_team_size
    
    return TeamDetailResponse(**team_dict)


@router.get("/hackathons/{hackathon_id}", response_model=list[TeamResponse])
async def list_teams_by_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: str = "open"
):
    """Получить список команд в хакатоне"""
    teams = db.query(Team).options(
        joinedload(Team.members).joinedload(TeamMember.user),
        joinedload(Team.hackathon)
    ).filter(
        Team.hackathon_id == hackathon_id,
        Team.status == status_filter
    ).all()

    result = []
    for team in teams:
        team_response = team_to_response(team)
        # Добавляем max_team_size из хакатона
        if team.hackathon:
            team_dict = team_response.model_dump()
            team_dict["max_team_size"] = team.hackathon.max_team_size
            result.append(TeamResponse(**team_dict))
        else:
            result.append(team_response)
    
    return result


@router.post("/{team_id}/invite")
async def invite_to_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Пригласить пользователя в команду (может только капитан)"""
    
    team = db.query(Team).options(
        joinedload(Team.members),
        joinedload(Team.hackathon)
    ).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Проверяем что текущий пользователь - капитан команды
    if team.captain_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team captain can send invitations"
        )
    
    # Проверяем максимальное количество участников
    hackathon = team.hackathon
    current_members_count = len(team.members) if team.members else 0
    if current_members_count >= hackathon.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is full. Maximum team size is {hackathon.max_team_size}"
        )
    
    # Проверяем что приглашаемый пользователь существует
    invitee = db.query(User).filter(User.id == user_id).first()
    if not invitee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Проверяем что пользователь еще не приглашен и не в команде
    existing_invitation = db.query(Invitation).filter(
        Invitation.team_id == team_id,
        Invitation.user_id == user_id,
        Invitation.status == "pending"
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a pending invitation"
        )
    
    # Проверяем что пользователь не в команде этого хакатона
    in_team = db.query(UserHackathon).filter(
        UserHackathon.user_id == user_id,
        UserHackathon.hackathon_id == team.hackathon_id,
        UserHackathon.team_id != None
    ).first()
    
    if in_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in a team for this hackathon"
        )
    
    # Создаем приглашение
    invitation = Invitation(
        team_id=team_id,
        user_id=user_id,
        sent_by_id=current_user.id
    )
    
    db.add(invitation)
    db.commit()
    
    return {
        "message": "Invitation sent",
        "invitation_id": invitation.id
    }


@router.delete("/{team_id}/members/{user_id}")
async def remove_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить члена команды (может только капитан или сам пользователь)"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Проверяем права
    if team.captain_id != current_user.id and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove this member"
        )
    
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in team"
        )
    
    # Удаляем члена команды
    db.delete(member)
    
    # Обновляем регистрацию пользователя
    registration = db.query(UserHackathon).filter(
        UserHackathon.user_id == user_id,
        UserHackathon.team_id == team_id
    ).first()
    
    if registration:
        registration.team_id = None
    
    db.commit()
    
    return {"message": "Member removed from team"}


@router.post("/{team_id}/leave")
async def leave_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Выйти из команды (может только участник, не капитан)"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Нельзя выйти если ты капитан
    if team.captain_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team captain cannot leave the team. Transfer captaincy first or delete the team."
        )
    
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this team"
        )
    
    # Удаляем члена команды
    db.delete(member)
    
    # Обновляем регистрацию пользователя
    registration = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.team_id == team_id
    ).first()
    
    if registration:
        registration.team_id = None
    
    db.commit()
    
    return {"message": "You have left the team"}
