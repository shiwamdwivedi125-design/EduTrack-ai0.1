"""
Pydantic Schemas for EduTrack AI
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import datetime, date


# ─────────────────────────── Auth ───────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Department ───────────────────────────
class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    hod_name: Optional[str] = None


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    hod_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# ─────────────────────────── Semester ───────────────────────────
class SemesterCreate(BaseModel):
    number: int
    name: str
    academic_year: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False


class SemesterOut(BaseModel):
    id: int
    number: int
    name: str
    academic_year: str
    is_current: bool

    class Config:
        from_attributes = True


# ─────────────────────────── Student ───────────────────────────
class StudentCreate(BaseModel):
    email: str
    password: str
    full_name: str
    student_id: str
    roll_number: str
    department_id: int
    branch: Optional[str] = None
    current_semester: int = 1
    admission_year: int
    academic_session: Optional[str] = None
    phone: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    student_id: str
    roll_number: str
    branch: Optional[str] = None
    current_semester: int
    admission_year: int
    academic_session: Optional[str] = None
    is_active: bool
    user: Optional[UserOut] = None
    department: Optional[DepartmentOut] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Teacher ───────────────────────────
class TeacherCreate(BaseModel):
    email: str
    password: str
    full_name: str
    teacher_id: str
    department_id: int
    designation: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None


class TeacherOut(BaseModel):
    id: int
    teacher_id: str
    designation: Optional[str] = None
    specialization: Optional[str] = None
    is_active: bool
    user: Optional[UserOut] = None
    department: Optional[DepartmentOut] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Subject ───────────────────────────
class SubjectCreate(BaseModel):
    name: str
    code: str
    department_id: int
    semester_id: int
    teacher_id: Optional[int] = None
    credits: int = 4
    max_internal: float = 30
    max_external: float = 70
    max_total: float = 100


class SubjectOut(BaseModel):
    id: int
    name: str
    code: str
    credits: int
    max_internal: float
    max_external: float
    max_total: float
    is_active: bool
    department: Optional[DepartmentOut] = None
    semester: Optional[SemesterOut] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Attendance ───────────────────────────
class AttendanceCreate(BaseModel):
    student_id: int
    subject_id: int
    date: date
    is_present: bool = True
    total_classes: int = 0
    present_classes: int = 0


class AttendanceBulkCreate(BaseModel):
    records: List[AttendanceCreate]


class AttendanceOut(BaseModel):
    id: int
    student_id: int
    subject_id: int
    date: date
    is_present: bool
    total_classes: int
    present_classes: int

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    student_id: int
    subject_id: int
    subject_name: str
    total_classes: int
    present_classes: int
    attendance_percentage: float
    status: str  # ok, warning, critical


# ─────────────────────────── Marks ───────────────────────────
class MarksCreate(BaseModel):
    student_id: int
    subject_id: int
    semester_id: int
    internal_marks: float
    external_marks: float


class MarksBulkCreate(BaseModel):
    records: List[MarksCreate]


class MarksOut(BaseModel):
    id: int
    student_id: int
    subject_id: int
    semester_id: int
    internal_marks: float
    external_marks: float
    total_marks: float
    max_marks: float
    percentage: float
    grade: Optional[str] = None
    grade_points: float
    credits: int
    is_pass: bool
    subject: Optional[SubjectOut] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Academic Alert ───────────────────────────
class AlertOut(BaseModel):
    id: int
    student_id: int
    risk_level: str
    risk_score: float
    reasons: List[str]
    recommendations: List[str]
    is_resolved: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Study Plan ───────────────────────────
class StudyPlanRequest(BaseModel):
    weak_subjects: List[str]
    daily_hours: float = 4
    study_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    exam_date: Optional[date] = None
    target_cgpa: Optional[float] = None


class StudyPlanOut(BaseModel):
    id: int
    title: str
    weak_subjects: List[str]
    daily_hours: float
    study_days: List[str]
    plan_data: dict
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Goals ───────────────────────────
class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    goal_type: str = "cgpa"
    deadline: Optional[date] = None


class GoalOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    current_value: float
    goal_type: str
    deadline: Optional[date] = None
    is_completed: bool
    badge_earned: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─────────────────────────── Analytics ───────────────────────────
class OverviewStats(BaseModel):
    total_students: int
    active_students: int
    total_teachers: int
    total_departments: int
    average_cgpa: float
    average_attendance: float
    students_needing_support: int
    high_risk_students: int


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
