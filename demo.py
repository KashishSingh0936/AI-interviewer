from groq import Groq
import os

# ✅ DEFINE CLIENT FIRST
client = Groq(api_key="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")

def generate_topic(role, difficulty):
    prompt = f"""
    Generate ONE interview topic for {role} at {difficulty} level.

    Rules:
    - Only output the topic name
    - No explanation
    - Keep it very simple (1-3 words)
    - Choose different topics each time
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7  # Increased for more variety
    )

    return response.choices[0].message.content.strip()


# 🧱 STEP 2: Convert Topic → Question
def topic_to_question(topic):
    prompt = f"""
    Convert this topic into ONE simple interview question.

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
        temperature=0.7  # Increased for variety
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

    # length control - increased limit
    if len(q.split()) > 15:  # Increased from 20 to 15
        return False

    return True


# 🧠 MAIN FUNCTION
def generate_interview_question(role="Machine Learning Engineer", difficulty="Beginner"):
    for _ in range(3):  # retry max 3 times
        topic = generate_topic(role, difficulty)
        question = topic_to_question(topic)
        question = clean_question(question)

        if is_valid(question):
            return question

    return "Failed to generate a valid question."


# 🚀 RUN
if __name__ == "__main__":
    q = generate_interview_question()
    print("\nInterview Question:")
    print(q)