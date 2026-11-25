"""
Synthetic Data Generator for EduTrack AI
Generates realistic but purely synthetic student academic data.
No real student data is used.
"""
import random
import csv
import os
import json
from datetime import date, timedelta


random.seed(42)  # Reproducible data

# ── Constants ──────────────────────────────────────────────────────────────
DEPARTMENTS = [
    {"id": 1, "name": "Computer Science & Engineering", "code": "CSE", "hod": "Dr. Ramesh Kumar"},
    {"id": 2, "name": "Electronics & Communication", "code": "ECE", "hod": "Dr. Priya Sharma"},
    {"id": 3, "name": "Mechanical Engineering", "code": "MECH", "hod": "Dr. Suresh Patel"},
]

FIRST_NAMES = [
    "Aarav", "Aditya", "Akash", "Amit", "Arjun", "Ayaan", "Bharat", "Chirag",
    "Deepak", "Dev", "Dhruv", "Gaurav", "Harsh", "Ishaan", "Jay", "Kabir",
    "Karan", "Kartik", "Kunal", "Manish", "Mohit", "Nikhil", "Pavan", "Pranav",
    "Priya", "Pooja", "Rahul", "Raj", "Riya", "Rohit", "Sachin", "Sanjay",
    "Sneha", "Suresh", "Tanvi", "Uday", "Varun", "Vikram", "Vishal", "Yash",
    "Ananya", "Anjali", "Diya", "Kavya", "Meera", "Nisha", "Payal", "Radha",
    "Sakshi", "Swati", "Tanya", "Vidya", "Neha", "Simran", "Komal", "Divya",
    "Ritesh", "Sumit", "Tarun", "Vinay", "Ajay", "Alok", "Ankit", "Arvind",
    "Ashish", "Dinesh", "Girish", "Hemant", "Jatin", "Lalit", "Manoj", "Naresh",
    "Piyush", "Rakesh", "Ramesh", "Sanjeev", "Shyam", "Sunil", "Tushar", "Vijay"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Joshi", "Mishra",
    "Reddy", "Nair", "Pillai", "Iyer", "Rao", "Mehta", "Shah", "Pandey",
    "Tiwari", "Srivastava", "Agarwal", "Khanna", "Kapoor", "Malhotra", "Bose",
    "Das", "Chatterjee", "Mukherjee", "Sen", "Ghosh", "Banerjee", "Dey",
    "Desai", "Jain", "Saxena", "Tripathi", "Dubey", "Yadav", "Thakur", "Rathore"
]

SUBJECTS_BY_DEPT = {
    "CSE": {
        1: [
            {"name": "Engineering Mathematics I", "code": "CSE101", "credits": 4},
            {"name": "Programming Fundamentals (C)", "code": "CSE102", "credits": 4},
            {"name": "Digital Logic Design", "code": "CSE103", "credits": 3},
            {"name": "English Communication", "code": "CSE104", "credits": 2},
            {"name": "Engineering Physics", "code": "CSE105", "credits": 3},
        ],
        2: [
            {"name": "Data Structures", "code": "CSE201", "credits": 4},
            {"name": "Object Oriented Programming", "code": "CSE202", "credits": 4},
            {"name": "Discrete Mathematics", "code": "CSE203", "credits": 3},
            {"name": "Computer Organization", "code": "CSE204", "credits": 3},
            {"name": "Engineering Mathematics II", "code": "CSE205", "credits": 4},
        ],
        3: [
            {"name": "Algorithms & Complexity", "code": "CSE301", "credits": 4},
            {"name": "Database Management Systems", "code": "CSE302", "credits": 4},
            {"name": "Operating Systems", "code": "CSE303", "credits": 4},
            {"name": "Computer Networks", "code": "CSE304", "credits": 3},
            {"name": "Software Engineering", "code": "CSE305", "credits": 3},
        ],
        4: [
            {"name": "Compiler Design", "code": "CSE401", "credits": 4},
            {"name": "Artificial Intelligence", "code": "CSE402", "credits": 4},
            {"name": "Web Technologies", "code": "CSE403", "credits": 3},
            {"name": "Information Security", "code": "CSE404", "credits": 3},
            {"name": "Mini Project", "code": "CSE405", "credits": 2},
        ],
    },
    "ECE": {
        1: [
            {"name": "Engineering Mathematics I", "code": "ECE101", "credits": 4},
            {"name": "Basic Electronics", "code": "ECE102", "credits": 4},
            {"name": "Circuit Theory", "code": "ECE103", "credits": 3},
            {"name": "English Communication", "code": "ECE104", "credits": 2},
            {"name": "Engineering Physics", "code": "ECE105", "credits": 3},
        ],
        2: [
            {"name": "Electronic Devices", "code": "ECE201", "credits": 4},
            {"name": "Network Theory", "code": "ECE202", "credits": 4},
            {"name": "Signals & Systems", "code": "ECE203", "credits": 4},
            {"name": "Digital Electronics", "code": "ECE204", "credits": 3},
            {"name": "Engineering Mathematics II", "code": "ECE205", "credits": 3},
        ],
        3: [
            {"name": "Analog Circuits", "code": "ECE301", "credits": 4},
            {"name": "Communication Systems", "code": "ECE302", "credits": 4},
            {"name": "Microprocessors", "code": "ECE303", "credits": 4},
            {"name": "Electromagnetics", "code": "ECE304", "credits": 3},
            {"name": "Control Systems", "code": "ECE305", "credits": 3},
        ],
        4: [
            {"name": "VLSI Design", "code": "ECE401", "credits": 4},
            {"name": "Digital Signal Processing", "code": "ECE402", "credits": 4},
            {"name": "Wireless Communication", "code": "ECE403", "credits": 3},
            {"name": "Embedded Systems", "code": "ECE404", "credits": 3},
            {"name": "Mini Project", "code": "ECE405", "credits": 2},
        ],
    },
    "MECH": {
        1: [
            {"name": "Engineering Mathematics I", "code": "MECH101", "credits": 4},
            {"name": "Engineering Drawing", "code": "MECH102", "credits": 3},
            {"name": "Engineering Physics", "code": "MECH103", "credits": 3},
            {"name": "English Communication", "code": "MECH104", "credits": 2},
            {"name": "Workshop Technology", "code": "MECH105", "credits": 3},
        ],
        2: [
            {"name": "Engineering Mathematics II", "code": "MECH201", "credits": 4},
            {"name": "Strength of Materials", "code": "MECH202", "credits": 4},
            {"name": "Thermodynamics", "code": "MECH203", "credits": 4},
            {"name": "Manufacturing Processes", "code": "MECH204", "credits": 3},
            {"name": "Fluid Mechanics", "code": "MECH205", "credits": 3},
        ],
        3: [
            {"name": "Machine Design", "code": "MECH301", "credits": 4},
            {"name": "Heat Transfer", "code": "MECH302", "credits": 4},
            {"name": "Dynamics of Machinery", "code": "MECH303", "credits": 4},
            {"name": "Metrology & Quality Control", "code": "MECH304", "credits": 3},
            {"name": "Industrial Engineering", "code": "MECH305", "credits": 3},
        ],
        4: [
            {"name": "CAD/CAM", "code": "MECH401", "credits": 4},
            {"name": "Robotics & Automation", "code": "MECH402", "credits": 4},
            {"name": "Refrigeration & AC", "code": "MECH403", "credits": 3},
            {"name": "Power Plant Engineering", "code": "MECH404", "credits": 3},
            {"name": "Mini Project", "code": "MECH405", "credits": 2},
        ],
    }
}

DESIGNATIONS = ["Assistant Professor", "Associate Professor", "Professor", "Senior Professor", "HOD"]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_email(name, uid):
    name_part = name.lower().replace(" ", ".")
    return f"{name_part}.{uid}@edu.example.com"


def skewed_marks(low=False, high=False):
    """Generate realistic marks with optional skew"""
    if low:
        return round(random.gauss(45, 15), 1)
    elif high:
        return round(random.gauss(78, 10), 1)
    else:
        return round(random.gauss(62, 18), 1)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def generate_all_data():
    """Generate all synthetic data"""
    output = {}

    # ── Students (200) ───────────────────────────────────────────
    students = []
    student_id = 1
    for dept in DEPARTMENTS:
        count = 70 if dept["id"] <= 2 else 60
        for i in range(count):
            name = random_name()
            admission_year = random.choice([2021, 2022, 2023])
            current_sem = min(8, (2024 - admission_year) * 2 + random.randint(1, 2))
            sid = f"{dept['code']}{admission_year}{str(i+1).zfill(3)}"
            roll = f"{dept['code']}/{admission_year}/{str(i+1).zfill(3)}"
            students.append({
                "id": student_id,
                "user_id": student_id + 10,
                "name": name,
                "email": random_email(name, f"s{student_id}"),
                "student_id": sid,
                "roll_number": roll,
                "department_id": dept["id"],
                "department_code": dept["code"],
                "branch": dept["name"],
                "current_semester": current_sem,
                "admission_year": admission_year,
                "academic_session": f"{admission_year}-{admission_year+4}",
                "phone": f"9{random.randint(100000000, 999999999)}",
                "guardian_name": random_name(),
                "guardian_phone": f"9{random.randint(100000000, 999999999)}",
                "performance_profile": random.choice(["high", "average", "low", "average", "average"]),
            })
            student_id += 1

    output["students"] = students

    # ── Marks ───────────────────────────────────────────────────────
    marks = []
    marks_id = 1
    for student in students:
        dept_code = student["department_code"]
        profile = student["performance_profile"]
        sems_to_fill = min(student["current_semester"], 4)

        for sem_num in range(1, sems_to_fill + 1):
            subjects = SUBJECTS_BY_DEPT.get(dept_code, {}).get(sem_num, [])
            for subj in subjects:
                max_int = 30
                max_ext = 70
                if profile == "high":
                    int_m = clamp(skewed_marks(high=True), 18, 30)
                    ext_m = clamp(skewed_marks(high=True) * 0.7, 42, 70)
                elif profile == "low":
                    int_m = clamp(skewed_marks(low=True), 5, 25)
                    ext_m = clamp(skewed_marks(low=True) * 0.7, 15, 55)
                else:
                    int_m = clamp(skewed_marks(), 10, 30)
                    ext_m = clamp(skewed_marks() * 0.7, 28, 70)

                total = round(int_m + ext_m, 2)
                pct = round((total / 100) * 100, 2)
                marks.append({
                    "id": marks_id,
                    "student_id": student["id"],
                    "subject_code": subj["code"],
                    "semester_number": sem_num,
                    "internal_marks": round(int_m, 2),
                    "external_marks": round(ext_m, 2),
                    "total_marks": total,
                    "max_marks": 100,
                    "percentage": pct,
                    "credits": subj["credits"],
                })
                marks_id += 1

    output["marks"] = marks

    # ── Attendance ───────────────────────────────────────────────
    attendance = []
    att_id = 1
    today = date.today()
    for student in students:
        dept_code = student["department_code"]
        profile = student["performance_profile"]
        sem_num = min(student["current_semester"], 4)
        subjects = SUBJECTS_BY_DEPT.get(dept_code, {}).get(sem_num, [])

        for subj in subjects:
            total_classes = random.randint(60, 90)
            if profile == "high":
                present_pct = random.uniform(85, 100)
            elif profile == "low":
                present_pct = random.uniform(45, 75)
            else:
                present_pct = random.uniform(70, 90)

            present_classes = int(total_classes * present_pct / 100)

            # Generate daily attendance records
            start_date = today - timedelta(days=total_classes * 2)
            current_date = start_date
            class_days = 0
            present_count = 0

            while class_days < total_classes and current_date <= today:
                if current_date.weekday() < 5:  # Weekday
                    is_present = class_days < present_classes
                    attendance.append({
                        "id": att_id,
                        "student_id": student["id"],
                        "subject_code": subj["code"],
                        "date": str(current_date),
                        "is_present": is_present,
                    })
                    att_id += 1
                    class_days += 1
                current_date += timedelta(days=1)

    output["attendance"] = attendance
    output["departments"] = DEPARTMENTS
    output["subjects"] = SUBJECTS_BY_DEPT

    return output


def save_csv_files(base_path: str):
    """Save sample data to CSV files"""
    data = generate_all_data()

    # Students CSV
    students_path = os.path.join(base_path, "students.csv")
    with open(students_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "name", "email", "student_id", "roll_number",
            "department_id", "department_code", "branch", "current_semester",
            "admission_year", "academic_session", "phone"
        ])
        writer.writeheader()
        for s in data["students"]:
            writer.writerow({k: s[k] for k in [
                "id", "name", "email", "student_id", "roll_number",
                "department_id", "department_code", "branch", "current_semester",
                "admission_year", "academic_session", "phone"
            ]})

    # Marks CSV
    marks_path = os.path.join(base_path, "marks.csv")
    with open(marks_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "student_id", "subject_code", "semester_number",
            "internal_marks", "external_marks", "total_marks", "max_marks", "percentage", "credits"
        ])
        writer.writeheader()
        writer.writerows(data["marks"])

    # Subjects CSV
    subjects_path = os.path.join(base_path, "subjects.csv")
    with open(subjects_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["code", "name", "department_code", "semester_number", "credits"])
        writer.writeheader()
        for dept_code, sems in data["subjects"].items():
            for sem_num, subj_list in sems.items():
                for subj in subj_list:
                    writer.writerow({
                        "code": subj["code"],
                        "name": subj["name"],
                        "department_code": dept_code,
                        "semester_number": sem_num,
                        "credits": subj["credits"],
                    })

    # Attendance summary CSV (not daily records - too large)
    att_summary_path = os.path.join(base_path, "attendance_summary.csv")
    att_by_student_subject = {}
    for att in data["attendance"]:
        key = (att["student_id"], att["subject_code"])
        if key not in att_by_student_subject:
            att_by_student_subject[key] = {"total": 0, "present": 0}
        att_by_student_subject[key]["total"] += 1
        if att["is_present"]:
            att_by_student_subject[key]["present"] += 1

    with open(att_summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_id", "subject_code", "total_classes", "present_classes", "attendance_percentage"])
        writer.writeheader()
        for (sid, scode), counts in att_by_student_subject.items():
            pct = round(counts["present"] / counts["total"] * 100, 2) if counts["total"] > 0 else 0
            writer.writerow({
                "student_id": sid,
                "subject_code": scode,
                "total_classes": counts["total"],
                "present_classes": counts["present"],
                "attendance_percentage": pct,
            })

    print(f"[EduTrack AI] Sample CSV files saved to: {base_path}")
    print(f"  students.csv:          {len(data['students'])} records")
    print(f"  marks.csv:             {len(data['marks'])} records")
    print(f"  subjects.csv:          generated")
    print(f"  attendance_summary.csv: generated")
    print("  NOTE: All data is synthetic. No real student information was used.")
    return data


if __name__ == "__main__":
    save_csv_files(os.path.join(os.path.dirname(__file__), "sample"))
