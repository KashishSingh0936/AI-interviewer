"""
🎯 SCORING ENGINE - Interview Performance Analysis
Handles scoring, analytics, and report generation for interview sessions.
"""

from datetime import datetime
import json

class ScoringEngine:
    """Tracks and calculates interview scores"""
    
    def __init__(self):
        self.question_scores = []
        self.feedback_log = []
        self.weak_areas = []
        self.strong_areas = []
        self.strict_mode_count = 0
        self.start_time = datetime.now()
    
    def add_answer_evaluation(self, question, answer, feedback, is_correct, weak_area=None, strict_mode=False):
        """
        Record an answer evaluation
        
        Args:
            question: The question asked
            answer: Candidate's response
            feedback: AI evaluation feedback
            is_correct: Boolean if answer was correct
            weak_area: Identified weak area (if any)
            strict_mode: Whether strict mode was active
        """
        # Strong base scoring, with room for improvement/bad outcomes
        score = 10 if is_correct else 4

        # Penalize weaknesses but avoid dropping to 0 immediately
        if weak_area and weak_area.lower() != "none":
            score -= 1

        # If feedback includes clear negative terms, penalize mildly
        if feedback:
            low_text = feedback.lower()
            if any(x in low_text for x in ["incorrect", "incomplete", "vague", "missing", "weak"]):
                score -= 1
            if "reason" in low_text and "good" not in low_text and "correct" not in low_text:
                score -= 1

        # Size-based answer quality check
        if answer:
            answer_length = len(answer.split())
            if answer_length < 5:
                score -= 2
            elif answer_length > 180:
                score -= 1

        # Strict mode should not excessively punish score, just note behavior
        if strict_mode:
            self.strict_mode_count += 1
            score -= 0  # stance remains firm but not too punitive

        # Ensure final score stays in acceptable range but avoid zero unless catastrophic
        score = max(1, min(10, score))

        # Ensure score stays in range
        score = max(0, min(10, score))
        
        # Ensure score stays in range
        score = max(0, min(10, score))
        
        strong_area = None
        if is_correct:
            strong_area = "correct understanding" if not (weak_area and weak_area.lower() != "none") else "partial correctness"
        elif feedback and any(x in feedback.lower() for x in ["good", "well done", "solid", "clearly", "accurate", "excellent"]):
            strong_area = "good communication"

        evaluation = {
            "question": question,
            "answer": answer,
            "feedback": feedback,
            "score": score,
            "is_correct": is_correct,
            "weak_area": weak_area,
            "strong_area": strong_area,
            "strict_mode": strict_mode
        }
        
        self.question_scores.append(evaluation)
        self.feedback_log.append(feedback)
        
        if weak_area and weak_area.lower() != "none":
            self.weak_areas.append(weak_area)
        if strong_area:
            self.strong_areas.append(strong_area)
        
        return score
    
    def get_overall_score(self):
        """Calculate overall interview score"""
        if not self.question_scores:
            return 0
        weighted_sum = sum(score["score"] for score in self.question_scores)
        return round(weighted_sum / len(self.question_scores), 2)
    
    def get_correct_count(self):
        """Get number of correct answers"""
        return sum(1 for score in self.question_scores if score["is_correct"])
    
    def get_accuracy_percentage(self):
        """Get accuracy as percentage"""
        if not self.question_scores:
            return 0
        correct = self.get_correct_count()
        total = len(self.question_scores)
        return round((correct / total) * 100, 1)
    
    def get_performance_grade(self):
        """Convert score to letter grade"""
        score = self.get_overall_score()
        if score >= 9:
            return "A+"
        elif score >= 8.5:
            return "A"
        elif score >= 8:
            return "A-"
        elif score >= 7.5:
            return "B+"
        elif score >= 7:
            return "B"
        elif score >= 6.5:
            return "B-"
        elif score >= 6:
            return "C+"
        elif score >= 5:
            return "C"
        else:
            return "D"


class PerformanceAnalyzer:
    """Analyzes interview performance and generates insights"""
    
    def __init__(self, scoring_engine):
        self.engine = scoring_engine
    
    def analyze_weak_areas(self):
        """Identify and summarize weak areas"""
        if not self.engine.weak_areas:
            return ["No specific weak areas identified. Good job!"]
        
        # Count occurrences
        area_count = {}
        for area in self.engine.weak_areas:
            area_count[area] = area_count.get(area, 0) + 1
        
        # Sort by frequency
        sorted_areas = sorted(area_count.items(), key=lambda x: x[1], reverse=True)
        return [f"{area}: {count} mention(s)" for area, count in sorted_areas]
    
    def analyze_strengths(self):
        """Identify strengths based on correct answers"""
        if self.engine.strong_areas:
            # return stated strong areas from scoring analysis (deduped)
            return list(dict.fromkeys(self.engine.strong_areas))

        correct_questions = [score["question"] for score in self.engine.question_scores if score["is_correct"]]
        
        if not correct_questions:
            return ["Continue working to identify strengths."]
        
        themes = {
            "conceptual understanding": 0,
            "problem-solving": 0,
            "communication": 0,
            "technical knowledge": 0
        }
        
        # Basic theme detection
        for q in correct_questions:
            q_lower = q.lower()
            if any(word in q_lower for word in ["what", "define", "explain", "concept"]):
                themes["conceptual understanding"] += 1
            elif any(word in q_lower for word in ["how", "solve", "approach", "design"]):
                themes["problem-solving"] += 1
            elif any(word in q_lower for word in ["describe", "discuss"]):
                themes["communication"] += 1
            else:
                themes["technical knowledge"] += 1
        
        strengths = [theme for theme, count in themes.items() if count > 0]
        return strengths if strengths else ["Technical proficiency"]
    
    def get_recommendations(self):
        """Generate improvement recommendations"""
        recommendations = []
        
        accuracy = self.engine.get_accuracy_percentage()
        
        if accuracy < 50:
            recommendations.append("⚠️  Focus on fundamentals - revisit core concepts in weak areas")
        elif accuracy < 70:
            recommendations.append("📚 Study weak areas more thoroughly before next attempt")
        else:
            recommendations.append("✅ Strong performance - practice advanced topics")
        
        if self.engine.strict_mode_count > 0:
            recommendations.append("🎯 Maintain professional and respectful communication in interviews")
        
        weak_areas = self.engine.weak_areas
        if weak_areas:
            top_weak = self.engine.weak_areas[0] if weak_areas else None
            if top_weak:
                recommendations.append(f"📖 Deep dive into '{top_weak}' to strengthen this area")
        
        if len(self.engine.question_scores) < 3:
            recommendations.append("🔄 Complete more practice interviews for consistent improvement")
        
        return recommendations


class ReportGenerator:
    """Generates interview reports"""
    
    def __init__(self, scoring_engine, domain, role, difficulty):
        self.engine = scoring_engine
        self.domain = domain
        self.role = role
        self.difficulty = difficulty
        self.analyzer = PerformanceAnalyzer(scoring_engine)
    
    def generate_summary_report(self):
        """Generate a summary report"""
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    INTERVIEW PERFORMANCE REPORT                  ║
╚══════════════════════════════════════════════════════════════════╝

📋 SESSION DETAILS
─────────────────────────────────────────────────────────────────
Domain:         {self.domain.title()}
Role:           {self.role.title()}
Difficulty:     {self.difficulty.title()}
Date:           {self.engine.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Total Questions: {len(self.engine.question_scores)}

📊 PERFORMANCE METRICS
─────────────────────────────────────────────────────────────────
Overall Score:  {self.engine.get_overall_score()}/10
Performance:    {self.engine.get_performance_grade()}
Accuracy:       {self.engine.get_accuracy_percentage()}% ({self.engine.get_correct_count()}/{len(self.engine.question_scores)} correct)

🎯 STRENGTHS
─────────────────────────────────────────────────────────────────
"""
        for i, strength in enumerate(self.analyzer.analyze_strengths(), 1):
            report += f"  {i}. {strength.title()}\n"
        
        report += f"""
⚠️  AREAS FOR IMPROVEMENT
─────────────────────────────────────────────────────────────────
"""
        weak_areas = self.analyzer.analyze_weak_areas()
        for i, area in enumerate(weak_areas, 1):
            report += f"  {i}. {area}\n"
        
        report += f"""
💡 RECOMMENDATIONS
─────────────────────────────────────────────────────────────────
"""
        for i, rec in enumerate(self.analyzer.get_recommendations(), 1):
            report += f"  {i}. {rec}\n"
        
        if self.engine.strict_mode_count > 0:
            report += f"""
🚨 BEHAVIORAL NOTES
─────────────────────────────────────────────────────────────────
  ⚠️  Strict mode was activated {self.engine.strict_mode_count} time(s)
  This indicates unprofessional conduct. Maintain professionalism in interviews.

"""
        
        report += """
═════════════════════════════════════════════════════════════════════
           Thank you for practicing with AI Interviewer!
═════════════════════════════════════════════════════════════════════
"""
        return report
    
    def generate_detailed_report(self):
        """Generate detailed Q&A report"""
        report = "\n📝 DETAILED QUESTION-ANSWER REVIEW\n"
        report += "═" * 70 + "\n\n"
        
        for i, score in enumerate(self.engine.question_scores, 1):
            report += f"Question {i}: {score['question']}\n"
            report += f"Your Answer: {score['answer']}\n"
            report += f"Score: {score['score']}/10 | "
            report += f"Status: {'✅ Correct' if score['is_correct'] else '❌ Incorrect'}\n"
            report += f"Feedback: {score['feedback']}\n"
            
            if score['weak_area']:
                report += f"⚠️  Weak Area: {score['weak_area']}\n"
            
            if score['strict_mode']:
                report += "🚨 Strict Mode Active\n"
            
            report += "─" * 70 + "\n\n"
        
        return report
    
    def export_to_json(self, filename="interview_report.json"):
        """Export report data to JSON"""
        report_data = {
            "metadata": {
                "domain": self.domain,
                "role": self.role,
                "difficulty": self.difficulty,
                "timestamp": self.engine.start_time.isoformat()
            },
            "performance": {
                "overall_score": self.engine.get_overall_score(),
                "grade": self.engine.get_performance_grade(),
                "accuracy": self.engine.get_accuracy_percentage(),
                "correct_count": self.engine.get_correct_count(),
                "total_questions": len(self.engine.question_scores)
            },
            "analysis": {
                "strengths": self.analyzer.analyze_strengths(),
                "weak_areas": self.analyzer.analyze_weak_areas(),
                "recommendations": self.analyzer.get_recommendations()
            },
            "questions": self.engine.question_scores,
            "strict_mode_activations": self.engine.strict_mode_count
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return filename
