"""
routers/hackathons.py — управление хакатонами
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Hackathon, UserHackathon, User
from schemas import HackathonResponse, HackathonCreate, HackathonUpdate
from dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/api/hackathons", tags=["hackathons"])


@router.get("", response_model=list[HackathonResponse])
async def list_hackathons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """Получить список доступных хакатонов"""
    hackathons = db.query(Hackathon).offset(skip).limit(limit).all()
    return [HackathonResponse.model_validate(h) for h in hackathons]


@router.get("/{hackathon_id}")
async def get_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о хакатоне с информацией о регистрации"""
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем, зарегистрирован ли пользователь
    registration = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.hackathon_id == hackathon_id
    ).first()
    
    hackathon_data = HackathonResponse.model_validate(hackathon).model_dump()
    hackathon_data["is_registered"] = registration is not None
    hackathon_data["team_id"] = registration.team_id if registration else None
    
    return hackathon_data


@router.post("/{hackathon_id}/register")
async def register_for_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Зарегистрироваться на хакатон"""
    
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем что пользователь еще не зарегистрирован
    existing = db.query(UserHackathon).filter(
        UserHackathon.user_id == current_user.id,
        UserHackathon.hackathon_id == hackathon_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this hackathon"
        )
    
    # Регистрируем пользователя
    user_hackathon = UserHackathon(
        user_id=current_user.id,
        hackathon_id=hackathon_id
    )
    
    db.add(user_hackathon)
    db.commit()
    
    return {"message": "Registered successfully", "hackathon_id": hackathon_id}


# ADMIN ENDPOINTS

@router.post("", response_model=HackathonResponse)
async def create_hackathon(
    request: HackathonCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Создать новый хакатон (только админ)"""
    
    # Проверяем что хакатон с таким названием не существует
    existing = db.query(Hackathon).filter(Hackathon.name == request.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hackathon with this name already exists"
        )
    
    hackathon = Hackathon(
        name=request.name,
        description=request.description,
        start_date=request.start_date,
        end_date=request.end_date,
        max_team_size=request.max_team_size
    )
    
    db.add(hackathon)
    db.commit()
    db.refresh(hackathon)
    
    return HackathonResponse.model_validate(hackathon)


@router.put("/{hackathon_id}", response_model=HackathonResponse)
async def update_hackathon(
    hackathon_id: int,
    request: HackathonUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Обновить хакатон (только админ)"""
    
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if request.name:
        hackathon.name = request.name
    if request.description is not None:
        hackathon.description = request.description
    if request.start_date:
        hackathon.start_date = request.start_date
    if request.end_date:
        hackathon.end_date = request.end_date
    if request.status:
        hackathon.status = request.status
    if request.max_team_size:
        hackathon.max_team_size = request.max_team_size
    
    db.commit()
    db.refresh(hackathon)
    
    return HackathonResponse.model_validate(hackathon)
