"""
Simple AI Agent for Study Plan Generation.

Priority:
  1. Try OpenAI API (reads OPENAI_API_KEY from environment / .env file).
  2. If key is absent or call fails → fall back to a built-in rule-based mock
     so the app always works without any API key.
"""

import os

# Load .env file if python-dotenv is installed (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ─────────────────────────────────────────────────────────────────────────────
# Mock fallback – no API required
# ─────────────────────────────────────────────────────────────────────────────

def _mock_plan(subject: str, priority_score: float, study_hours: float, time_left: int, exam_marks: int = 100) -> str:
    """Generate a deterministic study plan without any API call."""
    urgency = "HIGH" if priority_score >= 65 else ("MEDIUM" if priority_score >= 35 else "LOW")
    marks_note = f" (out of {exam_marks} marks)" if exam_marks != 100 else ""

    if urgency == "HIGH":
        advice = (
            f"⚠️  This subject needs IMMEDIATE attention!\n\n"
            f"📅 Daily Plan ({time_left} days remaining{marks_note}):\n"
            f"  • Day 1–2  : Review fundamentals & identify weak areas\n"
            f"  • Day 3–{max(3, time_left-2)}: Deep practice — {study_hours:.1f} hrs/day focused sessions\n"
            f"  • Final day: Quick revision, past questions & rest\n\n"
            f"💡 Tips:\n"
            f"  – Break sessions into 50-min blocks with 10-min breaks (Pomodoro).\n"
            f"  – Prioritise understanding over memorisation.\n"
            f"  – Test yourself with practice problems every evening."
        )
    elif urgency == "MEDIUM":
        advice = (
            f"📘 Moderate focus needed for {subject}.\n\n"
            f"📅 Daily Plan ({time_left} days remaining{marks_note}):\n"
            f"  • Weekdays : {study_hours:.1f} hrs/day structured study\n"
            f"  • Weekends : Light revision + concept mapping\n"
            f"  • Last 2 days: Mock tests & weak-point reinforcement\n\n"
            f"💡 Tips:\n"
            f"  – Create a summary sheet after each session.\n"
            f"  – Discuss tough topics with peers or online communities."
        )
    else:
        advice = (
            f"✅ {subject} is well under control.\n\n"
            f"📅 Daily Plan ({time_left} days remaining{marks_note}):\n"
            f"  • Maintain {study_hours:.1f} hrs/day light review\n"
            f"  • Focus on edge cases and advanced topics\n"
            f"  • Final 2 days: Skim notes & stay relaxed\n\n"
            f"💡 Tips:\n"
            f"  – Use spaced repetition for long-term retention.\n"
            f"  – Teach the concept to someone else to solidify understanding."
        )

    return (
        f"Subject        : {subject}\n"
        f"Priority Score : {priority_score:.1f} / 100  [{urgency} priority]\n"
        f"Recommended    : {study_hours:.1f} hours/day\n"
        f"Time Left      : {time_left} day(s)\n"
        f"Exam Marks     : {exam_marks}\n\n"
        f"{advice}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI path
# ─────────────────────────────────────────────────────────────────────────────

def _openai_plan(subject: str, priority_score: float, study_hours: float, time_left: int, exam_marks: int = 100) -> str:
    """Call OpenAI ChatCompletion and return the generated plan text."""
    try:
        from openai import OpenAI          # openai >= 1.0.0
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = (
            f"You are a study planner. Based on the data below, generate a simple "
            f"daily study plan with hours and a short explanation (max 200 words).\n\n"
            f"Subject       : {subject}\n"
            f"Priority Score: {priority_score:.1f} / 100\n"
            f"Study Hours   : {study_hours:.1f} hours per day\n"
            f"Days Left     : {time_left}\n"
            f"Exam Marks    : {exam_marks}\n\n"
            f"Format:\n"
            f"- Day-by-day schedule\n"
            f"- Key study tips\n"
            f"- Final encouragement"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful, concise study planner AI."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        print(f"[Agent] OpenAI call failed ({exc}). Using mock plan.")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_study_plan(
    subject: str,
    priority_score: float,
    study_hours: float,
    time_left: int,
    exam_marks: int = 100,
) -> str:
    """
    Generate a study plan.
    Tries OpenAI first; if unavailable or key missing, uses the mock.
    """
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        plan = _openai_plan(subject, priority_score, study_hours, time_left, exam_marks)
        if plan:
            return plan

    # Fallback
    return _mock_plan(subject, priority_score, study_hours, time_left, exam_marks)


if __name__ == "__main__":
    plan = generate_study_plan("Mathematics", 78.5, 4.5, 7)
    print(plan)
