"""Marks API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User, Student, Marks, Subject, Semester
from app.core.security import get_current_user
from app.services.academic import calculate_marks, calculate_sgpa, calculate_cgpa
from app.models import StudentSemester
from typing import Optional

router = APIRouter()


@router.post("")
async def add_marks(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    student_id = payload["student_id"]
    subject_id = payload["subject_id"]
    semester_id = payload["semester_id"]
    internal = float(payload.get("internal_marks", 0))
    external = float(payload.get("external_marks", 0))

    # Check subject exists
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Validate marks
    if internal > subject.max_internal:
        raise HTTPException(status_code=400, detail=f"Internal marks exceed maximum ({subject.max_internal})")
    if external > subject.max_external:
        raise HTTPException(status_code=400, detail=f"External marks exceed maximum ({subject.max_external})")

    # Calculate
    calculated = calculate_marks(internal, external, subject_id, db, semester_id)

    # Check existing
    existing = db.query(Marks).filter(
        Marks.student_id == student_id,
        Marks.subject_id == subject_id,
        Marks.semester_id == semester_id
    ).first()

    if existing:
        # Update - never silently overwrite
        for k, v in calculated.items():
            setattr(existing, k, v)
        existing.internal_marks = internal
        existing.external_marks = external
        db.commit()
        db.refresh(existing)
        mark = existing
    else:
        mark = Marks(
            student_id=student_id,
            subject_id=subject_id,
            semester_id=semester_id,
            internal_marks=internal,
            external_marks=external,
            **calculated
        )
        db.add(mark)
        db.commit()
        db.refresh(mark)

    # Recalculate SGPA/CGPA
    _update_sgpa_cgpa(student_id, semester_id, db)

    return {"message": "Marks saved", "marks": {
        "id": mark.id,
        "total": mark.total_marks,
        "percentage": mark.percentage,
        "grade": mark.grade,
        "grade_points": mark.grade_points,
        "is_pass": mark.is_pass,
    }}


def _update_sgpa_cgpa(student_id: int, semester_id: int, db: Session):
    """Update SGPA and CGPA after marks change"""
    sgpa = calculate_sgpa(student_id, semester_id, db)
    marks = db.query(Marks).filter(
        Marks.student_id == student_id,
        Marks.semester_id == semester_id
    ).all()
    total_credits = sum(m.credits for m in marks)
    earned_credits = sum(m.credits for m in marks if m.is_pass)
    backlogs = sum(1 for m in marks if not m.is_pass)

    # Compute CGPA
    all_sems = db.query(StudentSemester).filter(StudentSemester.student_id == student_id).all()
    temp = {s.semester_id: s.sgpa * s.total_credits for s in all_sems if s.total_credits > 0}
    temp[semester_id] = sgpa * total_credits
    temp_credits = {s.semester_id: s.total_credits for s in all_sems}
    temp_credits[semester_id] = total_credits
    total_c = sum(temp_credits.values())
    cgpa = round(sum(temp.values()) / total_c, 2) if total_c > 0 else 0

    existing = db.query(StudentSemester).filter(
        StudentSemester.student_id == student_id,
        StudentSemester.semester_id == semester_id
    ).first()
    if existing:
        existing.sgpa = sgpa
        existing.cgpa = cgpa
        existing.total_credits = total_credits
        existing.earned_credits = earned_credits
        existing.backlogs = backlogs
    else:
        db.add(StudentSemester(
            student_id=student_id,
            semester_id=semester_id,
            sgpa=sgpa,
            cgpa=cgpa,
            total_credits=total_credits,
            earned_credits=earned_credits,
            backlogs=backlogs,
        ))
    db.commit()


@router.get("/student/{student_id}")
async def get_student_marks(
    student_id: int,
    semester_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        s = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not s or s.id != student_id:
            raise HTTPException(status_code=403, detail="Access denied")

    q = db.query(Marks).filter(Marks.student_id == student_id)
    if semester_id:
        q = q.filter(Marks.semester_id == semester_id)

    marks = q.all()
    result = []
    for m in marks:
        subj = db.query(Subject).filter(Subject.id == m.subject_id).first()
        sem = db.query(Semester).filter(Semester.id == m.semester_id).first()
        result.append({
            "id": m.id,
            "subject_name": subj.name if subj else "",
            "subject_code": subj.code if subj else "",
            "semester_name": sem.name if sem else "",
            "semester_number": sem.number if sem else 0,
            "internal_marks": m.internal_marks,
            "external_marks": m.external_marks,
            "total_marks": m.total_marks,
            "max_marks": m.max_marks,
            "percentage": m.percentage,
            "grade": m.grade,
            "grade_points": m.grade_points,
            "credits": m.credits,
            "is_pass": m.is_pass,
        })

    return {"marks": result, "total": len(result)}


@router.get("")
async def list_marks(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Marks)
    if student_id:
        q = q.filter(Marks.student_id == student_id)
    if subject_id:
        q = q.filter(Marks.subject_id == subject_id)
    if semester_id:
        q = q.filter(Marks.semester_id == semester_id)
    marks = q.all()
    return {"marks": [{"id": m.id, "student_id": m.student_id, "subject_id": m.subject_id,
                       "total": m.total_marks, "percentage": m.percentage, "grade": m.grade} for m in marks]}


@router.post("/bulk")
async def bulk_upload_marks(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload marks from CSV data (already parsed)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    records = payload.get("records", [])
    errors = []
    success = 0

    for i, rec in enumerate(records):
        try:
            student_id = rec["student_id"]
            subject_id = rec["subject_id"]
            semester_id = rec["semester_id"]
            internal = float(rec.get("internal_marks", 0))
            external = float(rec.get("external_marks", 0))

            subject = db.query(Subject).filter(Subject.id == subject_id).first()
            if not subject:
                errors.append({"row": i + 1, "error": f"Subject {subject_id} not found"})
                continue

            calculated = calculate_marks(internal, external, subject_id, db, semester_id)
            existing = db.query(Marks).filter(
                Marks.student_id == student_id,
                Marks.subject_id == subject_id,
                Marks.semester_id == semester_id
            ).first()

            if existing:
                for k, v in calculated.items():
                    setattr(existing, k, v)
                existing.internal_marks = internal
                existing.external_marks = external
            else:
                db.add(Marks(
                    student_id=student_id,
                    subject_id=subject_id,
                    semester_id=semester_id,
                    internal_marks=internal,
                    external_marks=external,
                    **calculated
                ))
            success += 1
        except Exception as e:
            errors.append({"row": i + 1, "error": str(e)})

    db.commit()
    return {"success": success, "errors": errors, "total": len(records)}
