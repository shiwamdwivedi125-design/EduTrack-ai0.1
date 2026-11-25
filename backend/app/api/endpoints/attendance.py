"""Attendance endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User, Student, Attendance, Subject
from app.core.security import get_current_user
from typing import Optional
from datetime import date

router = APIRouter()


@router.post("")
async def add_attendance(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    student_id = payload["student_id"]
    subject_id = payload["subject_id"]
    att_date = payload.get("date", str(date.today()))
    if isinstance(att_date, str):
        att_date = date.fromisoformat(att_date)
    is_present = payload.get("is_present", True)
    total_classes = payload.get("total_classes", 0)
    present_classes = payload.get("present_classes", 0)

    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.subject_id == subject_id,
        Attendance.date == att_date
    ).first()

    if existing:
        existing.is_present = is_present
        existing.total_classes = total_classes
        existing.present_classes = present_classes
        db.commit()
        return {"message": "Attendance updated", "id": existing.id}

    att = Attendance(
        student_id=student_id,
        subject_id=subject_id,
        date=att_date,
        is_present=is_present,
        total_classes=total_classes,
        present_classes=present_classes,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return {"message": "Attendance recorded", "id": att.id}


@router.post("/bulk")
async def bulk_attendance(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    records = payload.get("records", [])
    success = 0
    errors = []

    for i, rec in enumerate(records):
        try:
            att_date = date.fromisoformat(str(rec.get("date", str(date.today()))))
            existing = db.query(Attendance).filter(
                Attendance.student_id == rec["student_id"],
                Attendance.subject_id == rec["subject_id"],
                Attendance.date == att_date
            ).first()
            if existing:
                existing.is_present = rec.get("is_present", True)
            else:
                db.add(Attendance(
                    student_id=rec["student_id"],
                    subject_id=rec["subject_id"],
                    date=att_date,
                    is_present=rec.get("is_present", True),
                    total_classes=rec.get("total_classes", 0),
                    present_classes=rec.get("present_classes", 0),
                ))
            success += 1
        except Exception as e:
            errors.append({"row": i + 1, "error": str(e)})

    db.commit()
    return {"success": success, "errors": errors}


@router.get("")
async def list_attendance(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Attendance)
    if student_id:
        q = q.filter(Attendance.student_id == student_id)
    if subject_id:
        q = q.filter(Attendance.subject_id == subject_id)
    records = q.limit(500).all()
    return {"attendance": [
        {"id": a.id, "student_id": a.student_id, "subject_id": a.subject_id,
         "date": str(a.date), "is_present": a.is_present}
        for a in records
    ]}


@router.get("/student/{student_id}")
async def student_attendance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        s = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not s or s.id != student_id:
            raise HTTPException(status_code=403, detail="Access denied")

    records = db.query(Attendance).filter(Attendance.student_id == student_id).all()

    # Summarize by subject
    by_subject = {}
    for att in records:
        sid = att.subject_id
        if sid not in by_subject:
            by_subject[sid] = {"total": 0, "present": 0, "dates": []}
        by_subject[sid]["total"] += 1
        if att.is_present:
            by_subject[sid]["present"] += 1
        by_subject[sid]["dates"].append({"date": str(att.date), "present": att.is_present})

    result = []
    for subj_id, counts in by_subject.items():
        subj = db.query(Subject).filter(Subject.id == subj_id).first()
        pct = round(counts["present"] / counts["total"] * 100, 2) if counts["total"] > 0 else 0
        result.append({
            "subject_id": subj_id,
            "subject_name": subj.name if subj else "Unknown",
            "subject_code": subj.code if subj else "",
            "total_classes": counts["total"],
            "present_classes": counts["present"],
            "absent_classes": counts["total"] - counts["present"],
            "attendance_percentage": pct,
            "status": "critical" if pct < 65 else ("warning" if pct < 75 else "ok"),
            "recent_dates": sorted(counts["dates"], key=lambda x: x["date"], reverse=True)[:10],
        })

    overall_total = sum(c["total"] for c in by_subject.values())
    overall_present = sum(c["present"] for c in by_subject.values())
    overall_pct = round((overall_present / overall_total) * 100, 2) if overall_total > 0 else 0

    return {
        "student_id": student_id,
        "subjects": result,
        "overall_attendance": overall_pct,
        "overall_total": overall_total,
        "overall_present": overall_present,
    }
