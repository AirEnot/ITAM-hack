"""
routers/admin.py — админ-панель: управление хакатонами и аналитика
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Hackathon, User, Team, UserHackathon, TeamMember
from schemas import HackathonResponse, HackathonAnalytics, ParticipantExportRow, TeamExportRow
from dependencies import get_current_admin
import csv
import io
from collections import Counter
import json

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/hackathons", response_model=list[HackathonResponse])
async def list_all_hackathons(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Получить все хакатоны (админ)"""
    hackathons = db.query(Hackathon).order_by(Hackathon.created_at.desc()).all()
    return [HackathonResponse.model_validate(h) for h in hackathons]


@router.get("/{hackathon_id}/analytics", response_model=HackathonAnalytics)
async def get_hackathon_analytics(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Получить аналитику по хакатону"""
    
    # Проверяем что хакатон существует
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Получаем всех участников хакатона
    registrations = db.query(UserHackathon).filter(
        UserHackathon.hackathon_id == hackathon_id
    ).all()
    
    total_participants = len(registrations)
    participants_in_team = len([r for r in registrations if r.team_id])
    participants_without_team = total_participants - participants_in_team
    
    # Получаем команды
    teams = db.query(Team).filter(Team.hackathon_id == hackathon_id).all()
    total_teams = len(teams)
    average_team_size = total_participants / total_teams if total_teams > 0 else 0
    
    # Собираем навыки и опыт
    all_users = db.query(User).join(
        UserHackathon,
        User.id == UserHackathon.user_id
    ).filter(UserHackathon.hackathon_id == hackathon_id).all()
    
    all_skills = []
    experience_levels = []
    
    for user in all_users:
        all_skills.extend(user.get_skills())
        experience_levels.append(user.experience_level)
    
    skills_frequency = dict(Counter(all_skills))
    experience_distribution = dict(Counter(experience_levels))
    
    return HackathonAnalytics(
        total_participants=total_participants,
        total_teams=total_teams,
        participants_without_team=participants_without_team,
        participants_in_team=participants_in_team,
        average_team_size=round(average_team_size, 2),
        skills_frequency=skills_frequency,
        experience_distribution=experience_distribution
    )


@router.get("/{hackathon_id}/participants/export")
async def export_participants(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Экспортировать участников в CSV"""
    
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Получаем всех участников
    users = db.query(User).join(
        UserHackathon,
        User.id == UserHackathon.user_id
    ).filter(UserHackathon.hackathon_id == hackathon_id).all()
    
    # Создаем CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "ID",
        "Full Name",
        "Telegram Username",
        "Skills",
        "Role Preference",
        "Experience Level",
        "Team Name",
        "Team Status"
    ])
    
    for user in users:
        # Получаем команду пользователя если она есть
        registration = db.query(UserHackathon).filter(
            UserHackathon.user_id == user.id,
            UserHackathon.hackathon_id == hackathon_id
        ).first()
        
        team_name = ""
        team_status = ""
        
        if registration and registration.team_id:
            team = db.query(Team).filter(Team.id == registration.team_id).first()
            if team:
                team_name = team.name
                team_status = team.status
        
        writer.writerow([
            user.id,
            user.full_name,
            user.telegram_username or "",
            ", ".join(user.get_skills()),
            user.role_preference or "",
            user.experience_level,
            team_name,
            team_status
        ])
    
    # Возвращаем CSV файл
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=participants_{hackathon_id}.csv"}
    )


@router.get("/{hackathon_id}/teams/export")
async def export_teams(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Экспортировать команды в CSV"""
    
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Получаем все команды
    teams = db.query(Team).filter(Team.hackathon_id == hackathon_id).all()
    
    # Создаем CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Team ID",
        "Team Name",
        "Team Status",
        "Captain Name",
        "Member Count",
        "Members"
    ])
    
    for team in teams:
        captain = db.query(User).filter(User.id == team.captain_id).first()
        members = db.query(User).join(
            TeamMember,
            User.id == TeamMember.user_id
        ).filter(TeamMember.team_id == team.id).all()
        
        member_names = ", ".join([m.full_name for m in members])
        
        writer.writerow([
            team.id,
            team.name,
            team.status,
            captain.full_name if captain else "",
            len(members),
            member_names
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=teams_{hackathon_id}.csv"}
    )
