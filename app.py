"""
Flask backend for Intelligent Study Planner.

Routes:
  GET  /              → homepage (index.html)
  POST /generate-plan → fuzzy logic + agent → save to DB → return JSON
  GET  /plans         → fetch all saved plans (JSON)
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import traceback

from database   import init_db, get_or_create_user, save_subject, save_study_plan, fetch_all_plans, delete_study_plan
from fuzzy_logic import get_fuzzy_output
from agent       import generate_study_plan

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    try:
        data = request.get_json(force=True)

        # ── Validate required fields ──────────────────────────────────────────
        required = ["username", "subject", "difficulty", "time_left", "preparation"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        username    = str(data["username"]).strip() or "Guest"
        subject     = str(data["subject"]).strip()
        difficulty  = float(data["difficulty"])
        time_left   = int(data["time_left"])
        preparation = float(data["preparation"])
        exam_marks  = int(data.get("exam_marks", 100))   # optional, default 100

        # ── Fuzzy Logic ───────────────────────────────────────────────────────
        fuzzy_result = get_fuzzy_output(
            difficulty_val  = difficulty,
            time_left_val   = time_left,
            preparation_val = preparation,
        )
        priority_score = fuzzy_result["priority_score"]
        study_hours    = fuzzy_result["study_hours"]

        # ── AI Agent ──────────────────────────────────────────────────────────
        plan_text = generate_study_plan(
            subject        = subject,
            priority_score = priority_score,
            study_hours    = study_hours,
            time_left      = time_left,
            exam_marks     = exam_marks,
        )

        # ── Persist to DB ─────────────────────────────────────────────────────
        user_id = get_or_create_user(username)
        save_subject(user_id, subject, difficulty)
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_study_plan(user_id, subject, priority_score, study_hours, plan_text, today)

        return jsonify({
            "success":        True,
            "subject":        subject,
            "priority_score": priority_score,
            "study_hours":    study_hours,
            "exam_marks":     exam_marks,
            "plan":           plan_text,
            "date":           today,
        })

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Internal server error. Check console for details."}), 500


@app.route("/plans", methods=["GET"])
def get_plans():
    try:
        plans = fetch_all_plans()
        return jsonify({"success": True, "plans": plans})
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Could not fetch plans."}), 500


@app.route("/plans/<int:plan_id>", methods=["DELETE"])
def delete_plan(plan_id):
    try:
        delete_study_plan(plan_id)
        return jsonify({"success": True})
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Could not delete plan."}), 500


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\n[OK] Study Planner running at --> http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
