"""
routers/teams.py — управление командами
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Team, TeamMember, User, Invitation, UserHackathon, Hackathon
from schemas import TeamCreate, TeamResponse, TeamDetailResponse, MyTeamItem
from dependencies import get_current_user

router = APIRouter(prefix="/api/teams", tags=["teams"])


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
    
    # Проверяем что пользователь еще не в команде этого хакатона
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
    db.refresh(team)
    
    return TeamResponse.model_validate(team)


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


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о команде"""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return TeamDetailResponse.model_validate(team)


@router.get("/hackathons/{hackathon_id}", response_model=list[TeamResponse])
async def list_teams_by_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: str = "open"
):
    """Получить список команд в хакатоне"""
    teams = db.query(Team).filter(
        Team.hackathon_id == hackathon_id,
        Team.status == status_filter
    ).all()

    return [TeamResponse.model_validate(t) for t in teams]


@router.post("/{team_id}/invite")
async def invite_to_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Пригласить пользователя в команду (может только капитан)"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
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
    
    return {"message": "Member removed"}
