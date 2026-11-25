"""
Extended API Endpoints for EduTrack AI:
- Interventions Tracker
- Placement Readiness & Skills
- Configurable Grading Rules
- CSV/Excel Bulk Import (Preview + Validation + Confirm)
- Descriptive Analytics & Seaborn Charts
- Downloadable PDF & Excel Reports
- Audit Logs
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io, csv, json
from datetime import date, datetime

from app.database.session import get_db
from app.models import (
    User, Student, Teacher, Department, Subject, Semester,
    Marks, Attendance, GradingRule, StudentSemester, AcademicAlert,
    Intervention, PlacementProgress, StudentSkill, AuditLog
)
from app.core.security import get_current_user, get_password_hash
from app.services.academic import calculate_marks
from app.analytics.engine import compute_descriptive_analytics, generate_seaborn_charts
from app.reports.generator import generate_pdf_report, generate_excel_report

# ─────────────────────────── Interventions ───────────────────────────
interventions_router = APIRouter()


@interventions_router.get("")
async def list_interventions(
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Intervention)
    if current_user.role == "student":
        st = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not st:
            return {"interventions": []}
        q = q.filter(Intervention.student_id == st.id)
    elif student_id:
        q = q.filter(Intervention.student_id == student_id)

    items = q.order_by(Intervention.id.desc()).all()
    result = []
    for iv in items:
        st = db.query(Student).filter(Student.id == iv.student_id).first()
        tch = db.query(Teacher).filter(Teacher.id == iv.teacher_id).first()
        result.append({
            "id": iv.id,
            "student_id": iv.student_id,
            "student_name": st.user.full_name if st and st.user else "",
            "student_code": st.student_id if st else "",
            "teacher_name": tch.user.full_name if tch and tch.user else "",
            "title": iv.title,
            "description": iv.description,
            "action_taken": iv.action_taken,
            "status": iv.status,
            "follow_up_date": str(iv.follow_up_date) if iv.follow_up_date else None,
            "created_at": str(iv.created_at) if iv.created_at else None,
        })
    return {"interventions": result}


@interventions_router.post("")
async def create_intervention(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can assign interventions")

    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        teacher = db.query(Teacher).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="No teacher profile found")

    follow_up = None
    if payload.get("follow_up_date"):
        try:
            follow_up = date.fromisoformat(payload["follow_up_date"])
        except Exception:
            pass

    iv = Intervention(
        student_id=payload["student_id"],
        teacher_id=teacher.id,
        title=payload["title"],
        description=payload.get("description", ""),
        action_taken=payload.get("action_taken", ""),
        status=payload.get("status", "pending"),
        follow_up_date=follow_up,
    )
    db.add(iv)
    db.commit()
    db.refresh(iv)
    return {"message": "Intervention created", "id": iv.id}


@interventions_router.put("/{intervention_id}")
async def update_intervention(
    intervention_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")
    iv = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not iv:
        raise HTTPException(status_code=404, detail="Intervention not found")
    for field in ["status", "action_taken", "description"]:
        if field in payload:
            setattr(iv, field, payload[field])
    db.commit()
    return {"message": "Intervention updated"}


# ─────────────────────────── Placement Readiness ───────────────────────────
placement_router = APIRouter()


@placement_router.get("/me")
async def get_my_placement(
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        st = db.query(Student).filter(Student.user_id == current_user.id).first()
    elif student_id:
        st = db.query(Student).filter(Student.id == student_id).first()
    else:
        st = db.query(Student).first()

    if not st:
        raise HTTPException(status_code=404, detail="Student not found")

    prog = db.query(PlacementProgress).filter(PlacementProgress.student_id == st.id).first()
    skills = db.query(StudentSkill).filter(StudentSkill.student_id == st.id).all()
    sems = db.query(StudentSemester).filter(StudentSemester.student_id == st.id).all()
    cgpa = sems[-1].cgpa if sems else 0.0

    if not prog:
        cgpa_score = round(min((cgpa / 10) * 100, 100), 1)
        prog = PlacementProgress(
            student_id=st.id,
            cgpa_score=cgpa_score,
            technical_score=50.0,
            aptitude_score=50.0,
            projects_count=1,
            internships_count=0,
            certifications_count=1,
            mock_interviews=1,
            overall_readiness=round(cgpa_score * 0.3 + 50 * 0.5 + 7, 1),
            target_companies=["TCS", "Infosys"],
        )
        db.add(prog)
        db.commit()
        db.refresh(prog)

    return {
        "student_id": st.id,
        "student_name": st.user.full_name if st.user else "",
        "cgpa": cgpa,
        "cgpa_score": prog.cgpa_score,
        "technical_score": prog.technical_score,
        "aptitude_score": prog.aptitude_score,
        "projects_count": prog.projects_count,
        "internships_count": prog.internships_count,
        "certifications_count": prog.certifications_count,
        "mock_interviews": prog.mock_interviews,
        "overall_readiness": prog.overall_readiness,
        "target_companies": prog.target_companies or [],
        "notes": prog.notes or "",
        "skills": [{"id": sk.id, "skill_name": sk.skill_name, "proficiency_level": sk.proficiency_level, "category": sk.category} for sk in skills],
        "disclaimer": "Placement readiness is an indicative metric based on academic and preparation inputs; placement is not guaranteed."
    }


@placement_router.put("/me")
async def update_my_placement(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        st = db.query(Student).filter(Student.user_id == current_user.id).first()
    else:
        st = db.query(Student).filter(Student.id == payload.get("student_id")).first()
    if not st:
        raise HTTPException(status_code=404, detail="Student not found")

    prog = db.query(PlacementProgress).filter(PlacementProgress.student_id == st.id).first()
    if not prog:
        prog = PlacementProgress(student_id=st.id)
        db.add(prog)

    for f in ["technical_score", "aptitude_score", "projects_count", "internships_count",
              "certifications_count", "mock_interviews", "target_companies", "notes"]:
        if f in payload:
            setattr(prog, f, payload[f])

    overall = (
        (prog.cgpa_score or 0) * 0.30 +
        (prog.technical_score or 0) * 0.30 +
        (prog.aptitude_score or 0) * 0.20 +
        min((prog.projects_count or 0) * 5, 10) +
        min((prog.mock_interviews or 0) * 2, 10)
    )
    prog.overall_readiness = round(min(overall, 100.0), 1)
    db.commit()
    return {"message": "Placement progress updated", "overall_readiness": prog.overall_readiness}


@placement_router.post("/skills")
async def add_skill(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    st = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Student profile not found")
    sk = StudentSkill(
        student_id=st.id,
        skill_name=payload["skill_name"],
        proficiency_level=int(payload.get("proficiency_level", 3)),
        category=payload.get("category", "technical"),
    )
    db.add(sk)
    db.commit()
    db.refresh(sk)
    return {"id": sk.id, "skill_name": sk.skill_name, "proficiency_level": sk.proficiency_level}


@placement_router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sk = db.query(StudentSkill).filter(StudentSkill.id == skill_id).first()
    if sk:
        db.delete(sk)
        db.commit()
    return {"message": "Skill removed"}


# ─────────────────────────── Grading Rules ───────────────────────────
grading_router = APIRouter()


@grading_router.get("")
async def list_grading_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rules = db.query(GradingRule).order_by(GradingRule.min_percentage.desc()).all()
    return [{"id": r.id, "grade": r.grade, "min_percentage": r.min_percentage,
             "max_percentage": r.max_percentage, "grade_points": r.grade_points, "is_pass": r.is_pass} for r in rules]


@grading_router.post("")
async def upsert_grading_rule(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    rule = GradingRule(
        grade=payload["grade"],
        min_percentage=float(payload["min_percentage"]),
        max_percentage=float(payload["max_percentage"]),
        grade_points=float(payload["grade_points"]),
        is_pass=bool(payload.get("is_pass", True)),
    )
    db.add(rule)
    db.commit()
    return {"message": "Grading rule added", "id": rule.id}


@grading_router.delete("/{rule_id}")
async def delete_grading_rule(rule_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    rule = db.query(GradingRule).filter(GradingRule.id == rule_id).first()
    if rule:
        db.delete(rule)
        db.commit()
    return {"message": "Deleted"}


# ─────────────────────────── CSV / Excel Bulk Import ───────────────────────────
import_router = APIRouter()

REQUIRED_COLUMNS = {
    "students": ["full_name", "email", "student_id", "roll_number", "department_code"],
    "marks": ["student_id", "subject_code", "semester_number", "internal_marks", "external_marks"],
}


def _parse_upload(file_bytes: bytes, filename: str) -> List[dict]:
    ext = filename.lower().split(".")[-1]
    if ext == "csv":
        text = file_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        return [dict(r) for r in reader]
    elif ext in ("xlsx", "xls"):
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(file_bytes), read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [str(h).strip() if h is not None else "" for h in rows[0]]
        return [dict(zip(headers, r)) for r in rows[1:] if any(r)]
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .csv or .xlsx")


@import_router.post("/preview")
async def preview_import(
    entity_type: str = Query(..., pattern="^(students|marks)$"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    raw = await file.read()
    rows = _parse_upload(raw, file.filename)
    if not rows:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    required = REQUIRED_COLUMNS[entity_type]
    columns = list(rows[0].keys())
    missing_cols = [c for c in required if c not in columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing_cols)}")

    row_errors = []
    duplicates = []
    valid_rows = []

    for idx, row in enumerate(rows, start=1):
        errs = []
        for col in required:
            if row.get(col) is None or str(row.get(col)).strip() == "":
                errs.append(f"Missing {col}")

        if entity_type == "students" and not errs:
            if db.query(Student).filter(Student.student_id == str(row["student_id"])).first():
                duplicates.append({"row": idx, "reason": f"Student ID {row['student_id']} already exists"})
                continue
            if db.query(User).filter(User.email == str(row["email"])).first():
                duplicates.append({"row": idx, "reason": f"Email {row['email']} already exists"})
                continue

        if errs:
            row_errors.append({"row": idx, "errors": errs})
        else:
            valid_rows.append(row)

    return {
        "entity_type": entity_type,
        "total_rows": len(rows),
        "valid_count": len(valid_rows),
        "duplicate_count": len(duplicates),
        "error_count": len(row_errors),
        "duplicates": duplicates[:20],
        "errors": row_errors[:20],
        "preview_rows": valid_rows[:20],
        "valid_rows": valid_rows,
    }


@import_router.post("/confirm")
async def confirm_import(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    entity_type = payload.get("entity_type")
    rows = payload.get("rows", [])
    imported = 0
    skipped = 0

    if entity_type == "students":
        depts = {d.code: d.id for d in db.query(Department).all()}
        for r in rows:
            if db.query(User).filter(User.email == str(r["email"])).first():
                skipped += 1
                continue
            dept_id = depts.get(str(r.get("department_code", "CSE")).upper(), 1)
            u = User(
                email=str(r["email"]),
                hashed_password=get_password_hash("Student@123"),
                full_name=str(r["full_name"]),
                role="student",
            )
            db.add(u)
            db.flush()
            db.add(Student(
                user_id=u.id,
                student_id=str(r["student_id"]),
                roll_number=str(r["roll_number"]),
                department_id=dept_id,
                current_semester=int(r.get("current_semester", 1)),
                admission_year=int(r.get("admission_year", 2024)),
            ))
            imported += 1
        db.commit()

    elif entity_type == "marks":
        subjects = {s.code: s for s in db.query(Subject).all()}
        students = {s.student_id: s.id for s in db.query(Student).all()}
        sems = {s.number: s.id for s in db.query(Semester).all()}
        for r in rows:
            st_id = students.get(str(r["student_id"]))
            subj = subjects.get(str(r["subject_code"]))
            sem_id = sems.get(int(r["semester_number"]), 1)
            if not st_id or not subj:
                skipped += 1
                continue
            existing = db.query(Marks).filter(
                Marks.student_id == st_id, Marks.subject_id == subj.id, Marks.semester_id == sem_id
            ).first()
            if existing:
                skipped += 1  # Never silently overwrite
                continue
            internal = float(r["internal_marks"])
            external = float(r["external_marks"])
            calc = calculate_marks(internal, external, subj.id, db, sem_id)
            db.add(Marks(
                student_id=st_id, subject_id=subj.id, semester_id=sem_id,
                internal_marks=internal, external_marks=external, **calc
            ))
            imported += 1
        db.commit()

    db.add(AuditLog(user_id=current_user.id, action=f"bulk_import_{entity_type}", details={"imported": imported, "skipped": skipped}))
    db.commit()
    return {"imported": imported, "skipped": skipped}


# ─────────────────────────── Advanced Analytics & Charts ───────────────────────────
ext_analytics_router = APIRouter()


@ext_analytics_router.get("/stats")
async def descriptive_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return compute_descriptive_analytics(db)


@ext_analytics_router.get("/charts")
async def seaborn_charts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"charts": generate_seaborn_charts(db)}


# ─────────────────────────── Downloadable PDF & Excel Reports ───────────────────────────
ext_reports_router = APIRouter()


@ext_reports_router.get("/download/{report_type}")
async def download_report(
    report_type: str,
    format: str = Query("pdf", pattern="^(pdf|excel)$"),
    student_id: Optional[int] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    headers = []
    rows = []
    summary = {}
    title = "Academic Report"
    subtitle = "EduTrack AI Institutional Report"

    if report_type == "student" and student_id:
        st = db.query(Student).filter(Student.id == student_id).first()
        if not st:
            raise HTTPException(status_code=404, detail="Student not found")
        if current_user.role == "student" and st.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        title = f"Student Report - {st.user.full_name if st.user else st.student_id}"
        subtitle = f"ID: {st.student_id} | Roll: {st.roll_number} | Sem: {st.current_semester}"
        marks = db.query(Marks).filter(Marks.student_id == student_id).all()
        sems = db.query(StudentSemester).filter(StudentSemester.student_id == student_id).all()
        summary = {
            "Student Name": st.user.full_name if st.user else "",
            "CGPA": sems[-1].cgpa if sems else 0,
            "Subjects Evaluated": len(marks),
            "Passed": sum(1 for m in marks if m.is_pass),
        }
        headers = ["Subject ID", "Internal", "External", "Total", "Percentage", "Grade", "Status"]
        rows = [[m.subject_id, m.internal_marks, m.external_marks, m.total_marks, f"{m.percentage}%", m.grade, "Pass" if m.is_pass else "Fail"] for m in marks]

    elif report_type == "risk":
        if current_user.role == "student":
            raise HTTPException(status_code=403, detail="Access denied")
        title = "Academic Risk & Early Warning Report"
        alerts = db.query(AcademicAlert).filter(AcademicAlert.is_resolved == False).all()
        summary = {
            "Total Active Alerts": len(alerts),
            "High Risk": sum(1 for a in alerts if a.risk_level == "high"),
            "Moderate Risk": sum(1 for a in alerts if a.risk_level == "moderate"),
        }
        headers = ["Student ID", "Name", "Risk Level", "Risk Score", "Primary Reason"]
        for a in alerts:
            st = db.query(Student).filter(Student.id == a.student_id).first()
            rows.append([
                st.student_id if st else a.student_id,
                st.user.full_name if st and st.user else "",
                str(a.risk_level).upper(),
                a.risk_score,
                (a.reasons[0] if a.reasons else "N/A")[:45]
            ])

    elif report_type == "attendance":
        title = "Attendance Summary Report"
        students = db.query(Student).limit(100).all()
        headers = ["Student ID", "Name", "Total Classes", "Present", "Attendance %"]
        for st in students:
            att = db.query(Attendance).filter(Attendance.student_id == st.id).all()
            tot = len(att)
            pres = sum(1 for a in att if a.is_present)
            pct = round(pres / tot * 100, 1) if tot > 0 else 0
            rows.append([st.student_id, st.user.full_name if st.user else "", tot, pres, f"{pct}%"])
        summary = {"Students Included": len(rows)}

    else:  # college / department / semester
        title = "College Academic Analytics Report"
        students = db.query(Student).all()
        if department_id:
            students = [s for s in students if s.department_id == department_id]
        sems = db.query(StudentSemester).all()
        latest = {}
        for ss in sems:
            if ss.student_id not in latest or ss.id > latest[ss.student_id].id:
                latest[ss.student_id] = ss
        summary = {
            "Total Students": len(students),
            "Average CGPA": round(sum(s.cgpa for s in latest.values()) / max(len(latest), 1), 2),
        }
        headers = ["Student ID", "Name", "Semester", "CGPA", "Backlogs"]
        for st in students[:100]:
            ss = latest.get(st.id)
            rows.append([st.student_id, st.user.full_name if st.user else "", st.current_semester, ss.cgpa if ss else 0, ss.backlogs if ss else 0])

    if format == "pdf":
        pdf_bytes = generate_pdf_report(title, subtitle, summary, headers, rows)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=edutrack_{report_type}_report.pdf"}
        )
    else:
        xlsx_bytes = generate_excel_report(title, headers, rows)
        return StreamingResponse(
            io.BytesIO(xlsx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=edutrack_{report_type}_report.xlsx"}
        )


# ─────────────────────────── Audit Logs ───────────────────────────
audit_router = APIRouter()


@audit_router.get("")
async def list_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(100).all()
    return [{"id": l.id, "user_id": l.user_id, "action": l.action, "resource": l.resource,
             "details": l.details, "created_at": str(l.created_at) if l.created_at else None} for l in logs]
