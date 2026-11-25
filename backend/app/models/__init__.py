"""
SQLAlchemy Database Models - EduTrack AI
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Enum, JSON, Date, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class RiskLevel(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


# ─────────────────────────── Users ───────────────────────────
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


# ─────────────────────────── Departments ───────────────────────────
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    hod_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="department")
    teachers = relationship("Teacher", back_populates="department")
    subjects = relationship("Subject", back_populates="department")


# ─────────────────────────── Semesters ───────────────────────────
class Semester(Base):
    __tablename__ = "semesters"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    academic_year = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("number", "academic_year", name="uq_semester_year"),)

    subjects = relationship("Subject", back_populates="semester")
    student_semesters = relationship("StudentSemester", back_populates="semester")


# ─────────────────────────── Students ───────────────────────────
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    roll_number = Column(String(50), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    branch = Column(String(100), nullable=True)
    current_semester = Column(Integer, default=1)
    admission_year = Column(Integer, nullable=False)
    academic_session = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    guardian_name = Column(String(255), nullable=True)
    guardian_phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="student_profile")
    department = relationship("Department", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")
    marks_records = relationship("Marks", back_populates="student")
    academic_alerts = relationship("AcademicAlert", back_populates="student")
    interventions = relationship("Intervention", back_populates="student")
    study_plans = relationship("StudyPlan", back_populates="student")
    goals = relationship("StudyGoal", back_populates="student")
    student_semesters = relationship("StudentSemester", back_populates="student")
    skills = relationship("StudentSkill", back_populates="student")
    placement = relationship("PlacementProgress", back_populates="student", uselist=False)


# ─────────────────────────── Teachers ───────────────────────────
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    teacher_id = Column(String(50), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation = Column(String(100), nullable=True)
    specialization = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="teacher_profile")
    department = relationship("Department", back_populates="teachers")
    subjects = relationship("Subject", back_populates="teacher")
    interventions = relationship("Intervention", back_populates="teacher")


# ─────────────────────────── Subjects ───────────────────────────
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    credits = Column(Integer, default=4)
    max_internal = Column(Float, default=30)
    max_external = Column(Float, default=70)
    max_total = Column(Float, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    department = relationship("Department", back_populates="subjects")
    semester = relationship("Semester", back_populates="subjects")
    teacher = relationship("Teacher", back_populates="subjects")
    attendance_records = relationship("Attendance", back_populates="subject")
    marks_records = relationship("Marks", back_populates="subject")


# ─────────────────────────── Attendance ───────────────────────────
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_present = Column(Boolean, default=True)
    total_classes = Column(Integer, default=0)
    present_classes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "date", name="uq_attendance"),
        Index("idx_attendance_student", "student_id"),
        Index("idx_attendance_subject", "subject_id"),
    )

    student = relationship("Student", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")


# ─────────────────────────── Marks ───────────────────────────
class Marks(Base):
    __tablename__ = "marks"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    internal_marks = Column(Float, default=0)
    external_marks = Column(Float, default=0)
    total_marks = Column(Float, default=0)
    max_marks = Column(Float, default=100)
    percentage = Column(Float, default=0)
    grade = Column(String(5), nullable=True)
    grade_points = Column(Float, default=0)
    credits = Column(Integer, default=4)
    is_pass = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "semester_id", name="uq_marks"),
        Index("idx_marks_student", "student_id"),
    )

    student = relationship("Student", back_populates="marks_records")
    subject = relationship("Subject", back_populates="marks_records")
    semester = relationship("Semester")


# ─────────────────────────── Grading Rules ───────────────────────────
class GradingRule(Base):
    __tablename__ = "grading_rules"
    id = Column(Integer, primary_key=True, index=True)
    grade = Column(String(5), nullable=False)
    min_percentage = Column(Float, nullable=False)
    max_percentage = Column(Float, nullable=False)
    grade_points = Column(Float, nullable=False)
    description = Column(String(100), nullable=True)
    is_pass = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────── Student Semester CGPA ───────────────────────────
class StudentSemester(Base):
    __tablename__ = "student_semesters"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    sgpa = Column(Float, default=0)
    cgpa = Column(Float, default=0)
    total_credits = Column(Integer, default=0)
    earned_credits = Column(Integer, default=0)
    backlogs = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("student_id", "semester_id", name="uq_student_semester"),)

    student = relationship("Student", back_populates="student_semesters")
    semester = relationship("Semester", back_populates="student_semesters")


# ─────────────────────────── Academic Alerts ───────────────────────────
class AcademicAlert(Base):
    __tablename__ = "academic_alerts"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_score = Column(Float, default=0)
    reasons = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="academic_alerts")


# ─────────────────────────── Interventions ───────────────────────────
class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    follow_up_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="interventions")
    teacher = relationship("Teacher", back_populates="interventions")


# ─────────────────────────── Study Plans ───────────────────────────
class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String(255), nullable=False)
    weak_subjects = Column(JSON, default=list)
    daily_hours = Column(Float, default=4)
    study_days = Column(JSON, default=list)
    exam_date = Column(Date, nullable=True)
    plan_data = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="study_plans")


# ─────────────────────────── Goals ───────────────────────────
class StudyGoal(Base):
    __tablename__ = "study_goals"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0)
    goal_type = Column(String(50), default="cgpa")
    deadline = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    badge_earned = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="goals")


# ─────────────────────────── Notifications ───────────────────────────
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


# ─────────────────────────── Audit Logs ───────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")


# ─────────────────────────── Student Skills ───────────────────────────
class StudentSkill(Base):
    __tablename__ = "student_skills"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(Integer, default=1)  # 1-5
    category = Column(String(50), default="technical")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="skills")


# ─────────────────────────── Placement Progress ───────────────────────────
class PlacementProgress(Base):
    __tablename__ = "placement_progress"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True)
    cgpa_score = Column(Float, default=0)
    technical_score = Column(Float, default=0)
    aptitude_score = Column(Float, default=0)
    projects_count = Column(Integer, default=0)
    internships_count = Column(Integer, default=0)
    certifications_count = Column(Integer, default=0)
    mock_interviews = Column(Integer, default=0)
    overall_readiness = Column(Float, default=0)
    target_companies = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    student = relationship("Student", back_populates="placement")
