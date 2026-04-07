from transformers import pipeline
import re

# =========================
# INITIALIZE MODEL
# =========================
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

# =========================
# CONTEXT
# =========================
context = {
    "previous_questions": [],
    "weak_areas": [],
    "strengths": []
}

# =========================
# FORMAT CONTEXT
# =========================
def format_context(context):
    return f"""
Previous Questions: {context['previous_questions']}
Weak Areas: {context['weak_areas']}
Strengths: {context['strengths']}
"""

# =========================
# CLEAN GENERATED TEXT
# =========================
def extract_first_question(text):
    # Look for the first sentence ending with ?
    sentences = re.split(r'(?<=\?)', text)
    for s in sentences:
        s = s.strip()
        if s.endswith("?"):
            return s
    # Fallback: if no ?, just return first line
    return text.split("\n")[0].strip()

# =========================
# QUESTION GENERATOR
# =========================
def generate_question(role, level, context_text):
    prompt = f"""
You are an interviewer not an interviewee/candidate.

Role: {role}
Difficulty: {level}

Context:
{context_text}

Task:
Ask ONE relevant, concise interview question.
Do NOT repeat previous questions.
"""
    result = generator(
        prompt,
        max_length=128,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    raw_text = result[0]['generated_text'].strip()
    return extract_first_question(raw_text)

# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":
    role = "Machine Learning Engineer"
    level = "Beginner"

    context_text = format_context(context)
    question = generate_question(role, level, context_text)

    print("\nAI Question:\n", question)

    # Save question to context
    context["previous_questions"].append(question)