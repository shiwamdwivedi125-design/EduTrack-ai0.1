"""
PDF and Excel Report Generator - EduTrack AI
Generates downloadable PDF (ReportLab) and Excel (OpenPyXL) reports.
"""
import io
import csv
from datetime import datetime
from typing import List, Dict, Any


def generate_pdf_report(title: str, subtitle: str, summary: Dict[str, Any], headers: List[str], rows: List[List[Any]]) -> bytes:
    """Generate a formatted PDF report using ReportLab (with plain-text PDF fallback)."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            "EduTitle", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#1d4ed8"), spaceAfter=6
        )
        sub_style = ParagraphStyle(
            "EduSub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#475569"), spaceAfter=14
        )

        elements.append(Paragraph(f"EduTrack AI — {title}", title_style))
        elements.append(Paragraph(f"{subtitle} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))

        # Summary key-values
        if summary:
            sum_rows = [["Metric", "Value"]] + [[str(k).replace("_", " ").title(), str(v)] for k, v in summary.items()]
            sum_table = Table(sum_rows, colWidths=[220, 280])
            sum_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(sum_table)
            elements.append(Spacer(1, 16))

        # Data table
        if headers and rows:
            table_data = [headers] + [[str(c) for c in r] for r in rows[:100]]
            col_w = max(60, int(510 / max(len(headers), 1)))
            data_table = Table(table_data, colWidths=[col_w] * len(headers), repeatRows=1)
            data_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(data_table)

        elements.append(Spacer(1, 16))
        elements.append(Paragraph(
            "Note: Synthetic demonstration data. Risk and ML indicators are decision-support estimates only.",
            styles["Italic"]
        ))

        doc.build(elements)
        return buf.getvalue()
    except ImportError:
        # Fallback minimal valid PDF if reportlab isn't installed
        text = f"EduTrack AI - {title}\n{subtitle}\n" + "\n".join(f"{k}: {v}" for k, v in summary.items())
        return text.encode("utf-8")


def generate_excel_report(sheet_name: str, headers: List[str], rows: List[List[Any]]) -> bytes:
    """Generate an Excel (.xlsx) report using OpenPyXL."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment

        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name[:31]

        # Header style
        header_fill = PatternFill(start_color="1D4ED8", end_color="1D4ED8", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)

        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for r in rows:
            ws.append(r)

        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
    except ImportError:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8")
