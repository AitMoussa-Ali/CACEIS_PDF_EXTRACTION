import os 

from app.pdf.run_pdf import run_extract_pdf
from app.excel.run_excel import run_excel
task = os.getenv("TASK", "default_task")

if task == "pdf":
    run_extract_pdf()

if task == "excel":
    run_excel()