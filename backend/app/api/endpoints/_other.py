"""Remaining simple endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User, Teacher, Department, Subject, Semester, Notification, AcademicAlert, Student, Marks, Attendance, StudentSemester
from app.core.security import get_current_user, get_password_hash
from typing import Optional

# ── Users ──
users_router = APIRouter()

@users_router.get("")
async def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role, "is_active": u.is_active} for u in users]

@users_router.put("/{user_id}")
async def update_user(user_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "full_name" in payload:
        user.full_name = payload["full_name"]
    if "is_active" in payload and current_user.role == "admin":
        user.is_active = payload["is_active"]
    if "password" in payload:
        user.hashed_password = get_password_hash(payload["password"])
    db.commit()
    return {"message": "Updated"}


# ── Teachers ──
teachers_router = APIRouter()

@teachers_router.get("")
async def list_teachers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    teachers = db.query(Teacher).all()
    return [{"id": t.id, "teacher_id": t.teacher_id, "name": t.user.full_name if t.user else "",
             "email": t.user.email if t.user else "", "department": t.department.name if t.department else "",
             "designation": t.designation, "specialization": t.specialization} for t in teachers]

@teachers_router.post("")
async def create_teacher(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if db.query(User).filter(User.email == payload["email"]).first():
        raise HTTPException(status_code=400, detail="Email exists")
    user = User(email=payload["email"], hashed_password=get_password_hash(payload.get("password", "Teacher@123")),
                full_name=payload["full_name"], role="teacher")
    db.add(user); db.flush()
    teacher = Teacher(user_id=user.id, teacher_id=payload["teacher_id"],
                      department_id=payload["department_id"], designation=payload.get("designation"),
                      specialization=payload.get("specialization"))
    db.add(teacher); db.commit()
    return {"message": "Teacher created", "id": teacher.id}


# ── Departments ──
depts_router = APIRouter()

@depts_router.get("")
async def list_depts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    depts = db.query(Department).all()
    students_count = {d.id: db.query(Student).filter(Student.department_id == d.id).count() for d in depts}
    return [{"id": d.id, "name": d.name, "code": d.code, "hod_name": d.hod_name,
             "is_active": d.is_active, "students_count": students_count[d.id]} for d in depts]

@depts_router.post("")
async def create_dept(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    dept = Department(name=payload["name"], code=payload["code"], hod_name=payload.get("hod_name"))
    db.add(dept); db.commit()
    return {"message": "Department created", "id": dept.id}


# ── Subjects ──
subjects_router = APIRouter()

@subjects_router.get("")
async def list_subjects(dept_id: Optional[int] = None, sem_id: Optional[int] = None,
                         db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Subject)
    if dept_id: q = q.filter(Subject.department_id == dept_id)
    if sem_id: q = q.filter(Subject.semester_id == sem_id)
    subjects = q.all()
    return [{"id": s.id, "name": s.name, "code": s.code, "credits": s.credits,
             "max_internal": s.max_internal, "max_external": s.max_external,
             "semester_id": s.semester_id, "department_id": s.department_id,
             "teacher_id": s.teacher_id} for s in subjects]

@subjects_router.post("")
async def create_subject(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if db.query(Subject).filter(Subject.code == payload["code"]).first():
        raise HTTPException(status_code=400, detail="Subject code exists")
    s = Subject(name=payload["name"], code=payload["code"], department_id=payload["department_id"],
                semester_id=payload["semester_id"], teacher_id=payload.get("teacher_id"),
                credits=payload.get("credits", 4), max_internal=payload.get("max_internal", 30),
                max_external=payload.get("max_external", 70), max_total=payload.get("max_total", 100))
    db.add(s); db.commit()
    return {"message": "Subject created", "id": s.id}


# ── Semesters ──
semesters_router = APIRouter()

@semesters_router.get("")
async def list_semesters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sems = db.query(Semester).order_by(Semester.number).all()
    return [{"id": s.id, "number": s.number, "name": s.name, "academic_year": s.academic_year, "is_current": s.is_current} for s in sems]

@semesters_router.post("")
async def create_semester(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    sem = Semester(number=payload["number"], name=payload["name"], academic_year=payload["academic_year"],
                   is_current=payload.get("is_current", False))
    db.add(sem); db.commit()
    return {"message": "Semester created", "id": sem.id}


# ── Notifications ──
notif_router = APIRouter()

@notif_router.get("")
async def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.id.desc()).limit(50).all()
    return [{"id": n.id, "title": n.title, "message": n.message, "type": n.type,
             "is_read": n.is_read, "created_at": str(n.created_at) if n.created_at else None} for n in notifs]

@notif_router.put("/{notif_id}/read")
async def mark_read(notif_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if n: n.is_read = True; db.commit()
    return {"message": "Marked read"}


# ── Alerts ──
alerts_router = APIRouter()

@alerts_router.get("")
async def list_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student: return {"alerts": []}
        alerts = db.query(AcademicAlert).filter(AcademicAlert.student_id == student.id).all()
    else:
        alerts = db.query(AcademicAlert).filter(AcademicAlert.is_resolved == False).order_by(AcademicAlert.risk_score.desc()).all()
    
    result = []
    for a in alerts:
        s = db.query(Student).filter(Student.id == a.student_id).first()
        result.append({"id": a.id, "student_id": a.student_id,
                       "student_name": s.user.full_name if s and s.user else "",
                       "student_code": s.student_id if s else "",
                       "risk_level": a.risk_level, "risk_score": a.risk_score,
                       "reasons": a.reasons, "recommendations": a.recommendations,
                       "is_resolved": a.is_resolved})
    return {"alerts": result}

@alerts_router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")
    alert = db.query(AcademicAlert).filter(AcademicAlert.id == alert_id).first()
    if not alert: raise HTTPException(status_code=404, detail="Alert not found")
    from datetime import datetime
    alert.is_resolved = True; alert.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Alert resolved"}


# ── Reports ──
reports_router = APIRouter()

@reports_router.get("/student/{student_id}")
async def student_report(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate student academic report data"""
    if current_user.role == "student":
        s = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not s or s.id != student_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    marks = db.query(Marks).filter(Marks.student_id == student_id).all()
    sems = db.query(StudentSemester).filter(StudentSemester.student_id == student_id).all()
    att = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    att_pct = round(sum(1 for a in att if a.is_present) / len(att) * 100, 2) if att else 0
    cgpa = sems[-1].cgpa if sems else 0

    return {
        "report_type": "individual_student",
        "student": {
            "name": student.user.full_name if student.user else "",
            "id": student.student_id,
            "roll": student.roll_number,
            "semester": student.current_semester,
            "department": student.department.name if student.department else "",
        },
        "summary": {
            "cgpa": cgpa,
            "total_marks": len(marks),
            "passed_subjects": sum(1 for m in marks if m.is_pass),
            "failed_subjects": sum(1 for m in marks if not m.is_pass),
            "overall_attendance": att_pct,
        },
        "semester_data": [{
            "semester": ss.semester_id,
            "sgpa": ss.sgpa,
            "cgpa": ss.cgpa,
            "backlogs": ss.backlogs,
        } for ss in sems],
        "marks_data": [{
            "subject_id": m.subject_id,
            "internal": m.internal_marks,
            "external": m.external_marks,
            "total": m.total_marks,
            "percentage": m.percentage,
            "grade": m.grade,
        } for m in marks],
        "generated_at": str(__import__('datetime').datetime.now()),
        "disclaimer": "This report contains synthetic data for demonstration purposes only."
    }

@reports_router.get("/department/{dept_id}")
async def department_report(dept_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept: raise HTTPException(status_code=404, detail="Department not found")

    students = db.query(Student).filter(Student.department_id == dept_id).all()
    student_ids = [s.id for s in students]
    marks = db.query(Marks).filter(Marks.student_id.in_(student_ids)).all()
    
    return {
        "report_type": "department",
        "department": {"name": dept.name, "code": dept.code},
        "total_students": len(students),
        "avg_percentage": round(sum(m.percentage for m in marks) / len(marks), 2) if marks else 0,
        "pass_rate": round(sum(1 for m in marks if m.is_pass) / len(marks) * 100, 2) if marks else 0,
        "generated_at": str(__import__('datetime').datetime.now()),
    }
