# automation/sharepoint_uploader.py
from GetToken import get_token
import zipfile
from Sharepoint_handeling.DriverID import get_drive_id
import dotenv
import requests
import os
from utils.Config import Config
from pages.caceis.Parser_excel import generate_excel_content_from_pdf
# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def create_folder(token: str, drive_id: str, parent_folder: str, folder_name: str) -> str:
    """Creates a subfolder inside parent_folder and returns its id"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # First, check if the folder already exists
    check_url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root:/{parent_folder}/{folder_name}"
    )
    
    check_response = requests.get(check_url, headers=headers)
    
    if check_response.status_code == 200:
        print(f"⚠️ Folder already exists: {parent_folder}/{folder_name}")
        return check_response.json()["id"]
    
    # Folder doesn't exist, create it
    url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root:/{parent_folder}:/children"
    )
    body = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "fail"  # fail if already exists
    }
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code in [200, 201]:
        print(f"✅ Folder created: {parent_folder}/{folder_name}")
        return response.json()["id"]
    else:
        raise Exception(f"Failed to create folder: {response.json()}")

def upload_file_to_folder(token: str, drive_id: str, folder_path: str, filename: str, file_content: bytes):
    """Uploads a file to a specific folder path"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root:/{folder_path}/{filename}:/content"
    )
    response = requests.put(url, headers=headers, data=file_content)

    if response.status_code in [200, 201]:
        print(f"✅ Uploaded: {filename}")
    else:
        raise Exception(f"Failed to upload {filename}: {response.json()}")

#eturning content
def upload_single_pdf_to_sharepoint(pdf_path, fund_name: str, dispo: str, au: str, file_name: str, periodicity):
    token = get_token()
    drive_id = get_drive_id(token)

    safe_fund_name = fund_name.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-").strip()
    subfolder_name = f"{safe_fund_name}-{dispo.replace('/', '-')}_{au.replace('/', '-')}"
    
    if periodicity == "MEN : Mensuelle": 
        parent_folder_pdf = Config.SHAREPOINT_FOLDER_PDF_MENSUELLE
    else:
        parent_folder_pdf = Config.SHAREPOINT_FOLDER_PDF_QUOTIDIEN
    
    full_folder_path_pdf = f"{parent_folder_pdf}/{subfolder_name}"
    # full_folder_path_excel = f"{parent_folder_excel}/{subfolder_name}"
    
    create_folder(token, drive_id, parent_folder_pdf, subfolder_name)
    # create_folder(token, drive_id, parent_folder_excel, subfolder_name)
    content = ""
    with open(pdf_path, "rb") as f:
        content = f.read()
    try:
        upload_file_to_folder(token, drive_id, full_folder_path_pdf, file_name + ".pdf", content)
    except Exception as e:
        print(f"Failed to upload PDF: {file_name}.pdf. Error: {str(e)}")
        
    return content


def upload_single_excel_to_sharepoint(management_company: str, excel_data, funds, periodicity):
    token = get_token()
    drive_id = get_drive_id(token)
    safe_management_name = management_company.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-").strip()
    
    if periodicity == "MEN : Mensuelle": 
        parent_folder_excel = Config.SHAREPOINT_FOLDER_EXCEL_MENSUELLE
    else:
        parent_folder_excel = Config.SHAREPOINT_FOLDER_EXCEL_QUOTIDIEN
    
    full_folder_path_excel = f"{parent_folder_excel}/{safe_management_name}"
    file_name = management_company
    create_folder(token, drive_id, parent_folder_excel, safe_management_name)
    
    try:
        excel_content = generate_excel_content_from_pdf("Caceis", excel_data, funds)
        upload_file_to_folder(token, drive_id, full_folder_path_excel, safe_management_name + ".xlsx", excel_content)
    except Exception as e:
        print(f"Failed to upload Excel: {file_name}.xlsx. Error: {str(e)}")