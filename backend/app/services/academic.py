"""
Academic Calculation Services - EduTrack AI
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models import Marks, GradingRule, StudentSemester, Attendance, Subject


def calculate_grade(percentage: float, db: Session) -> tuple:
    """Calculate grade and grade points from percentage using configurable rules"""
    rules = db.query(GradingRule).order_by(GradingRule.min_percentage.desc()).all()
    
    # Fallback default rules
    if not rules:
        default = [
            (90, 100, "O", 10, True),
            (80, 90, "A+", 9, True),
            (70, 80, "A", 8, True),
            (60, 70, "B+", 7, True),
            (50, 60, "B", 6, True),
            (40, 50, "C", 5, True),
            (0, 40, "F", 0, False),
        ]
        for min_p, max_p, grade, gp, is_pass in default:
            if min_p <= percentage < max_p or (percentage >= 90 and grade == "O"):
                return grade, gp, is_pass
        return "F", 0, False

    for rule in rules:
        if rule.min_percentage <= percentage <= rule.max_percentage:
            return rule.grade, rule.grade_points, rule.is_pass

    return "F", 0, False


def calculate_marks(internal: float, external: float, subject_id: int, db: Session, semester_id: int) -> dict:
    """Calculate total, percentage, grade for marks entry"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        max_marks = 100
    else:
        max_marks = subject.max_total

    total = internal + external
    percentage = (total / max_marks) * 100 if max_marks > 0 else 0
    grade, grade_points, is_pass = calculate_grade(percentage, db)
    credits = subject.credits if subject else 4

    return {
        "total_marks": round(total, 2),
        "max_marks": max_marks,
        "percentage": round(percentage, 2),
        "grade": grade,
        "grade_points": grade_points,
        "credits": credits,
        "is_pass": is_pass,
    }


def calculate_sgpa(student_id: int, semester_id: int, db: Session) -> float:
    """Calculate SGPA for a student in a semester"""
    marks = db.query(Marks).filter(
        Marks.student_id == student_id,
        Marks.semester_id == semester_id
    ).all()

    if not marks:
        return 0.0

    total_credits = sum(m.credits for m in marks)
    if total_credits == 0:
        return 0.0

    weighted_sum = sum(m.grade_points * m.credits for m in marks)
    return round(weighted_sum / total_credits, 2)


def calculate_cgpa(student_id: int, db: Session) -> float:
    """Calculate cumulative CGPA across all semesters"""
    semesters = db.query(StudentSemester).filter(
        StudentSemester.student_id == student_id
    ).all()

    if not semesters:
        return 0.0

    total_credits = sum(s.total_credits for s in semesters if s.total_credits > 0)
    if total_credits == 0:
        return 0.0

    weighted = sum(s.sgpa * s.total_credits for s in semesters if s.total_credits > 0)
    return round(weighted / total_credits, 2)


def get_attendance_percentage(student_id: int, subject_id: int, db: Session) -> float:
    """Calculate attendance % for a student in a subject"""
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.subject_id == subject_id
    ).all()

    if not records:
        return 0.0

    total = len(records)
    present = sum(1 for r in records if r.is_present)
    return round((present / total) * 100, 2) if total > 0 else 0.0


def compute_risk_score(student_id: int, db: Session) -> dict:
    """
    Compute academic risk score for a student.
    Returns risk_score (0-100), risk_level, reasons, recommendations.
    NOTE: This is a decision-support tool, not an automated outcome determiner.
    """
    score = 0
    reasons = []
    recommendations = []

    # Attendance check
    attendance_records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    if attendance_records:
        total = len(attendance_records)
        present = sum(1 for r in attendance_records if r.is_present)
        pct = (present / total) * 100 if total > 0 else 0

        if pct < 50:
            score += 35
            reasons.append(f"Very low attendance: {pct:.1f}% (below 50%)")
            recommendations.append("Attend all upcoming classes; discuss attendance issues with teacher immediately")
        elif pct < 65:
            score += 25
            reasons.append(f"Low attendance: {pct:.1f}% (below 65%)")
            recommendations.append("Improve attendance to at least 75% to avoid academic penalties")
        elif pct < 75:
            score += 15
            reasons.append(f"Attendance below requirement: {pct:.1f}% (below 75%)")
            recommendations.append("Attend classes consistently to reach the 75% minimum threshold")

    # Marks check
    marks_records = db.query(Marks).filter(
        Marks.student_id == student_id
    ).all()

    if marks_records:
        failing = [m for m in marks_records if not m.is_pass]
        avg_pct = sum(m.percentage for m in marks_records) / len(marks_records)

        if failing:
            score += min(len(failing) * 10, 30)
            reasons.append(f"Failed in {len(failing)} subject(s)")
            recommendations.append(f"Focus on clearing backlogs in failed subjects; seek teacher guidance")

        if avg_pct < 40:
            score += 20
            reasons.append(f"Very low average marks: {avg_pct:.1f}%")
            recommendations.append("Study regularly and seek tutoring for all subjects")
        elif avg_pct < 55:
            score += 10
            reasons.append(f"Below average marks: {avg_pct:.1f}%")
            recommendations.append("Increase study hours and review past question papers")

    # CGPA check
    student_sems = db.query(StudentSemester).filter(
        StudentSemester.student_id == student_id
    ).all()

    if student_sems:
        latest = sorted(student_sems, key=lambda s: s.id)[-1]
        if latest.cgpa < 5.0:
            score += 15
            reasons.append(f"CGPA below 5.0: {latest.cgpa:.2f}")
            recommendations.append("Create a study plan focusing on improving weaker subjects")
        elif latest.cgpa < 6.5:
            score += 5
            reasons.append(f"CGPA below 6.5: {latest.cgpa:.2f}")
            recommendations.append("Target specific weak subjects to improve overall CGPA")

    score = min(score, 100)

    if score >= 60:
        risk_level = "high"
    elif score >= 30:
        risk_level = "moderate"
    else:
        risk_level = "low"

    return {
        "risk_score": round(score, 1),
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendations": recommendations,
        "disclaimer": "This is a decision-support indicator. Final academic decisions must be made by qualified educators."
    }
