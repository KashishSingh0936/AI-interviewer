from groq import Groq
import os
from scoringEngine import ScoringEngine, ReportGenerator

# Voice I/O support
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# Video support
try:
    import cv2
except ImportError:
    cv2 = None

import threading
import time

# ✅ DEFINE CLIENT (Use environment variable for API key)
client = Groq(api_key=os.getenv("GROQ_API_KEY", "Hard-Code your api key here"))

# 🗂️ DOMAIN-ROLE MAPPING
domain_roles = {
    "data science": ["data scientist", "data analyst", "machine learning engineer"],
    "web development": ["frontend developer", "backend developer", "full stack developer"],
    "machine learning": ["ml engineer", "ai researcher", "data scientist"],
    "software engineering": ["software engineer", "devops engineer", "backend developer"],
    "cybersecurity": ["security analyst", "penetration tester", "security engineer"],
    "cloud computing": ["cloud architect", "devops engineer", "cloud engineer"],
    "mobile development": ["android developer", "ios developer", "mobile app developer"],
    "game development": ["game developer", "unity developer", "unreal engine developer"],
    "blockchain": ["blockchain developer", "smart contract developer", "crypto analyst"],
    "ai": ["ai engineer", "nlp specialist", "computer vision engineer"]
}

# 💬 Voice helpers

def speak_text(text):
    if pyttsx3 is None:
        print(f"[TTS missing] {text}")
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS error] {e}. Falling back to text output: {text}")


def capture_video(question_index, duration=300):
    """Capture video from webcam during interview answer"""
    if cv2 is None:
        return None
    
    video_file = f"answer_video_{question_index + 1}.avi"
    cap = cv2.VideoCapture(0)  # 0 = default camera
    
    if not cap.isOpened():
        print("[Camera error] Unable to access webcam. Proceeding without video.")
        return None
    
    fps = 20.0
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_file, fourcc, fps, (frame_width, frame_height))
    
    start_time = time.time()
    print("[Camera] Recording... Please look at the camera while answering.")
    
    try:
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Add timer overlay
            elapsed = int(time.time() - start_time)
            cv2.putText(frame, f"Recording: {elapsed}s", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            out.write(frame)
            cv2.imshow(f"Interview - Question {question_index + 1}", frame)
            
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
    
    return video_file


def listen_answer(question_index):
    if sr is None:
        print("[SpeechRecognition missing] using text input mode.")
        return input("Your Answer (text mode): ")

    r = sr.Recognizer()
    
    # Configure silence detection
    r.pause_threshold = 2.0  # 2 seconds of silence = end of answer
    r.non_speaking_duration = 0.3  # ignore short noise bursts
    r.dynamic_energy_threshold = True  # auto-adjust to mic levels
    
    # Start video recording in background
    video_thread = None
    if cv2 is not None:
        video_thread = threading.Thread(target=capture_video, args=(question_index, 300), daemon=True)
        video_thread.start()
    
    try:
        with sr.Microphone() as source:
            print("Listening... Speak clearly. 2 seconds of silence will end recording.")
            speak_text("Please answer now. When you pause for 2 seconds, I will stop recording.")
            audio = r.listen(source, timeout=300, phrase_time_limit=300)
    except sr.RequestError:
        print("Timeout: No speech detected for too long.")
        return input("Your Answer (text mode): ")
    except Exception as e:
        print(f"[Mic error] {e}. Please type your answer manually.")
        return input("Your Answer (text mode): ")

    try:
        text = r.recognize_google(audio)
        print(f"Captured: {text}")
        # save audio for later review
        filename = f"answer_{question_index + 1}.wav"
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())
        return text

    except sr.UnknownValueError:
        print("Could not understand audio. Please type your answer instead.")
        return input("Your Answer (fallback text mode): ")
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return input("Your Answer (fallback text mode): ")


# 🧱 STEP 1: Generate Topic (DOMAIN AWARE)
def generate_topic(domain, role, difficulty, weak_areas=None):
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
    - Choose different topics each time
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# 🧱 STEP 2: Convert Topic → Question
def topic_to_question(topic, role):
    prompt = f"""
    Convert this topic into ONE simple interview question.

    Role: {role}
    Topic: {topic}

    Rules:
    - Only ONE question
    - No bullet points
    - No explanation
    - Max 12 words total
    - Ask only ONE thing
    - Keep it very simple
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# 🧱 STEP 3: Clean Output
def clean_question(q):
    q = q.replace("*", "").replace("-", "")

    # take only first line
    q = q.split("\n")[0]

    # cut after first question mark
    if "?" in q:
        q = q.split("?")[0] + "?"

    return q.strip()

# 🧱 STEP 4: Validate Output
def is_valid(q):
    # must contain exactly one question mark
    if q.count("?") != 1:
        return False

    # length control (relaxed to 20 words)
    if len(q.split()) > 20:
        return False

    return True

# 🧱 STEP 5: Analyze Answer (LLM-based feedback)
def analyze_answer(question: str, answer: str) -> str:
    """
    Generate AI feedback on a candidate's answer.
    
    Args:
        question: The interview question asked
        answer: The candidate's response
        
    Returns:
        AI-generated feedback string
    """
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

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 IMPROVED SCORING, WEAK AREA, AND RESPONSE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def extract_weak_area(feedback: str) -> str | None:
    """
    Extract weak area from AI feedback with multiple robust strategies.
    
    Handles variations in AI response format:
    - "Weak Area: X" format
    - "Weak area: X" format
    - "Weakness: X" format
    - Implicit weak areas from reason text
    
    Args:
        feedback: AI feedback string (multi-line)
        
    Returns:
        Extracted weak area string or None if no weakness identified
    """
    if not feedback:
        return None
    
    # Strategy 1: Look for explicit "Weak Area:" or "Weak area:" or variations
    lines = feedback.split("\n")
    for line in lines:
        line_clean = line.strip()
        
        # Check for weak area keywords
        if any(key in line_clean for key in ["Weak Area:", "Weak area:", "Weakness:", "weakness:"]):
            # Extract everything after the colon
            weak_part = line_clean.split(":", 1)[-1].strip()
            # Filter out "None" or empty responses
            if weak_part and weak_part.lower() not in ["none", "n/a", "no", "none."]:
                return weak_part
    
    # Strategy 2: If answer is clearly marked as incorrect, extract from reasons
    feedback_lower = feedback.lower()
    
    # Look for common weakness indicators in the reason
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
    
    # Strategy 3: If clearly incorrect, infer weakness from feedback context
    if "incorrect" in feedback_lower and "correct: no" in feedback_lower:
        # Find what was wrong from the reason section
        if "reason:" in feedback_lower:
            reason_section = feedback_lower.split("reason:")[-1]
            if "not" in reason_section or "doesn't" in reason_section or "failed" in reason_section:
                return "Conceptual gap or knowledge deficiency"
    
    return None


def score_answer(question: str, answer: str, ai_feedback: str) -> int:
    """
    Calculate a deterministic score (0-10) based on correctness, depth, and relevance.
    
    Scoring logic:
    - Base: 0 by default (failures must be earned upward)
    - Correct + Depth: 9-10
    - Correct + Shallow: 7-8
    - Incomplete: 5-6
    - Vague/Wrong: 2-4
    - Completely Wrong: 0-1
    
    Args:
        question: The interview question
        answer: The candidate's response
        ai_feedback: AI evaluation feedback
        
    Returns:
        Score as integer from 0 to 10
    """
    if not ai_feedback:
        return 0
    
    feedback_lower = ai_feedback.lower()
    
    # Determine correctness verdict
    is_correct = False
    if "correct: yes" in feedback_lower:
        is_correct = True
    elif "correct: no" in feedback_lower:
        is_correct = False
    elif "correct: yes" in feedback_lower or (
        "correct" in feedback_lower and "yes" in feedback_lower and "incorrect" not in feedback_lower
    ):
        is_correct = True
    
    # Base score depends on correctness
    score = 0
    
    if is_correct:
        # CORRECT ANSWERS: Start at 8, can go to 10
        score = 8
        
        # Add depth assessment
        answer_length = len(answer.split()) if answer else 0
        if answer_length >= 50:  # Substantial answer
            score = 10  # Correct with good depth
        elif answer_length >= 20:  # Decent length
            score = 9  # Correct with reasonable depth
        # else score stays at 8 (correct but brief)
        
    else:
        # INCORRECT ANSWERS: Start lower
        
        # Check if it's completely wrong or partially correct
        if any(word in feedback_lower for word in ["completely wrong", "fundamental", "misunderstand", "no understanding"]):
            score = 1  # Completely incorrect
        
        elif "incomplete" in feedback_lower:
            # Missing some pieces but has some correct elements
            score = 4
        
        elif "vague" in feedback_lower or "generic" in feedback_lower:
            # Right direction but lacks specificity
            score = 3
        
        else:
            # Other incorrect cases
            score = 2
    
    # Answer length penalty (only if answer is suspiciously short)
    if answer:
        word_count = len(answer.split())
        if word_count < 3:  # Slap on wrist for one-liners
            score = max(0, score - 2)
    
    # Sanity check: ensure score is in valid range
    score = max(0, min(10, score))
    
    return score


def generate_interviewer_response(
    question: str,
    answer: str,
    ai_feedback: str,
    domain: str,
    role: str,
    strict_mode: bool = False
) -> str:
    """
    Generate a professional, concise interviewer response.
    
    Behavior:
    - Strict mode: Firm, professional warning about conduct
    - Normal mode: Constructive, objective feedback
    - Always professional, never rude
    - Always transitions to next question
    
    Args:
        question: The question asked
        answer: Candidate's response
        ai_feedback: AI feedback on the answer
        domain: Interview domain (e.g., "data science")
        role: Position role (e.g., "data scientist")
        strict_mode: If True, use firm/warning tone for conduct issues
        
    Returns:
        Interviewer response string (2-4 sentences, firm but professional)
    """
    
    if strict_mode:
        # STRICT MODE: Address behavior directly
        prompt = f"""
        You are a professional technical interviewer. The candidate has shown unprofessional or disrespectful behavior.

        Response Mode: STRICT - Address the conduct issue directly and professionally.

        Task:
        - Acknowledge the unprofessional conduct clearly
        - State that professional behavior is required going forward
        - Give ONE clear warning about expectations
        - Transition to the next question
        - Be firm but not angry; serious and no-nonsense

        Output Requirements:
        - Exactly 2-3 sentences. NO bullet points.
        - Be direct and clear about expectations.
        - End with: "Let's move to the next question."
        - Do NOT sugarcoat or apologize yourself.
        - Maintain respect but demand professionalism.

        Example: "I need to address the tone in that response. In technical interviews, we maintain professional and respectful communication at all times. Your next response should reflect that. Let's move to the next question."
        """
    else:
        # NORMAL MODE: Constructive feedback
        prompt = f"""
        You are a PROFESSIONAL technical interviewer for a {role} role in {domain}.

        Your task:
        - Provide brief, objective feedback on the candidate's answer
        - If correct: congratulate and move forward
        - If incorrect: identify one specific gap and encourage improvement
        - Always maintain respect and professionalism
        - Transition to next question

        Previous Question: {question}
        Candidate Answer: {answer}
        AI Feedback: {ai_feedback}

        Output Requirements:
        - Exactly 2-3 sentences. NO bullet points or lists.
        - Be concise and direct.
        - End with: "Let's proceed to the next question."
        - Tone: Professional, objective, encouraging but honest.

        Example: "Thank you for that answer. That's the correct approach. Let's proceed to the next question."
        """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5 if strict_mode else 0.6
    )

    return response.choices[0].message.content.strip()

# 🚨 STEP 6.5: Detect Bad Behavior (STRICT MODE)
def detect_bad_behavior(answer):
    """Detects rude, disrespectful, or unethical behavior"""
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



# 🧠 MAIN FUNCTION
def generate_interview_question(domain, role, difficulty, weak_areas):
    for _ in range(3):
        topic = generate_topic(domain, role, difficulty, weak_areas)
        question = topic_to_question(topic, role)
        question = clean_question(question)

        if is_valid(question):
            return question

    return "Failed to generate a valid question."

# 🚀 INTERACTIVE FLOW
if __name__ == "__main__":
    print("=== AI INTERVIEWER ===\n")

    domain = input("Enter Domain (e.g., data science, web development): ").lower()
    role = input("Enter Role (e.g., data scientist, frontend developer): ").lower()
    difficulty = input("Enter Difficulty (Beginner / Intermediate / Advanced): ")

    voice_mode = input("Enable voice mode? (y/n): ").strip().lower() in ["y", "yes"]
    if voice_mode and pyttsx3 is None:
        print("[Warning] pyttsx3 is not installed. Voice output disabled.")
        voice_mode = False

    if voice_mode:
        speak_text("Voice mode enabled. Starting your spoken interview.")

    print("\n--- Interview Started ---\n")

    conversation_history = []
    weak_areas = []
    strict_mode = False
    bad_behavior_count = 0
    
    # Initialize scoring engine
    scoring_engine = ScoringEngine()

    for i in range(3):
        q = generate_interview_question(domain, role, difficulty, weak_areas)

        if voice_mode:
            speak_text(f"Question {i+1}: {q}")
            print(f"Q{i+1}: {q}")
            answer = listen_answer(i)
        else:
            print(f"Q{i+1}: {q}")
            answer = input("Your Answer: ")

        # check if they want to repeat the question
        if any(phrase in answer.lower() for phrase in ["repeat", "hear", "again", "didn't hear", "couldn't hear", "say again"]):
            follow_up = "No worries, I'll repeat the question for you."
            print(follow_up)
            if voice_mode:
                speak_text(follow_up)
                speak_text(f"Question {i+1}: {q}")
            print(f"Q{i+1}: {q}")
            answer = listen_answer(i) if voice_mode else input("Your Answer: ")

        # 🚨 Check for bad behavior
        if detect_bad_behavior(answer):
            bad_behavior_count += 1
            if bad_behavior_count >= 1:
                strict_mode = True
                print("\n⚠️  STRICT MODE ACTIVATED - Professional conduct required\n")

        # store history
        conversation_history.append({
            "question": q,
            "answer": answer
        })

        # 📊 Evaluate answer and extract weak areas
        feedback = analyze_answer(q, answer)
        print("Feedback:", feedback)

        # 🧮 Extract weak area using robust method
        weak = extract_weak_area(feedback)
        if weak and weak.lower() != "none":
            weak_areas.append(weak)

        # 🎯 Calculate deterministic score
        answer_score = score_answer(q, answer, feedback)
        print(f"Answer Score: {answer_score}/10\n")

        # 📋 Record score with scoring engine
        scoring_engine.add_answer_evaluation(
            question=q,
            answer=answer,
            feedback=feedback,
            is_correct=answer_score >= 8,  # 8+ is considered correct
            weak_area=weak,
            strict_mode=strict_mode
        )


        # generate interviewer response for next question (if not last)
        if i < 2:
            interviewer_response = generate_interviewer_response(q, answer, feedback, domain, role, strict_mode=strict_mode)
            if voice_mode:
                speak_text(interviewer_response)
            print(f"Interviewer: {interviewer_response}\n")
        else:
            if strict_mode:
                print("\n⚠️  Interview concluded. Professional behavior will be noted in feedback.\n")
                if voice_mode:
                    speak_text("Interview concluded. Please maintain professional behavior next time.")
            else:
                print("Interview complete!\n")
                if voice_mode:
                    speak_text("Interview complete. Great job.")

            # Generate and display report
            reporter = ReportGenerator(scoring_engine, domain, role, difficulty)
            summary_report = reporter.generate_summary_report()
            detailed_report = reporter.generate_detailed_report()

            print(summary_report)
            print(detailed_report)

            # Export to JSON
            json_file = reporter.export_to_json()
            print(f"📄 Report exported to: {json_file}")    
