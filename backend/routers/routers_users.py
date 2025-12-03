"""
routers/users.py — управление профилем пользователя
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserProfile, UserUpdateRequest, UserListItem
from dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Получить свой профиль"""
    return UserProfile.model_validate(current_user)


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить свой профиль"""
    
    if request.full_name:
        current_user.full_name = request.full_name
    if request.bio is not None:
        current_user.bio = request.bio
    if request.skills is not None:
        current_user.set_skills(request.skills)
    if request.role_preference:
        current_user.role_preference = request.role_preference
    if request.experience_level:
        current_user.experience_level = request.experience_level
    if request.avatar_url:
        current_user.avatar_url = request.avatar_url
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile.model_validate(current_user)


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить профиль другого пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile.model_validate(user)


@router.get("/hackathons/{hackathon_id}/participants", response_model=list[UserListItem])
async def get_hackathon_participants(
    hackathon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """Получить список участников хакатона (для поиска команды)"""
    
    from models import UserHackathon
    
    # Получаем всех участников хакатона кроме текущего пользователя
    participants = db.query(User).join(
        UserHackathon,
        User.id == UserHackathon.user_id
    ).filter(
        UserHackathon.hackathon_id == hackathon_id,
        User.id != current_user.id
    ).offset(skip).limit(limit).all()
    
    return [UserListItem.model_validate(p) for p in participants]
