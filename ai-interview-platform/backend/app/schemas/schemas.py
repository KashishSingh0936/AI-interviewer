"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRoleSchema(str, Enum):
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"

class InterviewTypeSchema(str, Enum):
    MOCK = "mock"
    REAL = "real"

class InterviewStatusSchema(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============= USER SCHEMAS =============
class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRoleSchema


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRoleSchema
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= DOMAIN & ROLE SCHEMAS =============
class RoleResponse(BaseModel):
    """Role response schema"""
    id: int
    name: str
    description: Optional[str]
    domain_id: int
    
    class Config:
        from_attributes = True


class DomainResponse(BaseModel):
    """Domain response schema"""
    id: int
    name: str
    description: Optional[str]
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True


class DomainCreate(BaseModel):
    """Domain creation schema"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class RoleCreate(BaseModel):
    """Role creation schema"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    domain_id: int


# ============= INTERVIEW SCHEMAS =============
class InterviewCreate(BaseModel):
    """Interview creation schema"""
    domain_id: int
    role_id: int
    interview_type: InterviewTypeSchema = InterviewTypeSchema.MOCK
    difficulty: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced)$")
    scheduled_at: Optional[datetime] = None
    interviewer_id: Optional[int] = None


class InterviewSchedule(BaseModel):
    """Interview scheduling schema (for interviewers)"""
    candidate_id: int
    domain_id: int
    role_id: int
    scheduled_at: datetime
    difficulty: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced)$")


class QuestionResponse(BaseModel):
    """Question response schema"""
    id: int
    question_number: int
    question_text: str
    answer_text: Optional[str]
    audio_file_path: Optional[str]
    video_file_path: Optional[str]
    ai_feedback: Optional[str]
    score: int
    is_correct: bool
    weak_area: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewResponse(BaseModel):
    """Interview response schema"""
    id: int
    candidate_id: int
    interviewer_id: Optional[int]
    domain_id: int
    role_id: int
    interview_type: InterviewTypeSchema
    status: InterviewStatusSchema
    difficulty: str
    overall_score: int
    accuracy_percentage: int
    feedback_summary: Optional[str]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    questions: List[QuestionResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewDetailResponse(InterviewResponse):
    """Detailed interview response with related data"""
    candidate: UserResponse
    interviewer: Optional[UserResponse]
    domain: DomainResponse
    role: RoleResponse


# ============= QUESTION ANSWER SCHEMAS =============
class AnswerSubmit(BaseModel):
    """Answer submission schema"""
    question_number: int
    answer_text: Optional[str] = None
    audio_file_path: Optional[str] = None
    video_file_path: Optional[str] = None


class AnswerFeedback(BaseModel):
    """Answer feedback schema (from AI)"""
    question_id: int
    question_number: int
    ai_feedback: str
    score: int
    is_correct: bool
    weak_area: Optional[str]


# ============= NOTIFICATION SCHEMAS =============
class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: int
    title: str
    message: str
    is_read: bool
    interview_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= ANALYTICS SCHEMAS =============
class UserAnalytics(BaseModel):
    """User analytics schema"""
    total_interviews: int
    completed_interviews: int
    average_score: float
    accuracy: float
    most_common_weak_areas: List[str]
    interview_history: List[InterviewResponse]


class OrgAnalytics(BaseModel):
    """Organization analytics schema"""
    total_candidates: int
    total_interviews: int
    average_candidate_score: float
    weak_areas_summary: dict  # {weak_area: count}
    top_performing_candidates: List[dict]
