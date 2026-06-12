import os

from app.pdf.run_pdf import run_extract_pdf
from app.excel.run_excel import run_excel
from datetime import datetime, timedelta




def get_week_dates():
    today = datetime.today()

    # Previous Saturday
    last_saturday = today - timedelta(days=31)

    de = last_saturday.strftime("%d/%m/%Y")
    au = today.strftime("%d/%m/%Y")

    return de, au


de, au = get_week_dates()
run_extract_pdf(dispo=de, au=au)