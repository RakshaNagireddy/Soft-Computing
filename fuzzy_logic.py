"""
Fuzzy Logic Engine using scikit-fuzzy.

Inputs:
  - difficulty    : 1–10  (easy / medium / hard)
  - time_left     : 1–30  (low / medium / high)
  - preparation   : 1–10  (poor / average / good)

Outputs:
  - priority_score : 0–100
  - study_hours    : 0–10  (hours per day recommended)
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def build_fuzzy_system():
    # ── Antecedents ──────────────────────────────────────────────────────────
    difficulty  = ctrl.Antecedent(np.arange(1, 11, 1), "difficulty")
    time_left   = ctrl.Antecedent(np.arange(1, 31, 1), "time_left")
    preparation = ctrl.Antecedent(np.arange(1, 11, 1), "preparation")

    # ── Consequents ──────────────────────────────────────────────────────────
    priority    = ctrl.Consequent(np.arange(0, 101, 1), "priority")
    study_hours = ctrl.Consequent(np.arange(0, 10.1, 0.1), "study_hours")

    # ── Membership Functions: Difficulty ─────────────────────────────────────
    difficulty["easy"]   = fuzz.trimf(difficulty.universe, [1, 1, 5])
    difficulty["medium"] = fuzz.trimf(difficulty.universe, [3, 5, 8])
    difficulty["hard"]   = fuzz.trimf(difficulty.universe, [6, 10, 10])

    # ── Membership Functions: Time Left (days) ───────────────────────────────
    time_left["low"]    = fuzz.trimf(time_left.universe, [1, 1, 10])
    time_left["medium"] = fuzz.trimf(time_left.universe, [5, 15, 25])
    time_left["high"]   = fuzz.trimf(time_left.universe, [20, 30, 30])

    # ── Membership Functions: Preparation ────────────────────────────────────
    preparation["poor"]    = fuzz.trimf(preparation.universe, [1, 1, 4])
    preparation["average"] = fuzz.trimf(preparation.universe, [3, 5, 8])
    preparation["good"]    = fuzz.trimf(preparation.universe, [6, 10, 10])

    # ── Membership Functions: Priority Score ─────────────────────────────────
    priority["low"]    = fuzz.trimf(priority.universe, [0, 0, 40])
    priority["medium"] = fuzz.trimf(priority.universe, [30, 50, 70])
    priority["high"]   = fuzz.trimf(priority.universe, [60, 100, 100])

    # ── Membership Functions: Study Hours / Day ───────────────────────────────
    study_hours["low"]    = fuzz.trimf(study_hours.universe, [0, 0, 4])
    study_hours["medium"] = fuzz.trimf(study_hours.universe, [2, 5, 7])
    study_hours["high"]   = fuzz.trimf(study_hours.universe, [5, 10, 10])

    # ── Rules (10 rules) ─────────────────────────────────────────────────────
    rules = [
        # Rule 1: hard subject + low time  → highest priority & max hours
        ctrl.Rule(difficulty["hard"]   & time_left["low"],                 [priority["high"],  study_hours["high"]]),

        # Rule 2: hard subject + poor prep → high priority
        ctrl.Rule(difficulty["hard"]   & preparation["poor"],              [priority["high"],  study_hours["high"]]),

        # Rule 3: medium difficulty + low time → medium-high priority
        ctrl.Rule(difficulty["medium"] & time_left["low"],                 [priority["high"],  study_hours["medium"]]),

        # Rule 4: easy subject + high time → low priority
        ctrl.Rule(difficulty["easy"]   & time_left["high"],                [priority["low"],   study_hours["low"]]),

        # Rule 5: good preparation → lower priority regardless
        ctrl.Rule(preparation["good"],                                     [priority["low"],   study_hours["low"]]),

        # Rule 6: poor preparation + hard subject → high priority
        ctrl.Rule(preparation["poor"]  & difficulty["hard"],               [priority["high"],  study_hours["high"]]),

        # Rule 7: medium difficulty + average prep + medium time → medium
        ctrl.Rule(difficulty["medium"] & preparation["average"] & time_left["medium"],
                                                                           [priority["medium"], study_hours["medium"]]),

        # Rule 8: easy + low time → medium priority
        ctrl.Rule(difficulty["easy"]   & time_left["low"],                 [priority["medium"], study_hours["medium"]]),

        # Rule 9: hard + high time + good prep → medium priority
        ctrl.Rule(difficulty["hard"]   & time_left["high"] & preparation["good"],
                                                                           [priority["medium"], study_hours["medium"]]),

        # Rule 10: poor prep + low time → max urgency
        ctrl.Rule(preparation["poor"]  & time_left["low"],                 [priority["high"],  study_hours["high"]]),
    ]

    system     = ctrl.ControlSystem(rules)
    simulation = ctrl.ControlSystemSimulation(system)
    return simulation


# Cache the fuzzy system at module level (build once, reuse)
_fuzzy_sim = None


def get_fuzzy_output(difficulty_val: float, time_left_val: float, preparation_val: float) -> dict:
    global _fuzzy_sim
    if _fuzzy_sim is None:
        _fuzzy_sim = build_fuzzy_system()

    # Clamp inputs to valid ranges
    difficulty_val  = max(1, min(10, difficulty_val))
    time_left_val   = max(1, min(30, time_left_val))
    preparation_val = max(1, min(10, preparation_val))

    _fuzzy_sim.input["difficulty"]  = difficulty_val
    _fuzzy_sim.input["time_left"]   = time_left_val
    _fuzzy_sim.input["preparation"] = preparation_val

    try:
        _fuzzy_sim.compute()
        priority_score = round(float(_fuzzy_sim.output["priority"]),    2)
        study_hours    = round(float(_fuzzy_sim.output["study_hours"]), 2)
    except Exception as exc:
        # Fallback when no fuzzy rule fires for the given inputs
        print(f"[Fuzzy] compute() failed ({exc}). Using fallback values.")
        # Derive sensible defaults from raw inputs
        priority_score = round(
            min(100.0, (difficulty_val / 10) * 60 + (1 - preparation_val / 10) * 30 + (1 - time_left_val / 30) * 10),
            2,
        )
        study_hours = round(min(10.0, 1 + (difficulty_val / 10) * 5), 2)

    return {
        "priority_score": priority_score,
        "study_hours":    study_hours,
    }


if __name__ == "__main__":
    # Quick smoke-test
    result = get_fuzzy_output(difficulty_val=8, time_left_val=3, preparation_val=2)
    print("Fuzzy output:", result)
