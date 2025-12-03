"""
schemas.py — Pydantic схемы для Request/Response
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ==================== AUTH ====================

class TelegramAuthRequest(BaseModel):
    """Запрос для регистрации через Telegram"""
    telegram_id: int
    telegram_username: str
    full_name: str
    avatar_url: Optional[str] = None


class TokenResponse(BaseModel):
    """Ответ с JWT токеном"""
    access_token: str
    token_type: str = "bearer"
    user_id: int


class AdminLoginRequest(BaseModel):
    """Запрос для входа админа"""
    email: str
    password: str


# ==================== USERS ====================

class UserProfile(BaseModel):
    """Профиль пользователя (основные данные)"""
    id: int
    telegram_id: int
    telegram_username: Optional[str]
    full_name: str
    bio: Optional[str]
    skills: List[str]
    role_preference: Optional[str]
    experience_level: str
    avatar_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Запрос для обновления профиля"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    role_preference: Optional[str] = None
    experience_level: Optional[str] = None
    avatar_url: Optional[str] = None


class UserListItem(BaseModel):
    """Пользователь в списке (для поиска команды)"""
    id: int
    full_name: str
    skills: List[str]
    role_preference: Optional[str]
    experience_level: str
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== HACKATHONS ====================

class HackathonCreate(BaseModel):
    """Создание хакатона (только админ)"""
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    max_team_size: int = 5


class HackathonUpdate(BaseModel):
    """Обновление хакатона"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    max_team_size: Optional[int] = None


class HackathonResponse(BaseModel):
    """Информация о хакатоне"""
    id: int
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    status: str
    max_team_size: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== TEAMS ====================

class TeamMemberResponse(BaseModel):
    """Член команды"""
    id: int
    full_name: str
    role_preference: Optional[str]
    skills: List[str]
    
    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    """Создание команды"""
    hackathon_id: int
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    """Информация о команде"""
    id: int
    hackathon_id: int
    name: str
    description: Optional[str]
    captain_id: int
    status: str
    created_at: datetime
    members: List[TeamMemberResponse] = []
    
    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    """Детальная информация о команде с капитаном"""
    captain: UserProfile


# ==================== INVITATIONS ====================

class InvitationCreate(BaseModel):
    """Отправка приглашения в команду"""
    user_id: int


class InvitationResponse(BaseModel):
    """Приглашение"""
    id: int
    team_id: int
    user_id: int
    sent_by_id: int
    status: str
    created_at: datetime
    responded_at: Optional[datetime]
    team: Optional[TeamResponse] = None
    sent_by: Optional[UserProfile] = None
    
    class Config:
        from_attributes = True


class InvitationAcceptRequest(BaseModel):
    """Принятие приглашения"""
    accept: bool = True  # True = accept, False = decline


# ==================== ANALYTICS ====================

class HackathonAnalytics(BaseModel):
    """Аналитика по хакатону"""
    total_participants: int
    total_teams: int
    participants_without_team: int
    participants_in_team: int
    average_team_size: float
    skills_frequency: dict  # {"Python": 10, "React": 8, ...}
    experience_distribution: dict  # {"junior": 20, "middle": 15, "senior": 5}


class ParticipantExportRow(BaseModel):
    """Строка для экспорта участников"""
    id: int
    full_name: str
    telegram_username: str
    skills: str
    role_preference: str
    experience_level: str
    team_name: Optional[str]
    team_status: Optional[str]


class TeamExportRow(BaseModel):
    """Строка для экспорта команд"""
    team_id: int
    team_name: str
    team_status: str
    captain_name: str
    member_count: int
    members: str  # comma-separated names


# ==================== ERROR RESPONSES ====================

class ErrorResponse(BaseModel):
    """Ошибка"""
    detail: str
    error_code: Optional[str] = None
