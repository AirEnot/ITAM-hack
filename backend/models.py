"""
models.py — SQLAlchemy ORM модели (таблицы)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from database import Base


class User(Base):
    """Таблица пользователей (участников)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    telegram_username = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    skills = Column(Text, default="[]")  # JSON строка
    role_preference = Column(String, nullable=True)  # frontend, backend, fullstack, designer
    experience_level = Column(String, default="junior")  # junior, middle, senior
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hackathons = relationship("UserHackathon", back_populates="user", cascade="all, delete-orphan")
    teams_created = relationship("Team", back_populates="captain", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    invitations_sent = relationship("Invitation", foreign_keys="Invitation.sent_by_id", back_populates="sent_by")
    invitations_received = relationship("Invitation", foreign_keys="Invitation.user_id", back_populates="user")
    
    def get_skills(self):
        """Получить список навыков из JSON"""
        try:
            return json.loads(self.skills) if self.skills else []
        except:
            return []
    
    def set_skills(self, skills_list):
        """Установить навыки из списка"""
        self.skills = json.dumps(skills_list)


class Hackathon(Base):
    """Таблица хакатонов"""
    __tablename__ = "hackathons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, default="upcoming")  # upcoming, active, finished
    max_team_size = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("UserHackathon", back_populates="hackathon", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="hackathon", cascade="all, delete-orphan")


class Team(Base):
    """Таблица команд"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    hackathon_id = Column(Integer, ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    captain_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="open")  # open, closed, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hackathon = relationship("Hackathon", back_populates="teams")
    captain = relationship("User", back_populates="teams_created")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="team", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class TeamMember(Base):
    """Таблица членов команд (many-to-many)"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="active")  # active, left
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


class Invitation(Base):
    """Таблица приглашений в команду"""
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sent_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, declined
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="invitations")
    user = relationship("User", foreign_keys=[user_id], back_populates="invitations_received")
    sent_by = relationship("User", foreign_keys=[sent_by_id], back_populates="invitations_sent")


class UserHackathon(Base):
    """Таблица участия пользователя в хакатоне"""
    __tablename__ = "user_hackathon"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(Integer, ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="hackathons")
    hackathon = relationship("Hackathon", back_populates="users")


class Admin(Base):
    """Таблица администраторов"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
