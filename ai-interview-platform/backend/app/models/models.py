"""
SQLAlchemy models for database schema
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..core.database import Base


class UserRole(str, PyEnum):
    """User role enumeration"""
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"


class InterviewType(str, PyEnum):
    """Interview type enumeration"""
    MOCK = "mock"
    REAL = "real"


class InterviewStatus(str, PyEnum):
    """Interview status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """User model for candidates and interviewers"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CANDIDATE, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interviews = relationship("Interview", back_populates="candidate", foreign_keys="Interview.candidate_id")
    scheduled_interviews = relationship("Interview", back_populates="interviewer", foreign_keys="Interview.interviewer_id")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Domain(Base):
    """Interview domains"""
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", back_populates="domain", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="domain")
    
    def __repr__(self):
        return f"<Domain {self.name}>"


class Role(Base):
    """Interview roles within domains"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="roles")
    interviews = relationship("Interview", back_populates="role")
    
    __table_args__ = (
        # Prevent duplicate role names within a domain
        __import__('sqlalchemy').UniqueConstraint('domain_id', 'name', name='uq_domain_role'),
    )
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Interview(Base):
    """Interview records"""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for mock interviews
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    interview_type = Column(Enum(InterviewType), default=InterviewType.MOCK, nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED, nullable=False)
    difficulty = Column(String(50), default="intermediate")  # beginner, intermediate, advanced
    
    scheduled_at = Column(DateTime, nullable=True)  # For real interviews
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    overall_score = Column(Integer, default=0)  # 0-10
    accuracy_percentage = Column(Integer, default=0)
    feedback_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("User", back_populates="interviews", foreign_keys=[candidate_id])
    interviewer = relationship("User", back_populates="scheduled_interviews", foreign_keys=[interviewer_id])
    domain = relationship("Domain", back_populates="interviews")
    role = relationship("Role", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Interview {self.id} - {self.status}>"


class Question(Base):
    """Interview questions and answers"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    
    answer_text = Column(Text, nullable=True)
    audio_file_path = Column(String(500), nullable=True)
    video_file_path = Column(String(500), nullable=True)
    
    ai_feedback = Column(Text, nullable=True)
    score = Column(Integer, default=0)  # 0-10
    is_correct = Column(Boolean, default=False)
    weak_area = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interview = relationship("Interview", back_populates="questions")
    
    def __repr__(self):
        return f"<Question {self.question_number} - Interview {self.interview_id}>"


class Notification(Base):
    """In-app notifications for candidates"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"
