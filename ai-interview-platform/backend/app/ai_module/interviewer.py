"""
AI Interviewer Module - Integrated from existing interview system
Handles question generation, answer analysis, and scoring
"""
from groq import Groq
from typing import Optional, Tuple
import os
from ..core.config import settings


class AIInterviewer:
    """AI Interviewer using Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.1-8b-instant"
    
    # ============= QUESTION GENERATION =============
    
    def generate_topic(self, domain: str, role: str, difficulty: str, weak_areas: Optional[list] = None) -> str:
        """Generate a relevant interview topic"""
        weak_text = f"Weak areas to focus on: {', '.join(weak_areas)}" if weak_areas else ""
        
        prompt = f"""
        Generate ONE interview topic.

        Domain: {domain}
        Role: {role}
        Difficulty: {difficulty}
        {weak_text}

        Rules:
        - Only output the topic name
        - No explanation
        - Keep it very simple (1-3 words)
        - Must be relevant to the domain and role
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    def topic_to_question(self, topic: str, role: str) -> str:
        """Convert a topic into an interview question"""
        prompt = f"""
        Convert this topic into ONE simple interview question.

        Role: {role}
        Topic: {topic}

        Rules:
        - Only ONE question
        - No bullet points
        - No explanation
        - Max 12 words
        - Ask only ONE thing
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    def clean_question(self, question: str) -> str:
        """Clean question output"""
        question = question.replace("*", "").replace("-", "")
        question = question.split("\n")[0]
        
        if "?" in question:
            question = question.split("?")[0] + "?"
        
        return question.strip()

    def is_valid_question(self, question: str) -> bool:
        """Validate question format"""
        if question.count("?") != 1:
            return False
        if len(question.split()) > 20:
            return False
        return True

    def generate_interview_question(self, domain: str, role: str, difficulty: str, weak_areas: Optional[list] = None) -> str:
        """Generate a complete valid interview question"""
        for _ in range(3):  # Try up to 3 times
            topic = self.generate_topic(domain, role, difficulty, weak_areas)
            question = self.topic_to_question(topic, role)
            question = self.clean_question(question)
            
            if self.is_valid_question(question):
                return question
        
        return "Failed to generate a valid question."

    # ============= ANSWER ANALYSIS =============

    def analyze_answer(self, question: str, answer: str) -> str:
        """Analyze a candidate's answer and provide feedback"""
        prompt = f"""
        You are a STRICT technical interviewer evaluating a candidate's answer. Be critical and honest.

        Question: {question}
        Answer: {answer}

        Evaluation criteria:
        - CORRECT: Answer directly addresses the question with accurate technical details
        - INCOMPLETE: Missing critical points or lacks depth
        - INCORRECT: Wrong approach or fundamentally flawed understanding
        - VAGUE: Too generic, lacks specific examples or implementation details

        Task:
        - Determine if answer is CORRECT or NOT (Yes/No)
        - Be harsh - mediocre answers should be marked as No
        - Only mark Yes if answer demonstrates solid understanding
        - Identify specific weak areas for incorrect answers

        Output format:
        Correct: Yes/No
        Reason: <brief explanation of why>
        Weak Area: <specific skill gap or None if correct>
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    def extract_weak_area(self, feedback: str) -> Optional[str]:
        """Extract weak area from AI feedback - robust extraction"""
        if not feedback:
            return None
        
        # Strategy 1: Direct format matching
        lines = feedback.split("\n")
        for line in lines:
            line_clean = line.strip()
            if any(key in line_clean for key in ["Weak Area:", "Weak area:", "Weakness:", "weakness:"]):
                weak_part = line_clean.split(":", 1)[-1].strip()
                if weak_part and weak_part.lower() not in ["none", "n/a", "no", "none."]:
                    return weak_part
        
        # Strategy 2: Pattern matching
        feedback_lower = feedback.lower()
        
        weakness_patterns = {
            "missing": "Missing key concepts",
            "incomplete": "Incomplete understanding",
            "vague": "Lack of specific examples",
            "oversimplified": "Oversimplified explanation",
            "inaccurate": "Fundamental misunderstanding",
            "wrong approach": "Incorrect approach",
            "unclear": "Poor communication",
            "superficial": "Lack of depth",
        }
        
        for pattern, weakness_label in weakness_patterns.items():
            if pattern in feedback_lower:
                return weakness_label
        
        # Strategy 3: Context inference
        if "incorrect" in feedback_lower and "correct: no" in feedback_lower:
            if "reason:" in feedback_lower:
                reason_section = feedback_lower.split("reason:")[-1]
                if "not" in reason_section or "doesn't" in reason_section or "failed" in reason_section:
                    return "Conceptual gap or knowledge deficiency"
        
        return None

    def score_answer(self, question: str, answer: str, ai_feedback: str) -> int:
        """
        Calculate deterministic score (0-10) for answer
        Based on correctness, depth, and relevance
        """
        if not ai_feedback:
            return 0
        
        feedback_lower = ai_feedback.lower()
        
        # Determine correctness
        is_correct = False
        if "correct: yes" in feedback_lower:
            is_correct = True
        elif "correct: no" in feedback_lower:
            is_correct = False
        elif "correct: yes" in feedback_lower or (
            "correct" in feedback_lower and "yes" in feedback_lower and "incorrect" not in feedback_lower
        ):
            is_correct = True
        
        score = 0
        
        if is_correct:
            score = 8
            answer_length = len(answer.split()) if answer else 0
            
            if answer_length >= 50:
                score = 10  # Correct with good depth
            elif answer_length >= 20:
                score = 9   # Correct with reasonable depth
            # else score stays at 8
        
        else:
            # Incorrect answers
            if any(word in feedback_lower for word in ["completely wrong", "fundamental", "misunderstand", "no understanding"]):
                score = 1
            elif "incomplete" in feedback_lower:
                score = 4
            elif "vague" in feedback_lower or "generic" in feedback_lower:
                score = 3
            else:
                score = 2
        
        # Penalty for suspiciously short answers
        if answer:
            word_count = len(answer.split())
            if word_count < 3:
                score = max(0, score - 2)
        
        return max(0, min(10, score))

    def detect_bad_behavior(self, answer: str) -> bool:
        """Detect unprofessional or disrespectful behavior"""
        bad_indicators = [
            "i don't care", "stupid", "dumb", "idiot", "joke", "waste of time",
            "f***", "shut up", "rude", "disrespect", "i'm leaving", "this sucks",
            "you're wrong", "you're biased", "i know better", "nonsense",
            "refusal", "i refuse", "won't answer", "not answering"
        ]
        answer_lower = answer.lower()
        for indicator in bad_indicators:
            if indicator in answer_lower:
                return True
        return False

    def generate_interviewer_response(
        self,
        question: str,
        answer: str,
        ai_feedback: str,
        domain: str,
        role: str,
        strict_mode: bool = False
    ) -> str:
        """Generate professional interviewer response"""
        
        if strict_mode:
            prompt = f"""
            You are a professional technical interviewer. The candidate has shown unprofessional behavior.

            Response Mode: STRICT - Address the conduct issue directly and professionally.

            Task:
            - Acknowledge the unprofessional conduct clearly
            - State that professional behavior is required
            - Give ONE clear warning
            - Be firm but not angry
            - Transition to next question

            Output Requirements:
            - Exactly 2-3 sentences. NO bullet points.
            - End with: "Let's move to the next question."

            Example: "I need to address the tone in that response. In technical interviews, we maintain professional communication at all times. Let's move to the next question."
            """
        else:
            prompt = f"""
            You are a PROFESSIONAL technical interviewer for a {role} role in {domain}.

            Your task:
            - Provide brief, objective feedback on the candidate's answer
            - If correct: congratulate and move forward
            - If incorrect: identify one specific gap
            - Always maintain respect and professionalism
            - Transition to next question

            Previous Question: {question}
            Candidate Answer: {answer}
            AI Feedback: {ai_feedback}

            Output Requirements:
            - Exactly 2-3 sentences. NO bullet points.
            - End with: "Let's proceed to the next question."
            - Tone: Professional, objective, encouraging but honest.
            """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5 if strict_mode else 0.6
        )

        return response.choices[0].message.content.strip()
