"""FastAPI Router modules"""
from fastapi import APIRouter
from app.api.endpoints._other import (
    users_router,
    teachers_router, 
    depts_router,
    subjects_router,
    semesters_router,
    notif_router,
    alerts_router,
    reports_router,
)

class _RouterWrapper:
    def __init__(self, r): self.router = r

users = _RouterWrapper(users_router)
teachers = _RouterWrapper(teachers_router)
departments = _RouterWrapper(depts_router)
subjects = _RouterWrapper(subjects_router)
semesters = _RouterWrapper(semesters_router)
notifications = _RouterWrapper(notif_router)
alerts = _RouterWrapper(alerts_router)
reports = _RouterWrapper(reports_router)
