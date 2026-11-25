"""
Database Seeder - Seeds initial data into EduTrack AI database
Run: python scripts/seed.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database.session import SessionLocal, create_tables
from app.models import (
    User, Department, Semester, Teacher, Student, Subject,
    Marks, Attendance, GradingRule, StudentSemester, AcademicAlert,
    PlacementProgress, Notification
)
from app.core.security import get_password_hash
from app.services.academic import calculate_grade, compute_risk_score
import random
import sys
import os

# Import data generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from generate_data import generate_all_data, SUBJECTS_BY_DEPT, DEPARTMENTS

random.seed(42)


def seed_grading_rules(db):
    """Seed default grading rules (10-point scale)"""
    rules = [
        {"grade": "O",  "min_percentage": 90.0, "max_percentage": 100.0, "grade_points": 10.0, "is_pass": True},
        {"grade": "A+", "min_percentage": 80.0, "max_percentage": 89.99, "grade_points": 9.0, "is_pass": True},
        {"grade": "A",  "min_percentage": 70.0, "max_percentage": 79.99, "grade_points": 8.0, "is_pass": True},
        {"grade": "B+", "min_percentage": 60.0, "max_percentage": 69.99, "grade_points": 7.0, "is_pass": True},
        {"grade": "B",  "min_percentage": 50.0, "max_percentage": 59.99, "grade_points": 6.0, "is_pass": True},
        {"grade": "C",  "min_percentage": 40.0, "max_percentage": 49.99, "grade_points": 5.0, "is_pass": True},
        {"grade": "F",  "min_percentage": 0.0,  "max_percentage": 39.99, "grade_points": 0.0, "is_pass": False},
    ]
    for r in rules:
        existing = db.query(GradingRule).filter(GradingRule.grade == r["grade"]).first()
        if not existing:
            db.add(GradingRule(**r))
    db.commit()
    print("  [OK] Grading rules seeded")


def seed_departments(db):
    """Seed departments"""
    dept_map = {}
    for d in DEPARTMENTS:
        existing = db.query(Department).filter(Department.code == d["code"]).first()
        if not existing:
            dept = Department(name=d["name"], code=d["code"], hod_name=d["hod"])
            db.add(dept)
            db.flush()
            dept_map[d["code"]] = dept.id
        else:
            dept_map[d["code"]] = existing.id
    db.commit()
    print(f"  [OK] {len(dept_map)} departments seeded")
    return dept_map


def seed_semesters(db):
    """Seed 8 semesters"""
    sem_map = {}
    for num in range(1, 9):
        existing = db.query(Semester).filter(Semester.number == num, Semester.academic_year == "2024-25").first()
        if not existing:
            sem = Semester(
                number=num,
                name=f"Semester {num}",
                academic_year="2024-25",
                is_current=(num == 3)
            )
            db.add(sem)
            db.flush()
            sem_map[num] = sem.id
        else:
            sem_map[num] = existing.id
    db.commit()
    print(f"  [OK] {len(sem_map)} semesters seeded")
    return sem_map


def seed_admin(db):
    """Seed admin user"""
    existing = db.query(User).filter(User.email == "admin@edutrack.ai").first()
    if not existing:
        admin = User(
            email="admin@edutrack.ai",
            hashed_password=get_password_hash("Admin@123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("  [OK] Admin user seeded -> admin@edutrack.ai / Admin@123")
    else:
        print("  [OK] Admin already exists")


def seed_teachers(db, dept_map):
    """Seed teacher accounts"""
    teachers_data = [
        {"name": "Dr. Ramesh Kumar",    "email": "ramesh.kumar@edutrack.ai",   "dept": "CSE", "desig": "Professor",             "spec": "Algorithms"},
        {"name": "Prof. Anita Singh",   "email": "anita.singh@edutrack.ai",    "dept": "CSE", "desig": "Associate Professor",    "spec": "DBMS"},
        {"name": "Dr. Priya Sharma",    "email": "priya.sharma@edutrack.ai",   "dept": "ECE", "desig": "Professor",             "spec": "VLSI"},
        {"name": "Prof. Suresh Patel",  "email": "suresh.patel@edutrack.ai",   "dept": "ECE", "desig": "Assistant Professor",   "spec": "DSP"},
        {"name": "Dr. Suresh Kumar",    "email": "suresh.kumar@edutrack.ai",   "dept": "MECH","desig": "Professor",             "spec": "Thermodynamics"},
        {"name": "Prof. Kavita Rao",    "email": "kavita.rao@edutrack.ai",     "dept": "MECH","desig": "Associate Professor",   "spec": "Machine Design"},
        {"name": "Dr. Arun Mehta",      "email": "arun.mehta@edutrack.ai",     "dept": "CSE", "desig": "Assistant Professor",  "spec": "AI & ML"},
        {"name": "Prof. Deepa Nair",    "email": "deepa.nair@edutrack.ai",     "dept": "ECE", "desig": "Assistant Professor",  "spec": "Communications"},
    ]
    teacher_map = {}  # teacher_id -> dept_code
    for idx, t in enumerate(teachers_data, start=1):
        existing = db.query(User).filter(User.email == t["email"]).first()
        if not existing:
            user = User(
                email=t["email"],
                hashed_password=get_password_hash("Teacher@123"),
                full_name=t["name"],
                role="teacher",
                is_active=True
            )
            db.add(user)
            db.flush()
            teacher = Teacher(
                user_id=user.id,
                teacher_id=f"TCH{str(idx).zfill(3)}",
                department_id=dept_map[t["dept"]],
                designation=t["desig"],
                specialization=t["spec"],
            )
            db.add(teacher)
            db.flush()
            teacher_map[teacher.id] = t["dept"]
    db.commit()
    print(f"  [OK] {len(teachers_data)} teachers seeded -> password: Teacher@123")
    return db.query(Teacher).all()


def seed_subjects(db, dept_map, sem_map, teachers):
    """Seed all subjects"""
    subject_map = {}  # code -> Subject.id
    teacher_list = list(teachers)
    t_idx = 0

    for dept_code, sems in SUBJECTS_BY_DEPT.items():
        dept_id = dept_map[dept_code]
        for sem_num, subj_list in sems.items():
            sem_id = sem_map.get(sem_num)
            if not sem_id:
                continue
            for subj in subj_list:
                existing = db.query(Subject).filter(Subject.code == subj["code"]).first()
                if not existing:
                    teacher = teacher_list[t_idx % len(teacher_list)]
                    t_idx += 1
                    s = Subject(
                        name=subj["name"],
                        code=subj["code"],
                        department_id=dept_id,
                        semester_id=sem_id,
                        teacher_id=teacher.id,
                        credits=subj["credits"],
                        max_internal=30,
                        max_external=70,
                        max_total=100,
                    )
                    db.add(s)
                    db.flush()
                    subject_map[subj["code"]] = s.id
                else:
                    subject_map[subj["code"]] = existing.id

    db.commit()
    print(f"  [OK] {len(subject_map)} subjects seeded")
    return subject_map


def seed_students(db, dept_map, data):
    """Seed student users and profiles"""
    student_map = {}  # original_id -> db_id
    profiles = data["students"]

    batch_size = 50
    for batch_start in range(0, len(profiles), batch_size):
        batch = profiles[batch_start:batch_start + batch_size]
        for s in batch:
            existing = db.query(User).filter(User.email == s["email"]).first()
            if not existing:
                user = User(
                    email=s["email"],
                    hashed_password=get_password_hash("Student@123"),
                    full_name=s["name"],
                    role="student",
                    is_active=True
                )
                db.add(user)
                db.flush()

                student = Student(
                    user_id=user.id,
                    student_id=s["student_id"],
                    roll_number=s["roll_number"],
                    department_id=dept_map[s["department_code"]],
                    branch=s["branch"],
                    current_semester=s["current_semester"],
                    admission_year=s["admission_year"],
                    academic_session=s["academic_session"],
                    phone=s["phone"],
                    guardian_name=s["guardian_name"],
                    guardian_phone=s["guardian_phone"],
                    is_active=True
                )
                db.add(student)
                db.flush()
                student_map[s["id"]] = student.id
            else:
                student = db.query(Student).filter(Student.user_id == existing.id).first()
                if student:
                    student_map[s["id"]] = student.id
        db.commit()
        print(f"    Students batch {batch_start}-{batch_start+batch_size} seeded")

    print(f"  [OK] {len(student_map)} students seeded -> password: Student@123")
    return student_map


def seed_marks(db, student_map, subject_map, sem_map, data):
    """Seed marks records"""
    count = 0
    for m in data["marks"]:
        orig_student_id = m["student_id"]
        db_student_id = student_map.get(orig_student_id)
        if not db_student_id:
            continue

        subject_db_id = subject_map.get(m["subject_code"])
        if not subject_db_id:
            continue

        sem_db_id = sem_map.get(m["semester_number"])
        if not sem_db_id:
            continue

        pct = m["percentage"]
        grade_rules = db.query(GradingRule).order_by(GradingRule.min_percentage.desc()).all()
        grade, gp, is_pass = "F", 0.0, False
        for rule in grade_rules:
            if rule.min_percentage <= pct <= rule.max_percentage:
                grade, gp, is_pass = rule.grade, rule.grade_points, rule.is_pass
                break

        existing = db.query(Marks).filter(
            Marks.student_id == db_student_id,
            Marks.subject_id == subject_db_id,
            Marks.semester_id == sem_db_id
        ).first()

        if not existing:
            mk = Marks(
                student_id=db_student_id,
                subject_id=subject_db_id,
                semester_id=sem_db_id,
                internal_marks=m["internal_marks"],
                external_marks=m["external_marks"],
                total_marks=m["total_marks"],
                max_marks=m["max_marks"],
                percentage=pct,
                grade=grade,
                grade_points=gp,
                credits=m["credits"],
                is_pass=is_pass,
            )
            db.add(mk)
            count += 1

        if count % 500 == 0 and count > 0:
            db.commit()
            print(f"    Marks committed: {count}")

    db.commit()
    print(f"  [OK] {count} marks records seeded")


def seed_attendance_summary(db, student_map, subject_map):
    """Seed attendance summary records per student/subject"""
    students = db.query(Student).all()
    count = 0
    for student in students:
        subjects = db.query(Subject).filter(
            Subject.semester_id.in_(
                db.query(Semester.id).filter(Semester.number <= min(student.current_semester, 4))
            )
        ).all()

        from datetime import date, timedelta
        import random as rnd
        rnd.seed(student.id)

        for subj in subjects[:5]:  # Limit per student
            # Already seeded?
            existing = db.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.subject_id == subj.id
            ).first()
            if existing:
                continue

            total = rnd.randint(60, 90)
            pct = rnd.uniform(55, 98)
            present = int(total * pct / 100)
            today = date.today()
            start = today - timedelta(days=total * 2)
            day = start
            added = 0
            present_added = 0
            while added < total and day <= today:
                if day.weekday() < 5:
                    is_present = present_added < present
                    db.add(Attendance(
                        student_id=student.id,
                        subject_id=subj.id,
                        date=day,
                        is_present=is_present,
                        total_classes=total,
                        present_classes=present,
                    ))
                    added += 1
                    if is_present:
                        present_added += 1
                    count += 1
                day += timedelta(days=1)

        if count % 2000 == 0 and count > 0:
            db.commit()

    db.commit()
    print(f"  [OK] {count} attendance records seeded")


def seed_sgpa_cgpa(db, sem_map):
    """Calculate and store SGPA/CGPA for all students"""
    students = db.query(Student).all()
    count = 0
    for student in students:
        cumulative_weighted = 0
        cumulative_credits = 0

        for sem_num, sem_id in sorted(sem_map.items()):
            marks = db.query(Marks).filter(
                Marks.student_id == student.id,
                Marks.semester_id == sem_id
            ).all()

            if not marks:
                continue

            tc = sum(m.credits for m in marks)
            if tc == 0:
                continue

            sgpa = round(sum(m.grade_points * m.credits for m in marks) / tc, 2)
            cumulative_weighted += sgpa * tc
            cumulative_credits += tc
            cgpa = round(cumulative_weighted / cumulative_credits, 2) if cumulative_credits > 0 else 0

            backlogs = sum(1 for m in marks if not m.is_pass)
            earned_credits = sum(m.credits for m in marks if m.is_pass)

            existing = db.query(StudentSemester).filter(
                StudentSemester.student_id == student.id,
                StudentSemester.semester_id == sem_id
            ).first()

            if not existing:
                db.add(StudentSemester(
                    student_id=student.id,
                    semester_id=sem_id,
                    sgpa=sgpa,
                    cgpa=cgpa,
                    total_credits=tc,
                    earned_credits=earned_credits,
                    backlogs=backlogs,
                ))
                count += 1

    db.commit()
    print(f"  [OK] {count} SGPA/CGPA records calculated")


def seed_alerts(db):
    """Generate academic alerts for at-risk students"""
    students = db.query(Student).all()
    count = 0
    for student in students:
        risk = compute_risk_score(student.id, db)
        if risk["risk_level"] in ["moderate", "high"]:
            existing = db.query(AcademicAlert).filter(
                AcademicAlert.student_id == student.id,
                AcademicAlert.is_resolved == False
            ).first()
            if not existing:
                db.add(AcademicAlert(
                    student_id=student.id,
                    risk_level=risk["risk_level"],
                    risk_score=risk["risk_score"],
                    reasons=risk["reasons"],
                    recommendations=risk["recommendations"],
                    is_resolved=False
                ))
                count += 1

    db.commit()
    print(f"  [OK] {count} academic alerts generated")


def seed_placement(db):
    """Generate placement readiness data for students"""
    students = db.query(Student).all()
    count = 0
    for student in students:
        existing = db.query(PlacementProgress).filter(
            PlacementProgress.student_id == student.id
        ).first()
        if existing:
            continue

        sems = db.query(StudentSemester).filter(
            StudentSemester.student_id == student.id
        ).all()
        cgpa = sems[-1].cgpa if sems else 5.0

        cgpa_score = min((cgpa / 10) * 100, 100)
        tech_score = round(random.uniform(30, 90), 1)
        apt_score = round(random.uniform(25, 85), 1)
        projects = random.randint(0, 5)
        internships = random.randint(0, 3)
        certs = random.randint(0, 4)
        mocks = random.randint(0, 10)

        overall = round((cgpa_score * 0.3 + tech_score * 0.3 + apt_score * 0.2 + projects * 5 + mocks * 2), 1)
        overall = min(overall, 100)

        db.add(PlacementProgress(
            student_id=student.id,
            cgpa_score=round(cgpa_score, 1),
            technical_score=tech_score,
            aptitude_score=apt_score,
            projects_count=projects,
            internships_count=internships,
            certifications_count=certs,
            mock_interviews=mocks,
            overall_readiness=overall,
            target_companies=random.sample(["TCS", "Infosys", "Wipro", "HCL", "Accenture", "Cognizant", "Google", "Microsoft"], 2),
        ))
        count += 1

    db.commit()
    print(f"  [OK] {count} placement records seeded")


def run_seeder():
    print("\n" + "="*60)
    print("  EduTrack AI - Database Seeder")
    print("  NOTE: All data is synthetic. No real student info used.")
    print("="*60)

    # Create tables
    create_tables()
    print("\n[1] Tables created")

    db = SessionLocal()
    try:
        print("\n[2] Seeding reference data...")
        seed_grading_rules(db)
        dept_map = seed_departments(db)
        sem_map = seed_semesters(db)

        print("\n[3] Seeding users...")
        seed_admin(db)
        teachers = seed_teachers(db, dept_map)

        print("\n[4] Seeding subjects...")
        subject_map = seed_subjects(db, dept_map, sem_map, teachers)

        print("\n[5] Generating and seeding student data...")
        data = generate_all_data()
        student_map = seed_students(db, dept_map, data)

        print("\n[6] Seeding marks...")
        seed_marks(db, student_map, subject_map, sem_map, data)

        print("\n[7] Seeding attendance...")
        seed_attendance_summary(db, student_map, subject_map)

        print("\n[8] Calculating SGPA/CGPA...")
        seed_sgpa_cgpa(db, sem_map)

        print("\n[9] Generating academic alerts...")
        seed_alerts(db)

        print("\n[10] Seeding placement data...")
        seed_placement(db)

        print("\n" + "="*60)
        print("  DATABASE SEEDED SUCCESSFULLY!")
        print("="*60)
        print("\nDemo Credentials:")
        print("  Admin:   admin@edutrack.ai   / Admin@123")
        print("  Teacher: ramesh.kumar@edutrack.ai / Teacher@123")
        print("  Student: (see students.csv for email list)")
        print("           Default password: Student@123")
        print("="*60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seeder()
