import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")
    SHARED_MAILBOX = os.getenv("SHARED_MAILBOX")
    SCOPES = os.getenv("SCOPES")
    PASSWORD_MAILBOX = os.getenv("PASSWORD_MAILBOX")
    URL_SHARE_POINT = os.getenv("URL_SHARE_POINT")
    SHAREPOINT_FOLDER_PDF_MENSUELLE = os.getenv("SHAREPOINT_FOLDER_PDF_MENSUELLE")
    SHAREPOINT_FOLDER_PDF_QUOTIDIEN = os.getenv("SHAREPOINT_FOLDER_PDF_QUOTIDIEN")
    SHAREPOINT_FOLDER_EXCEL_MENSUELLE = os.getenv("SHAREPOINT_FOLDER_EXCEL_MENSUELLE")
    SHAREPOINT_FOLDER_EXCEL_QUOTIDIEN = os.getenv("SHAREPOINT_FOLDER_EXCEL_QUOTIDIEN")
    SHAREPOINT_SITE_URL = os.getenv("SHAREPOINT_SITE_URL")
    PATH_LOGIN_FILE = os.getenv("PATH_LOGIN_FILE")
    SHEET_LOGIN_NAME = os.getenv("SHEET_LOGIN_NAME")
    LOCAL_PATH_LOGIN_FILE_SHEET = os.getenv("LOCAL_PATH_LOGIN_FILE_SHEET")
    MAIL_SENDER = os.getenv("SENDER") 
    
    # docker compose run --rm caceis-extract 2>&1 | Tee-Object -FilePath log.txt