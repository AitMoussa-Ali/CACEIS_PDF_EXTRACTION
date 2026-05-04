import os 

from app.pdf.run_pdf import run_extract_pdf
from app.excel.run_excel import run_excel
task = os.getenv("TASK", "default_task")
de = os.getenv("DE", "default_de")
au = os.getenv("AU", "default_au")

if task == "pdf":
    run_extract_pdf(dispo=de, au=au)

if task == "excel":
    run_excel()