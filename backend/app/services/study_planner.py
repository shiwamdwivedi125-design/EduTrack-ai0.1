"""
AI Study Planner - Rule-based engine (no paid API required)
Optional LLM integration with fallback
"""
from datetime import date, timedelta
from typing import List, Optional, Dict
import math


SUBJECT_TIPS = {
    "mathematics": ["Practice 10 problems daily", "Review formulas each morning", "Solve past papers weekly"],
    "physics": ["Draw diagrams for each concept", "Link theory to real-world examples", "Solve numerical problems"],
    "chemistry": ["Use mnemonics for elements", "Practice balanced equations", "Review periodic table daily"],
    "programming": ["Code for 1 hour daily", "Build mini projects", "Review data structures"],
    "english": ["Read 2 pages daily", "Practice grammar exercises", "Write short essays weekly"],
    "default": ["Review lecture notes", "Make summary cards", "Practice past papers", "Join study groups"]
}


def get_subject_tips(subject: str) -> List[str]:
    subject_lower = subject.lower()
    for key in SUBJECT_TIPS:
        if key in subject_lower:
            return SUBJECT_TIPS[key]
    return SUBJECT_TIPS["default"]


def generate_study_plan(
    weak_subjects: List[str],
    daily_hours: float,
    study_days: List[str],
    exam_date: Optional[date] = None,
    student_cgpa: Optional[float] = None,
    target_cgpa: Optional[float] = None
) -> dict:
    """
    Generate a personalized weekly study plan using rule-based logic.
    No external API required.
    """
    if not study_days:
        study_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    if not weak_subjects:
        weak_subjects = ["General Review"]

    # Calculate days until exam
    days_until_exam = None
    weeks_available = 4
    if exam_date:
        today = date.today()
        days_until_exam = max((exam_date - today).days, 1)
        weeks_available = max(math.ceil(days_until_exam / 7), 1)

    # Allocate hours per subject based on weakness priority
    n_subjects = len(weak_subjects)
    hours_per_subject = {}

    # Distribute time: first subject gets most, rest proportionally
    if n_subjects == 1:
        hours_per_subject[weak_subjects[0]] = daily_hours
    else:
        # Priority allocation: 40% first, rest shared
        first_share = 0.4
        rest_share = (1 - first_share) / (n_subjects - 1)
        for i, subj in enumerate(weak_subjects):
            if i == 0:
                hours_per_subject[subj] = round(daily_hours * first_share, 1)
            else:
                hours_per_subject[subj] = round(daily_hours * rest_share, 1)

    # Build weekly schedule
    weekly_schedule = {}
    subject_cycle = []
    for day in study_days:
        subject_cycle.append(day)

    day_plan = {}
    for idx, day in enumerate(study_days):
        subject_idx = idx % n_subjects
        subject = weak_subjects[subject_idx]
        hours = hours_per_subject[subject]
        tips = get_subject_tips(subject)

        day_plan[day] = {
            "subjects": [subject],
            "hours": hours,
            "tasks": [
                f"Study {subject} for {hours} hours",
                f"Review notes from last session",
                tips[0] if tips else "Practice exercises",
            ],
            "break_schedule": "Take 10-min break every 50 minutes (Pomodoro technique)"
        }

    # Subject recommendations
    subject_recommendations = {}
    for subj in weak_subjects:
        tips = get_subject_tips(subj)
        subject_recommendations[subj] = {
            "daily_target": f"{hours_per_subject.get(subj, 1)} hours/day",
            "weekly_topics": [f"Week {i+1}: Review {subj} Unit {i+1}" for i in range(min(weeks_available, 4))],
            "resources": ["Textbook chapters", "Past year papers", "Online tutorials"],
            "tips": tips,
            "practice": f"Solve minimum 5 practice problems in {subj} daily"
        }

    # Revision schedule
    revision_schedule = []
    if weeks_available > 1:
        for i in range(min(weeks_available, 4)):
            revision_schedule.append({
                "week": i + 1,
                "focus": weak_subjects[i % n_subjects],
                "activity": "Full revision + practice test" if i == weeks_available - 1 else "Chapter review + exercises",
                "hours_total": len(study_days) * daily_hours
            })

    # Progress tracking milestones
    milestones = []
    for i, week in enumerate(range(1, min(weeks_available + 1, 5))):
        milestones.append({
            "week": week,
            "goal": f"Complete {weak_subjects[i % n_subjects]} revision",
            "check": "Take a self-assessment quiz",
            "expected_improvement": f"{10 * (i + 1)}% improvement expected"
        })

    return {
        "plan_title": f"Personalized Study Plan - {len(weak_subjects)} Subject(s)",
        "summary": {
            "total_subjects": n_subjects,
            "daily_study_hours": daily_hours,
            "study_days_per_week": len(study_days),
            "weeks_available": weeks_available,
            "days_until_exam": days_until_exam,
            "current_cgpa": student_cgpa,
            "target_cgpa": target_cgpa,
        },
        "weekly_schedule": day_plan,
        "subject_recommendations": subject_recommendations,
        "revision_schedule": revision_schedule,
        "milestones": milestones,
        "general_tips": [
            "Start each session by reviewing previous day's notes",
            "Use active recall instead of passive reading",
            "Take regular breaks - study in 50-min blocks",
            "Get 7-8 hours of sleep; avoid late-night cramming before exams",
            "Stay hydrated and eat brain-healthy foods",
            "Track your progress weekly and adjust the plan as needed"
        ],
        "disclaimer": "This study plan is generated by a rule-based algorithm as a starting guide. Adapt it to your learning style."
    }
