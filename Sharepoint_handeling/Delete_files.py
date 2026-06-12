import dotenv
import requests
from GetToken import get_token
from Sharepoint_handeling.DriverID import get_drive_id
from utils.Config import Config

# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")


def delete_files():
    
    token = get_token()
    drive_id = get_drive_id(token)
    """Deletes all files in a specific folder path"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    check_url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root:/{Config.SHAREPOINT_FOLDER}"
    )
    
    check_response = requests.get(check_url, headers=headers)
    if check_response.status_code == 200:
        print(f"Folder found: {Config.SHAREPOINT_FOLDER}")
        delete_url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root:/{Config.SHAREPOINT_FOLDER}"
        )
    
        delete_response = requests.delete(delete_url, headers=headers)
        
        if delete_response.status_code == 204:
            print(f"Files deleted successfully from folder: {Config.SHAREPOINT_FOLDER}")
        else:
            raise Exception(f"Failed to delete files: {delete_response.json()}")
    else:
        print(f"Folder not found: {Config.SHAREPOINT_FOLDER}. No files to delete.")
    