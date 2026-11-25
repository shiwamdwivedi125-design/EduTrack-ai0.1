"""Goals and achievements endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User, Student, StudyGoal, StudentSemester
from app.core.security import get_current_user
from datetime import datetime

router = APIRouter()

BADGES = {
    "cgpa_7": {"name": "7+ CGPA Achiever", "icon": "🏆", "condition": "cgpa >= 7"},
    "cgpa_8": {"name": "8+ CGPA Achiever", "icon": "🥇", "condition": "cgpa >= 8"},
    "cgpa_9": {"name": "Excellence Award", "icon": "⭐", "condition": "cgpa >= 9"},
    "attendance_90": {"name": "Perfect Attendance", "icon": "📅", "condition": "attendance >= 90"},
    "first_goal": {"name": "Goal Setter", "icon": "🎯", "condition": "first_goal"},
    "10_goals": {"name": "Goal Champion", "icon": "🏅", "condition": "10 goals completed"},
}


@router.get("")
async def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            return {"goals": [], "badges": []}
        student_id = student.id
    else:
        return {"message": "Use student_id parameter"}

    goals = db.query(StudyGoal).filter(StudyGoal.student_id == student_id).order_by(StudyGoal.id.desc()).all()

    return {
        "goals": [{
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "target_value": g.target_value,
            "current_value": g.current_value,
            "goal_type": g.goal_type,
            "deadline": str(g.deadline) if g.deadline else None,
            "is_completed": g.is_completed,
            "badge_earned": g.badge_earned,
            "created_at": str(g.created_at) if g.created_at else None,
        } for g in goals],
        "total": len(goals),
        "completed": sum(1 for g in goals if g.is_completed),
    }


@router.post("")
async def create_goal(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_id = student.id
    else:
        student_id = payload.get("student_id")

    deadline = None
    if payload.get("deadline"):
        from datetime import date
        deadline = date.fromisoformat(payload["deadline"])

    goal = StudyGoal(
        student_id=student_id,
        title=payload["title"],
        description=payload.get("description"),
        target_value=payload.get("target_value"),
        goal_type=payload.get("goal_type", "cgpa"),
        deadline=deadline,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    return {"message": "Goal created", "id": goal.id}


@router.put("/{goal_id}/complete")
async def complete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(StudyGoal).filter(StudyGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.is_completed = True
    goal.completed_at = datetime.utcnow()
    goal.badge_earned = "Goal Achiever 🎯"
    db.commit()

    return {"message": "Congratulations! Goal completed!", "badge": goal.badge_earned}


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(StudyGoal).filter(StudyGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted"}
