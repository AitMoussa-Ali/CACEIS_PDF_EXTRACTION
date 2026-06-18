import os
import requests
from GetToken import get_token
from Sharepoint_handeling.DriverID import get_drive_id
import pandas as pd
import io
from utils.Config import Config

# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

# def read_excel_from_sharepoint() -> pd.DataFrame:
#     token = get_token()
#     drive_id = get_drive_id(token)
    
    
#     file_path = Config.PATH_LOGIN_FILE
#     sheet_name = Config.SHEET_LOGIN_NAME
#     LOCAL_PATH = Config.LOCAL_PATH_LOGIN_FILE_SHEET
#     headers = {"Authorization": f"Bearer {token}"}

#     # Download the file as bytes in memory
#     try:
        
#         response = requests.get(
#             f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_path}/{sheet_name}:/content",
#             headers=headers
#         )
#         with open(LOCAL_PATH, "wb") as f:
#             f.write(response.content)
#         print(f"✅ File downloaded successfully to {LOCAL_PATH}")
            
#     except Exception as e:
#         print(f"Error downloading file: {e}")
#         return None

def read_excel_from_sharepoint() -> pd.DataFrame:
    token = get_token()
    drive_id = get_drive_id(token)
    
    file_path = Config.PATH_LOGIN_FILE
    sheet_name = Config.SHEET_LOGIN_NAME
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_path}/{sheet_name}:/content",
            headers=headers
        )
        response.raise_for_status()
        
        df = pd.read_excel(io.BytesIO(response.content), skiprows=1)
        df.columns = df.columns.str.replace(' ', '_')
        df = df.where(pd.notnull(df), None)
        
        print("✅ File read successfully from SharePoint")
        return df
            
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    