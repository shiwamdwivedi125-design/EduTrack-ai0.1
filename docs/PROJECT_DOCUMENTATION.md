# EduTrack AI - Project Documentation

## 1. Introduction

EduTrack AI is a college academic performance and early-warning platform designed to support data-informed academic decisions. It gives administrators, teachers and students separate views of academic activity.

## 2. Problem Statement

Manual academic tracking makes it difficult to identify low attendance, weak subjects and declining performance early enough for intervention. EduTrack AI centralizes records and presents explainable risk indicators and academic reports.

## 3. Objectives

- Manage users and academic master data
- Record attendance and marks
- Calculate percentages and credit-based academic summaries
- Configure grading rules
- Identify students who may need support
- Plan study activities and placement readiness
- Generate PDF and Excel reports
- Protect each role's data and operations

## 4. Existing System and Proposed System

The existing system may rely on separate spreadsheets or manual registers. The proposed system provides a single database-backed application with role-based dashboards, validation, analytics and exports.

## 5. Module Description

### Authentication

The backend verifies bcrypt password hashes and issues signed JWT access tokens. Endpoint dependencies enforce administrator, teacher and student permissions.

### Student Management

Administrators can create, view, update and deactivate students. Student accounts are linked to department, semester and profile records.

### Attendance

Attendance supports daily subject entries and student summaries. Present/absent records are used to calculate percentages.

### Marks and Grading

Marks combine internal and external components. The configurable grading table maps percentage ranges to grades and grade points.

### Early Warning

Risk calculation considers attendance, CGPA, marks and repeated failures where available. Low, moderate and high categories are decision-support indicators.

### Study Planner

The planner distributes available study time across weak subjects and selected weekdays. It works locally without an external API key.

### Placement Readiness

CGPA, technical skills, projects, aptitude, certifications and interview preparation contribute to an indicative readiness score.

### Reports and Imports

ReportLab creates PDF responses and OpenPyXL creates Excel responses. CSV/Excel workflows validate and preview records before confirmation.

## 6. Database Design

Primary entities include users, students, teachers, departments, subjects, semesters, attendance, marks, grading rules, student semester performance, alerts, interventions, study plans, goals, notifications, audit logs, skills and placement progress.

Each entity uses primary keys and appropriate foreign keys, uniqueness constraints and timestamps.

## 7. Security

- bcrypt password hashing
- JWT access tokens
- FastAPI role dependencies
- SQLAlchemy parameterized queries
- CORS allowlists
- Upload size and type validation
- Audit and login event records

## 8. Testing

The automated suite covers:

- Health endpoint
- Login and authenticated identity
- Role restrictions
- Student CRUD
- Attendance percentages
- Marks and CGPA
- Analytics
- ML prediction
- Study plans and goals
- PDF and Excel report responses

Run:

```powershell
python -m pytest backend/tests/test_edutrack.py -q
```

## 9. Deployment

Use Docker Compose for a local PostgreSQL demonstration or configure a hosted PostgreSQL database. Set a strong `SECRET_KEY`, production CORS origins and a production `DATABASE_URL`.

```powershell
docker compose up --build
```

## 10. Future Scope

- Formal Alembic migration history
- Real assignment and LMS integrations
- Stronger ML training datasets
- Notification email/SMS delivery
- Rate limiting and two-factor authentication
- Mobile application
- Formal user privacy and retention policies
