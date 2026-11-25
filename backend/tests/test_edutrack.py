"""
Comprehensive Automated Test Suite - EduTrack AI
Tests:
- Authentication & JWT
- Role-based Access Control
- Student CRUD
- Attendance Calculations
- Marks & CGPA Calculations
- Analytics & Risk Classification
- ML Predictions
- Study Planner
- PDF & Excel Report Generation
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db
from app.core.security import get_password_hash
from app.models import User, Department, Semester, Teacher, Student, Subject, GradingRule

SQLALCHEMY_TEST_URL = "sqlite:///./test_edutrack.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed grading rules
    db.add_all([
        GradingRule(grade="O", min_percentage=90, max_percentage=100, grade_points=10, is_pass=True),
        GradingRule(grade="A", min_percentage=70, max_percentage=89.99, grade_points=8, is_pass=True),
        GradingRule(grade="B", min_percentage=50, max_percentage=69.99, grade_points=6, is_pass=True),
        GradingRule(grade="F", min_percentage=0, max_percentage=49.99, grade_points=0, is_pass=False),
    ])

    dept = Department(name="Computer Science", code="CSE", hod_name="Dr. Test")
    db.add(dept)
    db.flush()

    sem = Semester(number=1, name="Semester 1", academic_year="2024-25", is_current=True)
    db.add(sem)
    db.flush()

    # Admin
    admin_u = User(email="admin@test.ai", hashed_password=get_password_hash("Admin@123"), full_name="Admin User", role="admin")
    # Teacher
    teacher_u = User(email="teacher@test.ai", hashed_password=get_password_hash("Teacher@123"), full_name="Teacher User", role="teacher")
    # Student
    student_u = User(email="student@test.ai", hashed_password=get_password_hash("Student@123"), full_name="Student User", role="student")
    db.add_all([admin_u, teacher_u, student_u])
    db.flush()

    teacher = Teacher(user_id=teacher_u.id, teacher_id="TCH001", department_id=dept.id)
    student = Student(user_id=student_u.id, student_id="CSE2024001", roll_number="CSE/2024/001", department_id=dept.id, current_semester=1, admission_year=2024)
    db.add_all([teacher, student])
    db.flush()

    subj = Subject(name="Data Structures", code="CSE101", department_id=dept.id, semester_id=sem.id, teacher_id=teacher.id, credits=4, max_internal=30, max_external=70, max_total=100)
    db.add(subj)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_edutrack.db"):
        os.remove("./test_edutrack.db")


client = TestClient(app)


def get_token(email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_auth_login_and_me():
    token = get_token("admin@test.ai", "Admin@123")
    normalized_email_login = client.post(
        "/api/auth/login",
        json={"email": " ADMIN@TEST.AI ", "password": "Admin@123"}
    )
    assert normalized_email_login.status_code == 200
    assert normalized_email_login.json()["user"]["role"] == "admin"
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "admin"

    bad = client.post("/api/auth/login", json={"email": "admin@test.ai", "password": "wrong"})
    assert bad.status_code == 401


def test_role_permissions():
    student_token = get_token("student@test.ai", "Student@123")
    # Student cannot list all students or create student
    res = client.get("/api/students", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403

    res2 = client.post("/api/departments", json={"name": "IT", "code": "IT"}, headers={"Authorization": f"Bearer {student_token}"})
    assert res2.status_code == 403


def test_student_crud():
    admin_token = get_token("admin@test.ai", "Admin@123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create
    res = client.post("/api/students", json={
        "email": "newstudent@test.ai",
        "password": "Student@123",
        "full_name": "New Student",
        "student_id": "CSE2024002",
        "roll_number": "CSE/2024/002",
        "department_id": 1,
        "current_semester": 1,
        "admission_year": 2024
    }, headers=headers)
    assert res.status_code == 200
    sid = res.json()["id"]

    # Read
    get_res = client.get(f"/api/students/{sid}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["student_id"] == "CSE2024002"

    # Update
    upd_res = client.put(f"/api/students/{sid}", json={"current_semester": 2}, headers=headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["current_semester"] == 2

    # Delete (deactivate)
    del_res = client.delete(f"/api/students/{sid}", headers=headers)
    assert del_res.status_code == 200


def test_attendance_calculations():
    teacher_token = get_token("teacher@test.ai", "Teacher@123")
    headers = {"Authorization": f"Bearer {teacher_token}"}

    # Record 3 present, 1 absent => 75%
    dates = ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]
    for idx, d in enumerate(dates):
        res = client.post("/api/attendance", json={
            "student_id": 1, "subject_id": 1, "date": d, "is_present": idx < 3
        }, headers=headers)
        assert res.status_code == 200

    summary = client.get("/api/attendance/student/1", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["overall_attendance"] == 75.0


def test_marks_and_cgpa_calculations():
    teacher_token = get_token("teacher@test.ai", "Teacher@123")
    headers = {"Authorization": f"Bearer {teacher_token}"}

    res = client.post("/api/marks", json={
        "student_id": 1, "subject_id": 1, "semester_id": 1,
        "internal_marks": 25, "external_marks": 55
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()["marks"]
    assert data["total"] == 80.0
    assert data["percentage"] == 80.0
    assert data["grade"] == "A"
    assert data["grade_points"] == 8.0
    assert data["is_pass"] is True

    # Check academic summary CGPA
    sum_res = client.get("/api/students/1/academic-summary", headers=headers)
    assert sum_res.status_code == 200
    assert sum_res.json()["current_cgpa"] == 8.0


def test_analytics_and_risk():
    admin_token = get_token("admin@test.ai", "Admin@123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    ov = client.get("/api/analytics/overview", headers=headers)
    assert ov.status_code == 200
    assert ov.json()["total_students"] >= 1

    st = client.get("/api/analytics/stats", headers=headers)
    assert st.status_code == 200
    assert "stats" in st.json()


def test_ml_prediction():
    token = get_token("student@test.ai", "Student@123")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/ml/predict", json={
        "attendance": 85, "previous_cgpa": 8.0, "avg_internal_percentage": 80
    }, headers=headers)
    assert res.status_code == 200
    assert res.json()["prediction"] in ["Pass", "Needs Improvement"]


def test_study_planner_and_goals():
    token = get_token("student@test.ai", "Student@123")
    headers = {"Authorization": f"Bearer {token}"}

    plan_res = client.post("/api/study-plans/generate", json={
        "weak_subjects": ["Data Structures", "Algorithms"],
        "daily_hours": 4,
        "study_days": ["Monday", "Wednesday", "Friday"]
    }, headers=headers)
    assert plan_res.status_code == 200
    assert plan_res.json()["saved"] is True

    goal_res = client.post("/api/goals", json={
        "title": "Achieve 8.5 CGPA", "goal_type": "cgpa", "target_value": 8.5
    }, headers=headers)
    assert goal_res.status_code == 200


def test_reports_generation():
    admin_token = get_token("admin@test.ai", "Admin@123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    pdf_res = client.get("/api/reports/download/college?format=pdf", headers=headers)
    assert pdf_res.status_code == 200

    xlsx_res = client.get("/api/reports/download/college?format=excel", headers=headers)
    assert xlsx_res.status_code == 200
