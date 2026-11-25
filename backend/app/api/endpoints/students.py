"""Students API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database.session import get_db
from app.models import User, Student, Department, AuditLog
from app.schemas import StudentCreate, StudentOut, PaginatedResponse
from app.core.security import get_current_user, get_password_hash
import csv, io, math

router = APIRouter()


def get_student_or_404(student_id: int, db: Session):
    s = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.department)
    ).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s


@router.get("", response_model=dict)
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="Access denied")

    q = db.query(Student).options(joinedload(Student.user), joinedload(Student.department))

    if search:
        q = q.join(User).filter(
            (User.full_name.ilike(f"%{search}%")) |
            (Student.student_id.ilike(f"%{search}%")) |
            (Student.roll_number.ilike(f"%{search}%"))
        )
    if department_id:
        q = q.filter(Student.department_id == department_id)
    if semester:
        q = q.filter(Student.current_semester == semester)
    if is_active is not None:
        q = q.filter(Student.is_active == is_active)

    total = q.count()
    students = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [format_student(s) for s in students],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size)
    }


def format_student(s: Student) -> dict:
    return {
        "id": s.id,
        "student_id": s.student_id,
        "roll_number": s.roll_number,
        "full_name": s.user.full_name if s.user else "",
        "email": s.user.email if s.user else "",
        "department": s.department.name if s.department else "",
        "department_code": s.department.code if s.department else "",
        "branch": s.branch,
        "current_semester": s.current_semester,
        "admission_year": s.admission_year,
        "academic_session": s.academic_session,
        "is_active": s.is_active,
        "phone": s.phone,
        "guardian_name": s.guardian_name,
    }


@router.get("/me/profile", response_model=dict)
async def get_my_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    s = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.department)
    ).filter(Student.user_id == current_user.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return format_student(s)


@router.get("/{student_id}", response_model=dict)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Students can only see their own profile
    if current_user.role == "student":
        s = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not s or s.id != student_id:
            raise HTTPException(status_code=403, detail="Access denied")

    student = get_student_or_404(student_id, db)
    return format_student(student)


@router.post("", response_model=dict)
async def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create students")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(Student).filter(Student.student_id == payload.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")
    if db.query(Student).filter(Student.roll_number == payload.roll_number).first():
        raise HTTPException(status_code=400, detail="Roll number already exists")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role="student",
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.id,
        student_id=payload.student_id,
        roll_number=payload.roll_number,
        department_id=payload.department_id,
        branch=payload.branch,
        current_semester=payload.current_semester,
        admission_year=payload.admission_year,
        academic_session=payload.academic_session,
        phone=payload.phone,
        guardian_name=payload.guardian_name,
        guardian_phone=payload.guardian_phone,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    db.add(AuditLog(user_id=current_user.id, action="create_student", resource="students", resource_id=student.id))
    db.commit()

    return format_student(get_student_or_404(student.id, db))


@router.put("/{student_id}", response_model=dict)
async def update_student(
    student_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    student = get_student_or_404(student_id, db)
    
    allowed_fields = ["branch", "current_semester", "phone", "guardian_name", "guardian_phone", "is_active"]
    for field in allowed_fields:
        if field in payload:
            setattr(student, field, payload[field])

    db.commit()
    return format_student(get_student_or_404(student_id, db))


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete students")

    student = get_student_or_404(student_id, db)
    # Soft delete
    student.is_active = False
    student.user.is_active = False
    db.commit()
    return {"message": "Student deactivated successfully"}


@router.get("/{student_id}/academic-summary")
async def get_academic_summary(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete academic summary for a student"""
    if current_user.role == "student":
        s = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not s or s.id != student_id:
            raise HTTPException(status_code=403, detail="Access denied")

    from app.models import Marks, StudentSemester, Attendance, Subject, Semester
    from app.services.academic import compute_risk_score

    student = get_student_or_404(student_id, db)

    # Marks
    marks = db.query(Marks).filter(Marks.student_id == student_id).all()
    marks_data = []
    for m in marks:
        subj = db.query(Subject).filter(Subject.id == m.subject_id).first()
        marks_data.append({
            "subject_name": subj.name if subj else "Unknown",
            "subject_code": subj.code if subj else "",
            "semester": m.semester_id,
            "internal": m.internal_marks,
            "external": m.external_marks,
            "total": m.total_marks,
            "max": m.max_marks,
            "percentage": m.percentage,
            "grade": m.grade,
            "grade_points": m.grade_points,
            "credits": m.credits,
            "is_pass": m.is_pass,
        })

    # CGPA history
    sems = db.query(StudentSemester).filter(StudentSemester.student_id == student_id).all()
    cgpa_history = []
    for ss in sems:
        sem = db.query(Semester).filter(Semester.id == ss.semester_id).first()
        cgpa_history.append({
            "semester": sem.name if sem else f"Sem {ss.semester_id}",
            "sgpa": ss.sgpa,
            "cgpa": ss.cgpa,
            "total_credits": ss.total_credits,
            "earned_credits": ss.earned_credits,
            "backlogs": ss.backlogs,
        })

    # Attendance summary
    attendance = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    att_by_subject = {}
    for att in attendance:
        sid = att.subject_id
        if sid not in att_by_subject:
            att_by_subject[sid] = {"total": 0, "present": 0}
        att_by_subject[sid]["total"] += 1
        if att.is_present:
            att_by_subject[sid]["present"] += 1

    att_summary = []
    for subj_id, counts in att_by_subject.items():
        subj = db.query(Subject).filter(Subject.id == subj_id).first()
        pct = round(counts["present"] / counts["total"] * 100, 2) if counts["total"] > 0 else 0
        att_summary.append({
            "subject_name": subj.name if subj else "Unknown",
            "subject_code": subj.code if subj else "",
            "total_classes": counts["total"],
            "present_classes": counts["present"],
            "attendance_percentage": pct,
            "status": "critical" if pct < 65 else ("warning" if pct < 75 else "ok"),
        })

    # Risk score
    risk = compute_risk_score(student_id, db)
    current_cgpa = cgpa_history[-1]["cgpa"] if cgpa_history else 0

    return {
        "student": format_student(student),
        "marks": marks_data,
        "cgpa_history": cgpa_history,
        "current_cgpa": current_cgpa,
        "attendance": att_summary,
        "risk": risk,
    }
