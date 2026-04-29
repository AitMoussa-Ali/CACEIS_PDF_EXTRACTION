import dotenv
import requests
vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")
import os
def get_drive_id(token: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    
    site_url = vars["SHAREPOINT_SITE_URL"]

    site_response = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_url}",
        headers=headers
    )
    site_id = site_response.json()["id"]

    drives_response = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives",
        headers=headers
    )
    drives = drives_response.json().get("value", [])
    return drives[0]["id"]

def get_drive_id_excel(token:str)-> str:
    headers = {"Authorization": f"Bearer {token}"}
    # site_url = vars["SHAREPOINT_SITE_URL"]

    site_response = requests.get(
        f"https://graph.microsoft.com/v1.0/drives",
        headers=headers
    )
    site_id = site_response.json()["value"][0]["id"]

    return site_id
