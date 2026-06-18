import os

from app.pdf.run_pdf import run_extract_pdf
from app.excel.run_excel import run_excel
from datetime import datetime, timedelta
import calendar

def is_last_day_of_month() -> bool:
    today = datetime.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return last_day == today.day  # fix

def should_run_today() -> bool:
    today = datetime.today()
    is_friday = today.weekday() == 3          # Jeudi
    is_last_day = is_last_day_of_month()      # dernier jour du mois
    return is_friday or is_last_day

if __name__ == "__main__":
    if not should_run_today():
        print(f"⏭️ Pas d'exécution aujourd'hui ({datetime.today().strftime('%A %d/%m/%Y')}), skip.")
        exit(0)
    
    run_extract_pdf()
