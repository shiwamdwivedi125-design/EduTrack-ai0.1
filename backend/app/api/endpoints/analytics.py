"""Analytics endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models import (
    User, Student, Teacher, Department, Marks, Attendance,
    StudentSemester, AcademicAlert, Subject
)
from app.core.security import get_current_user

router = APIRouter()


@router.get("/overview")
async def overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dashboard KPI overview"""
    total_students = db.query(Student).count()
    active_students = db.query(Student).filter(Student.is_active == True).count()
    total_teachers = db.query(Teacher).count()
    total_depts = db.query(Department).count()

    # Avg CGPA
    sems = db.query(StudentSemester).all()
    if sems:
        latest_per_student = {}
        for s in sems:
            if s.student_id not in latest_per_student or s.id > latest_per_student[s.student_id].id:
                latest_per_student[s.student_id] = s
        avg_cgpa = round(sum(s.cgpa for s in latest_per_student.values()) / len(latest_per_student), 2)
    else:
        avg_cgpa = 0.0

    # Avg attendance
    att_records = db.query(Attendance).all()
    if att_records:
        total = len(att_records)
        present = sum(1 for a in att_records if a.is_present)
        avg_att = round((present / total) * 100, 2)
    else:
        avg_att = 0.0

    # Students needing support (alerts)
    alerts = db.query(AcademicAlert).filter(AcademicAlert.is_resolved == False).all()
    high_risk = sum(1 for a in alerts if a.risk_level == "high")
    needing_support = len(alerts)

    return {
        "total_students": total_students,
        "active_students": active_students,
        "completed_students": total_students - active_students,
        "total_teachers": total_teachers,
        "total_departments": total_depts,
        "average_cgpa": avg_cgpa,
        "average_attendance": avg_att,
        "students_needing_support": needing_support,
        "high_risk_students": high_risk,
    }


@router.get("/performance")
async def performance_analytics(
    department_id: int = None,
    semester_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Performance distribution and analytics"""
    marks_q = db.query(Marks)
    if semester_id:
        marks_q = marks_q.filter(Marks.semester_id == semester_id)

    all_marks = marks_q.all()

    # Grade distribution
    grade_dist = {}
    for m in all_marks:
        grade_dist[m.grade or "F"] = grade_dist.get(m.grade or "F", 0) + 1

    # Pass/fail
    pass_count = sum(1 for m in all_marks if m.is_pass)
    fail_count = len(all_marks) - pass_count

    # CGPA distribution
    all_cgpa = db.query(StudentSemester).all()
    latest_per_student = {}
    for s in all_cgpa:
        if s.student_id not in latest_per_student or s.id > latest_per_student[s.student_id].id:
            latest_per_student[s.student_id] = s

    cgpa_buckets = {"<5": 0, "5-6": 0, "6-7": 0, "7-8": 0, "8-9": 0, "9-10": 0}
    for s in latest_per_student.values():
        c = s.cgpa
        if c < 5:
            cgpa_buckets["<5"] += 1
        elif c < 6:
            cgpa_buckets["5-6"] += 1
        elif c < 7:
            cgpa_buckets["6-7"] += 1
        elif c < 8:
            cgpa_buckets["7-8"] += 1
        elif c < 9:
            cgpa_buckets["8-9"] += 1
        else:
            cgpa_buckets["9-10"] += 1

    # Department-wise average CGPA
    depts = db.query(Department).all()
    dept_performance = []
    for dept in depts:
        dept_students = db.query(Student).filter(Student.department_id == dept.id).all()
        dept_student_ids = [s.id for s in dept_students]
        dept_sems = [s for s in latest_per_student.values() if s.student_id in dept_student_ids]
        avg = round(sum(s.cgpa for s in dept_sems) / len(dept_sems), 2) if dept_sems else 0
        dept_performance.append({"department": dept.code, "avg_cgpa": avg, "students": len(dept_student_ids)})

    # Semester-wise average SGPA
    from app.models import Semester
    semesters = db.query(Semester).order_by(Semester.number).all()
    sem_performance = []
    for sem in semesters:
        sem_records = [s for s in all_cgpa if s.semester_id == sem.id]
        avg = round(sum(s.sgpa for s in sem_records) / len(sem_records), 2) if sem_records else 0
        sem_performance.append({"semester": sem.name, "avg_sgpa": avg, "count": len(sem_records)})

    # Subject-wise average marks
    subjects = db.query(Subject).all()
    subj_performance = []
    for subj in subjects[:20]:  # Top 20
        subj_marks = [m for m in all_marks if m.subject_id == subj.id]
        avg = round(sum(m.percentage for m in subj_marks) / len(subj_marks), 2) if subj_marks else 0
        subj_performance.append({"subject": subj.code, "name": subj.name, "avg_percentage": avg, "count": len(subj_marks)})

    return {
        "grade_distribution": [{"grade": k, "count": v} for k, v in sorted(grade_dist.items())],
        "pass_fail": [{"name": "Pass", "value": pass_count}, {"name": "Fail", "value": fail_count}],
        "cgpa_distribution": [{"range": k, "count": v} for k, v in cgpa_buckets.items()],
        "department_performance": dept_performance,
        "semester_performance": sem_performance,
        "subject_performance": sorted(subj_performance, key=lambda x: x["avg_percentage"], reverse=True),
        "total_marks_records": len(all_marks),
        "avg_percentage": round(sum(m.percentage for m in all_marks) / len(all_marks), 2) if all_marks else 0,
    }


@router.get("/attendance")
async def attendance_analytics(
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Attendance analytics"""
    att_records = db.query(Attendance).all()

    total = len(att_records)
    present = sum(1 for a in att_records if a.is_present)
    avg_att = round((present / total) * 100, 2) if total > 0 else 0

    # Attendance buckets
    att_by_student = {}
    for att in att_records:
        sid = att.student_id
        if sid not in att_by_student:
            att_by_student[sid] = {"total": 0, "present": 0}
        att_by_student[sid]["total"] += 1
        if att.is_present:
            att_by_student[sid]["present"] += 1

    buckets = {"<50%": 0, "50-65%": 0, "65-75%": 0, "75-85%": 0, "85-100%": 0}
    low_att_students = []
    for sid, counts in att_by_student.items():
        pct = round(counts["present"] / counts["total"] * 100, 2) if counts["total"] > 0 else 0
        if pct < 50:
            buckets["<50%"] += 1
        elif pct < 65:
            buckets["50-65%"] += 1
        elif pct < 75:
            buckets["65-75%"] += 1
        elif pct < 85:
            buckets["75-85%"] += 1
        else:
            buckets["85-100%"] += 1

        if pct < 75:
            student = db.query(Student).filter(Student.id == sid).first()
            if student and student.user:
                low_att_students.append({
                    "student_id": sid,
                    "name": student.user.full_name,
                    "student_code": student.student_id,
                    "attendance_percentage": pct,
                    "total_classes": counts["total"],
                    "present_classes": counts["present"],
                })

    low_att_students.sort(key=lambda x: x["attendance_percentage"])

    return {
        "overall_attendance": avg_att,
        "total_records": total,
        "distribution": [{"range": k, "count": v} for k, v in buckets.items()],
        "low_attendance_students": low_att_students[:50],
        "students_below_75": sum(1 for s in att_by_student.values() if s["total"] > 0 and s["present"]/s["total"]*100 < 75),
    }


@router.get("/risk-summary")
async def risk_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Academic risk summary"""
    alerts = db.query(AcademicAlert).filter(AcademicAlert.is_resolved == False).all()
    high = [a for a in alerts if a.risk_level == "high"]
    moderate = [a for a in alerts if a.risk_level == "moderate"]
    low = [a for a in alerts if a.risk_level == "low"]

    risk_students = []
    for alert in sorted(alerts, key=lambda a: a.risk_score, reverse=True)[:50]:
        student = db.query(Student).filter(Student.id == alert.student_id).first()
        if student and student.user:
            risk_students.append({
                "student_id": alert.student_id,
                "name": student.user.full_name,
                "student_code": student.student_id,
                "risk_level": alert.risk_level,
                "risk_score": alert.risk_score,
                "reasons": alert.reasons,
                "recommendations": alert.recommendations,
            })

    return {
        "total_alerts": len(alerts),
        "high_risk": len(high),
        "moderate_risk": len(moderate),
        "low_risk": len(low),
        "distribution": [
            {"level": "High", "count": len(high), "color": "#ef4444"},
            {"level": "Moderate", "count": len(moderate), "color": "#f59e0b"},
            {"level": "Low", "count": len(low), "color": "#10b981"},
        ],
        "top_risk_students": risk_students,
        "disclaimer": "Risk scores are decision-support indicators, not automated outcome determiners."
    }
