"""
FastAPI Main Application - EduTrack AI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.config import settings

app = FastAPI(
    title="EduTrack AI API",
    description="Student Academic Performance & Early Warning System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register all routers
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.students import router as students_router
from app.api.endpoints.attendance import router as attendance_router
from app.api.endpoints.marks import router as marks_router
from app.api.endpoints.analytics import router as analytics_router
from app.api.endpoints.ml_predict import router as ml_router
from app.api.endpoints.study_planner import router as study_router
from app.api.endpoints.goals import router as goals_router
from app.api.endpoints._other import (
    users_router, teachers_router, depts_router,
    subjects_router, semesters_router, notif_router,
    alerts_router, reports_router
)
from app.api.endpoints.extended import (
    interventions_router, placement_router, grading_router,
    import_router, ext_analytics_router, ext_reports_router,
    audit_router
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(students_router, prefix="/api/students", tags=["Students"])
app.include_router(teachers_router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(depts_router, prefix="/api/departments", tags=["Departments"])
app.include_router(subjects_router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(semesters_router, prefix="/api/semesters", tags=["Semesters"])
app.include_router(attendance_router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(marks_router, prefix="/api/marks", tags=["Marks"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ext_analytics_router, prefix="/api/analytics", tags=["Advanced Analytics"])
app.include_router(ml_router, prefix="/api/ml", tags=["Machine Learning"])
app.include_router(study_router, prefix="/api/study-plans", tags=["Study Planner"])
app.include_router(goals_router, prefix="/api/goals", tags=["Goals"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(ext_reports_router, prefix="/api/reports", tags=["Report Downloads"])
app.include_router(notif_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["Academic Alerts"])
app.include_router(interventions_router, prefix="/api/interventions", tags=["Interventions"])
app.include_router(placement_router, prefix="/api/placement", tags=["Placement Readiness"])
app.include_router(grading_router, prefix="/api/grading-rules", tags=["Grading Rules"])
app.include_router(import_router, prefix="/api/import", tags=["CSV & Excel Import"])
app.include_router(audit_router, prefix="/api/audit-logs", tags=["Audit Logs"])

# Static files
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
try:
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
except Exception:
    pass


@app.get("/", tags=["Health"])
async def root():
    return {"message": "EduTrack AI API is running", "version": "1.0.0", "docs": "/api/docs"}


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.on_event("startup")
async def startup_event():
    from app.database.session import create_tables
    create_tables()
    print("[EduTrack AI] Database tables initialized")
