"""
Interview service for managing interviews
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from ..models.models import (
    Interview, Question, User, Domain, Role, 
    InterviewStatus, InterviewType
)
from ..schemas.schemas import (
    InterviewCreate, InterviewSchedule, InterviewResponse,
    InterviewDetailResponse, AnswerSubmit, AnswerFeedback
)
from ..ai_module.interviewer import AIInterviewer


class InterviewService:
    """Interview management service"""
    
    def __init__(self):
        self.ai = AIInterviewer()
    
    def create_interview(self, db: Session, candidate_id: int, interview_data: InterviewCreate) -> Interview:
        """Create a new interview (mock or real)"""
        # Validate domain and role exist
        domain = db.query(Domain).filter(Domain.id == interview_data.domain_id).first()
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        role = db.query(Role).filter(
            and_(Role.id == interview_data.role_id, Role.domain_id == interview_data.domain_id)
        ).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found for this domain")
        
        # For real interviews, validate interviewer and schedule
        interviewer_id = None
        scheduled_at = None
        
        if interview_data.interview_type == InterviewType.REAL:
            if not interview_data.interviewer_id:
                raise HTTPException(
                    status_code=400,
                    detail="Interviewer required for real interviews"
                )
            if not interview_data.scheduled_at:
                raise HTTPException(
                    status_code=400,
                    detail="Scheduled time required for real interviews"
                )
            interviewer_id = interview_data.interviewer_id
            scheduled_at = interview_data.scheduled_at
        
        # Create interview
        interview = Interview(
            candidate_id=candidate_id,
            interviewer_id=interviewer_id,
            domain_id=interview_data.domain_id,
            role_id=interview_data.role_id,
            interview_type=interview_data.interview_type,
            difficulty=interview_data.difficulty,
            scheduled_at=scheduled_at,
            status=InterviewStatus.SCHEDULED
        )
        
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        return interview

    def schedule_interview(self, db: Session, interview_data: InterviewSchedule, interviewer_id: int) -> Interview:
        """Schedule a real interview for a candidate"""
        # Validate candidate exists and is a candidate
        candidate = db.query(User).filter(User.id == interview_data.candidate_id).first()
        if not candidate or candidate.role.value != "candidate":
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Create real interview
        interview_create = InterviewCreate(
            domain_id=interview_data.domain_id,
            role_id=interview_data.role_id,
            interview_type=InterviewType.REAL,
            difficulty=interview_data.difficulty,
            scheduled_at=interview_data.scheduled_at,
            interviewer_id=interviewer_id
        )
        
        return self.create_interview(db, interview_data.candidate_id, interview_create)

    def get_interview(self, db: Session, interview_id: int) -> Interview:
        """Get interview by ID"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        return interview

    def get_user_interviews(self, db: Session, user_id: int) -> List[Interview]:
        """Get all interviews for a user (candidate or interviewer)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.role.value == "candidate":
            return db.query(Interview).filter(Interview.candidate_id == user_id).all()
        else:  # interviewer
            return db.query(Interview).filter(Interview.interviewer_id == user_id).all()

    def start_interview(self, db: Session, interview_id: int) -> Interview:
        """Mark interview as started"""
        interview = self.get_interview(db, interview_id)
        
        if interview.status != InterviewStatus.SCHEDULED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot start interview with status {interview.status}"
            )
        
        interview.status = InterviewStatus.IN_PROGRESS
        interview.started_at = datetime.utcnow()
        db.commit()
        db.refresh(interview)
        
        return interview

    def get_next_question(self, db: Session, interview_id: int) -> Optional[str]:
        """Get next question for interview (max 3 questions)"""
        interview = self.get_interview(db, interview_id)
        question_count = db.query(Question).filter(Question.interview_id == interview_id).count()
        
        if question_count >= 3:
            return None  # Interview complete
        
        # Generate next question
        weak_areas = [q.weak_area for q in interview.questions if q.weak_area]
        
        question_text = self.ai.generate_interview_question(
            domain=interview.domain.name,
            role=interview.role.name,
            difficulty=interview.difficulty,
            weak_areas=weak_areas if weak_areas else None
        )
        
        # Save question to database
        question = Question(
            interview_id=interview_id,
            question_number=question_count + 1,
            question_text=question_text
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        return question_text

    def submit_answer(
        self,
        db: Session,
        interview_id: int,
        question_number: int,
        answer_data: AnswerSubmit
    ) -> AnswerFeedback:
        """Submit answer and get AI feedback"""
        interview = self.get_interview(db, interview_id)
        
        # Get question
        question = db.query(Question).filter(
            and_(
                Question.interview_id == interview_id,
                Question.question_number == question_number
            )
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Save answer
        question.answer_text = answer_data.answer_text
        question.audio_file_path = answer_data.audio_file_path
        question.video_file_path = answer_data.video_file_path
        
        # Get AI feedback
        ai_feedback = self.ai.analyze_answer(question.question_text, answer_data.answer_text or "")
        
        # Extract weak area
        weak_area = self.ai.extract_weak_area(ai_feedback)
        
        # Score answer
        score = self.ai.score_answer(question.question_text, answer_data.answer_text or "", ai_feedback)
        
        # Update question
        question.ai_feedback = ai_feedback
        question.score = score
        question.is_correct = score >= 8
        question.weak_area = weak_area
        
        db.commit()
        db.refresh(question)
        
        return AnswerFeedback(
            question_id=question.id,
            question_number=question_number,
            ai_feedback=ai_feedback,
            score=score,
            is_correct=question.is_correct,
            weak_area=weak_area
        )

    def complete_interview(self, db: Session, interview_id: int) -> Interview:
        """Complete interview and calculate final scores"""
        interview = self.get_interview(db, interview_id)
        
        if interview.status != InterviewStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=400,
                detail="Interview is not in progress"
            )
        
        # Calculate overall score and accuracy
        questions = interview.questions
        if questions:
            overall_score = sum(q.score for q in questions) // len(questions)
            correct_count = sum(1 for q in questions if q.is_correct)
            accuracy = (correct_count / len(questions)) * 100
            
            interview.overall_score = overall_score
            interview.accuracy_percentage = int(accuracy)
            
            # Generate feedback summary
            weak_areas = [q.weak_area for q in questions if q.weak_area]
            interview.feedback_summary = f"Average Score: {overall_score}/10. Weak Areas: {', '.join(set(weak_areas)) if weak_areas else 'None identified'}"
        
        interview.status = InterviewStatus.COMPLETED
        interview.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(interview)
        
        return interview
