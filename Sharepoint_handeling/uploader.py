# automation/sharepoint_uploader.py
from GetToken import get_token
import zipfile
from Sharepoint_handeling.DriverID import get_drive_id
import dotenv
import requests
import os

vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

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

def upload_zip_to_sharepoint(zip_path: str, fund_name: str, dispo: str, au: str, texts: list):
    """
    Extracts zip and uploads PDFs to SharePoint
    inside a subfolder named after the date range
    """
    token = get_token()
    drive_id = get_drive_id(token)
    fund_name = fund_name.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-").strip()
    
    # Build subfolder name from dates e.g. "01-04-2026_18-04-2026"
    subfolder_name = f"{fund_name}-{dispo.replace('/', '-')}_{au.replace('/', '-')}"
    parent_folder = vars["SHAREPOINT_FOLDER"]  # test_automation_aplitec
    full_folder_path = f"{parent_folder}/{subfolder_name}"

    # Create the subfolder on SharePoint
    create_folder(token, drive_id, parent_folder, subfolder_name)

    # Extract zip in memory and upload each PDF
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        pdf_files = [f for f in zip_ref.namelist() if f.endswith(".pdf")]
        print(f"📤 Uploading {len(pdf_files)} PDFs to SharePoint/{full_folder_path}")

        if len(pdf_files) != len(texts):
            raise ValueError(f"Mismatch: {len(pdf_files)} PDFs but {len(texts)} names")
        
        for pdf_name, file_name in zip(pdf_files, texts):
            file_name = file_name.strip().replace("/", "-").replace("\n", " ") + ".pdf"
            with zip_ref.open(pdf_name) as pdf_file:
                content = pdf_file.read()  # read into memory
                upload_file_to_folder(token, drive_id, full_folder_path, file_name, content)

    print(f"\n✅ All files uploaded to SharePoint/{full_folder_path}")

def upload_single_pdf_to_sharepoint(pdf_path, fund_name: str, dispo: str, au: str, file_name: str):
    token = get_token()
    drive_id = get_drive_id(token)

    safe_fund_name = fund_name.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-").strip()
    subfolder_name = f"{safe_fund_name}-{dispo.replace('/', '-')}_{au.replace('/', '-')}"
    parent_folder = vars["SHAREPOINT_FOLDER"]
    full_folder_path = f"{parent_folder}/{subfolder_name}"

    create_folder(token, drive_id, parent_folder, subfolder_name)

    with open(pdf_path, "rb") as f:
        content = f.read()

    upload_file_to_folder(token, drive_id, full_folder_path, file_name + ".pdf", content)

