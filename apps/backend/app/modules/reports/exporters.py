from io import BytesIO
from typing import Any, Dict

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_kpis_excel(data: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    df = pd.DataFrame([data])
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


def export_table_excel(records: list[Dict[str, Any]]) -> bytes:
    buffer = BytesIO()
    df = pd.DataFrame(records)
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


def export_kpis_pdf(data: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("PalmCore CMMS KPI Report")
    pdf.drawString(72, 740, "PalmCore CMMS KPI Report")
    y = 700
    for key, value in data.items():
        pdf.drawString(72, y, f"{key}: {value}")
        y -= 20
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def export_table_pdf(title: str, records: list[Dict[str, Any]]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(title)
    pdf.drawString(72, 740, title)
    y = 700
    for record in records:
        line = " | ".join(f"{key}: {value}" for key, value in record.items())
        pdf.drawString(72, y, line)
        y -= 16
        if y < 72:
            pdf.showPage()
            y = 740
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
