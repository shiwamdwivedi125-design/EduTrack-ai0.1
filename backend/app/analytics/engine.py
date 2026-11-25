"""
Python Data Analytics Engine - EduTrack AI
Uses Pandas, NumPy, Matplotlib, and Seaborn for:
- Data loading & cleaning
- Missing value handling & duplicate detection
- Descriptive statistics (mean, median, mode, std)
- Student ranking & subject/department analysis
- Attendance vs Marks correlation
- Matplotlib & Seaborn chart generation (base64 encoded PNGs)
"""
import io
import base64
import numpy as np
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Student, Marks, Attendance, Department, Subject, StudentSemester


def _safe_imports():
    try:
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        return pd, plt, sns
    except ImportError:
        return None, None, None


def compute_descriptive_analytics(db: Session) -> Dict[str, Any]:
    """Compute comprehensive descriptive statistics using Pandas & NumPy."""
    pd, _, _ = _safe_imports()

    marks_rows = db.query(Marks).all()
    att_rows = db.query(Attendance).all()
    students = db.query(Student).all()
    depts = {d.id: d for d in db.query(Department).all()}
    subjects = {s.id: s for s in db.query(Subject).all()}
    sems = db.query(StudentSemester).all()

    if not marks_rows:
        return {"message": "No marks data available", "stats": {}, "rankings": [], "correlation": 0}

    # Build raw arrays/DataFrame
    marks_data = [
        {
            "student_id": m.student_id,
            "subject_id": m.subject_id,
            "subject_code": subjects[m.subject_id].code if m.subject_id in subjects else str(m.subject_id),
            "subject_name": subjects[m.subject_id].name if m.subject_id in subjects else "Unknown",
            "semester_id": m.semester_id,
            "internal": m.internal_marks,
            "external": m.external_marks,
            "total": m.total_marks,
            "percentage": m.percentage,
            "grade_points": m.grade_points,
            "is_pass": m.is_pass,
        }
        for m in marks_rows
    ]

    if pd is not None:
        df = pd.DataFrame(marks_data)
        # Data cleaning & validation
        initial_count = len(df)
        missing_count = int(df.isnull().sum().sum())
        df = df.dropna(subset=["percentage", "total"])
        dup_count = int(df.duplicated(subset=["student_id", "subject_id", "semester_id"]).sum())
        df = df.drop_duplicates(subset=["student_id", "subject_id", "semester_id"])

        pct_series = df["percentage"]
        mode_vals = pct_series.mode()
        mode_val = round(float(mode_vals.iloc[0]), 2) if len(mode_vals) > 0 else 0.0

        stats = {
            "records_analyzed": len(df),
            "missing_values_handled": missing_count,
            "duplicates_removed": dup_count,
            "mean_percentage": round(float(np.mean(pct_series)), 2),
            "median_percentage": round(float(np.median(pct_series)), 2),
            "mode_percentage": mode_val,
            "std_deviation": round(float(np.std(pct_series, ddof=1)), 2) if len(pct_series) > 1 else 0.0,
            "min_percentage": round(float(np.min(pct_series)), 2),
            "max_percentage": round(float(np.max(pct_series)), 2),
            "q25": round(float(np.percentile(pct_series, 25)), 2),
            "q75": round(float(np.percentile(pct_series, 75)), 2),
            "pass_rate": round(float(df["is_pass"].mean() * 100), 2),
        }

        # Subject-wise stats
        subj_stats = []
        for scode, grp in df.groupby("subject_code"):
            subj_stats.append({
                "subject_code": scode,
                "subject_name": grp["subject_name"].iloc[0],
                "mean": round(float(grp["percentage"].mean()), 2),
                "median": round(float(grp["percentage"].median()), 2),
                "std": round(float(grp["percentage"].std(ddof=1)), 2) if len(grp) > 1 else 0.0,
                "pass_rate": round(float(grp["is_pass"].mean() * 100), 2),
                "count": int(len(grp)),
            })
        subj_stats.sort(key=lambda x: x["mean"], reverse=True)
    else:
        pcts = [m["percentage"] for m in marks_data]
        stats = {
            "records_analyzed": len(pcts),
            "missing_values_handled": 0,
            "duplicates_removed": 0,
            "mean_percentage": round(float(np.mean(pcts)), 2),
            "median_percentage": round(float(np.median(pcts)), 2),
            "mode_percentage": round(float(np.median(pcts)), 2),
            "std_deviation": round(float(np.std(pcts)), 2),
            "min_percentage": round(float(np.min(pcts)), 2),
            "max_percentage": round(float(np.max(pcts)), 2),
            "pass_rate": round(sum(1 for m in marks_data if m["is_pass"]) / len(marks_data) * 100, 2),
        }
        subj_stats = []

    # Student rankings & attendance correlation
    latest_cgpa = {}
    for ss in sems:
        if ss.student_id not in latest_cgpa or ss.id > latest_cgpa[ss.student_id].id:
            latest_cgpa[ss.student_id] = ss

    att_by_student = {}
    for a in att_rows:
        d = att_by_student.setdefault(a.student_id, {"t": 0, "p": 0})
        d["t"] += 1
        if a.is_present:
            d["p"] += 1

    rankings = []
    att_vec, cgpa_vec = [], []
    for st in students:
        cgpa = latest_cgpa[st.id].cgpa if st.id in latest_cgpa else 0.0
        att_info = att_by_student.get(st.id, {"t": 0, "p": 0})
        att_pct = round((att_info["p"] / att_info["t"]) * 100, 2) if att_info["t"] > 0 else 0.0
        if cgpa > 0 and att_info["t"] > 0:
            att_vec.append(att_pct)
            cgpa_vec.append(cgpa)
        rankings.append({
            "student_id": st.id,
            "student_code": st.student_id,
            "name": st.user.full_name if st.user else st.student_id,
            "department": depts[st.department_id].code if st.department_id in depts else "",
            "cgpa": cgpa,
            "attendance_pct": att_pct,
        })

    rankings.sort(key=lambda x: x["cgpa"], reverse=True)
    for idx, r in enumerate(rankings, start=1):
        r["rank"] = idx

    correlation = 0.0
    if len(att_vec) > 2:
        corr_matrix = np.corrcoef(att_vec, cgpa_vec)
        val = corr_matrix[0, 1]
        if not np.isnan(val):
            correlation = round(float(val), 3)

    return {
        "stats": stats,
        "subject_analysis": subj_stats[:20],
        "top_rankings": rankings[:15],
        "attendance_cgpa_correlation": correlation,
        "correlation_interpretation": (
            "Strong positive correlation" if correlation > 0.6
            else "Moderate positive correlation" if correlation > 0.3
            else "Weak/negligible correlation"
        ),
    }


def generate_seaborn_charts(db: Session) -> Dict[str, str]:
    """Generate Matplotlib/Seaborn charts and return base64 PNG data URLs."""
    pd, plt, sns = _safe_imports()
    if pd is None or plt is None or sns is None:
        return {}

    sns.set_theme(style="whitegrid", palette="Blues_d")
    charts = {}

    marks = db.query(Marks).all()
    sems = db.query(StudentSemester).all()
    depts = {d.id: d.code for d in db.query(Department).all()}
    students = {s.id: s for s in db.query(Student).all()}

    if not marks:
        return {}

    # 1. Marks Percentage Distribution Histogram + KDE
    try:
        pcts = [m.percentage for m in marks]
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        sns.histplot(pcts, bins=20, kde=True, color="#2563eb", ax=ax)
        ax.set_title("Student Marks Percentage Distribution", fontsize=12, fontweight="bold")
        ax.set_xlabel("Percentage (%)")
        ax.set_ylabel("Frequency")
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        charts["marks_distribution"] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        pass

    # 2. Department-wise CGPA Boxplot
    try:
        latest = {}
        for ss in sems:
            if ss.student_id not in latest or ss.id > latest[ss.student_id].id:
                latest[ss.student_id] = ss
        box_data = []
        for sid, ss in latest.items():
            st = students.get(sid)
            if st:
                box_data.append({"Department": depts.get(st.department_id, "Other"), "CGPA": ss.cgpa})
        if box_data:
            df_box = pd.DataFrame(box_data)
            fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
            sns.boxplot(data=df_box, x="Department", y="CGPA", palette="Set2", ax=ax)
            ax.set_title("Department-wise CGPA Distribution", fontsize=12, fontweight="bold")
            buf = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format="png")
            plt.close(fig)
            charts["dept_cgpa_boxplot"] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        pass

    return charts
