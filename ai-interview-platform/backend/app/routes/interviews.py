"""
Interview routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.security import decode_access_token
from ..models.models import User, InterviewType
from ..schemas.schemas import (
    InterviewCreate, InterviewSchedule, InterviewResponse,
    InterviewDetailResponse, AnswerSubmit, AnswerFeedback
)
from ..services.interview_service import InterviewService
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


def get_auth_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Extract user from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from ..services.user_service import UserService
    return UserService.get_user_by_id(db, user_id)


@router.post("", response_model=InterviewResponse)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Create a new mock or real interview"""
    service = InterviewService()
    
    # Only candidates can create interviews
    if current_user.role.value != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can create interviews")
    
    # Candidates can only create mock interviews themselves
    if interview_data.interview_type == InterviewType.REAL:
        raise HTTPException(
            status_code=400,
            detail="Candidates cannot create real interviews. Interviewers schedule real interviews."
        )
    
    interview = service.create_interview(db, current_user.id, interview_data)
    return interview


@router.post("/schedule", response_model=InterviewResponse)
async def schedule_interview(
    interview_data: InterviewSchedule,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Interviewer schedules a real interview for a candidate"""
    service = InterviewService()
    
    # Only interviewers can schedule
    if current_user.role.value != "interviewer":
        raise HTTPException(status_code=403, detail="Only interviewers can schedule interviews")
    
    interview = service.schedule_interview(db, interview_data, current_user.id)
    return interview


@router.get("/{interview_id}", response_model=InterviewDetailResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Get interview details"""
    service = InterviewService()
    interview = service.get_interview(db, interview_id)
    
    # Verify access: candidate owns it or interviewer assigned to it
    if current_user.role.value == "candidate" and interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role.value == "interviewer" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return interview


@router.get("", response_model=List[InterviewResponse])
async def get_my_interviews(
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Get all interviews for current user"""
    service = InterviewService()
    interviews = service.get_user_interviews(db, current_user.id)
    return interviews


@router.post("/{interview_id}/start", response_model=InterviewResponse)
async def start_interview(
    interview_id: int,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Start taking interview"""
    service = InterviewService()
    interview = service.get_interview(db, interview_id)
    
    # Only candidate can start
    if interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return service.start_interview(db, interview_id)


@router.get("/{interview_id}/next-question")
async def get_next_question(
    interview_id: int,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Get next question for interview"""
    service = InterviewService()
    interview = service.get_interview(db, interview_id)
    
    # Only candidate can get questions
    if interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    next_question = service.get_next_question(db, interview_id)
    
    if not next_question:
        raise HTTPException(
            status_code=400,
            detail="Interview complete. Please submit your final answers."
        )
    
    return {"question": next_question}


@router.post("/{interview_id}/answer", response_model=AnswerFeedback)
async def submit_answer(
    interview_id: int,
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Submit answer and get AI feedback"""
    service = InterviewService()
    interview = service.get_interview(db, interview_id)
    
    # Only candidate can submit answers
    if interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return service.submit_answer(db, interview_id, answer_data.question_number, answer_data)


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
async def complete_interview(
    interview_id: int,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Complete interview and get final scores"""
    service = InterviewService()
    interview = service.get_interview(db, interview_id)
    
    # Only candidate can complete
    if interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return service.complete_interview(db, interview_id)
