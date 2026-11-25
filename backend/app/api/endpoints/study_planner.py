"""Study Planner endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User, Student, StudyPlan, StudentSemester
from app.core.security import get_current_user
from app.services.study_planner import generate_study_plan
from datetime import date

router = APIRouter()


@router.post("/generate")
async def generate_plan(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        student_id = student.id
    else:
        student_id = payload.get("student_id")
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id required")

    weak_subjects = payload.get("weak_subjects", [])
    daily_hours = float(payload.get("daily_hours", 4))
    study_days = payload.get("study_days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    exam_date_str = payload.get("exam_date")
    target_cgpa = payload.get("target_cgpa")

    exam_date = None
    if exam_date_str:
        try:
            exam_date = date.fromisoformat(exam_date_str)
        except Exception:
            pass

    # Get current CGPA
    sems = db.query(StudentSemester).filter(StudentSemester.student_id == student_id).all()
    student_cgpa = sems[-1].cgpa if sems else None

    plan_data = generate_study_plan(
        weak_subjects=weak_subjects,
        daily_hours=daily_hours,
        study_days=study_days,
        exam_date=exam_date,
        student_cgpa=student_cgpa,
        target_cgpa=target_cgpa,
    )

    # Save plan
    plan = StudyPlan(
        student_id=student_id,
        title=plan_data["plan_title"],
        weak_subjects=weak_subjects,
        daily_hours=daily_hours,
        study_days=study_days,
        exam_date=exam_date,
        plan_data=plan_data,
        is_active=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {
        "id": plan.id,
        "plan": plan_data,
        "saved": True
    }


@router.get("")
async def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            return {"plans": []}
        plans = db.query(StudyPlan).filter(
            StudyPlan.student_id == student.id,
            StudyPlan.is_active == True
        ).order_by(StudyPlan.id.desc()).all()
    else:
        plans = db.query(StudyPlan).order_by(StudyPlan.id.desc()).limit(50).all()

    return {
        "plans": [{
            "id": p.id,
            "title": p.title,
            "weak_subjects": p.weak_subjects,
            "daily_hours": p.daily_hours,
            "study_days": p.study_days,
            "plan": p.plan_data,
            "created_at": str(p.created_at) if p.created_at else None,
        } for p in plans]
    }


@router.get("/{plan_id}")
async def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student or student.id != plan.student_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": plan.id,
        "title": plan.title,
        "weak_subjects": plan.weak_subjects,
        "daily_hours": plan.daily_hours,
        "study_days": plan.study_days,
        "plan": plan.plan_data,
        "created_at": str(plan.created_at) if plan.created_at else None,
    }
