from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(120), default='Alex Morgan')
    role: Mapped[str] = mapped_column(String(160), default='Computer Science student')
    skills: Mapped[list] = mapped_column(JSON, default=lambda: ['React', 'Python', 'SQL'])
    role_name: Mapped[str] = mapped_column(String(30), default='student')

class Opportunity(Base):
    __tablename__ = 'opportunities'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    company: Mapped[str] = mapped_column(String(120), index=True)
    location: Mapped[str] = mapped_column(String(120))
    match: Mapped[int] = mapped_column(Integer, default=75)
    tag: Mapped[str] = mapped_column(String(40), index=True)
    color: Mapped[str] = mapped_column(String(30), default='violet')
    skills: Mapped[list] = mapped_column(JSON, default=list)
    deadline: Mapped[str] = mapped_column(String(40), default='Open')

class Application(Base):
    __tablename__ = 'applications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunities.id'))
    status: Mapped[str] = mapped_column(String(30), default='Applied')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    opportunity: Mapped[Opportunity] = relationship()