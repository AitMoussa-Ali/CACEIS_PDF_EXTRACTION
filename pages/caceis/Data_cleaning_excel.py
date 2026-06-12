import pandas as pd
from GetToken import get_token
from Sharepoint_handeling.DriverID import get_drive_id
from Sharepoint_handeling.uploader import create_folder, upload_file_to_folder
import dotenv
import io
from utils.Config import Config

df = pd.read_excel(r"C:\Users\aaitmoussa\Desktop\Excel_files\Mouvements_cash.xlsx")
# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def clear_data(df : pd.DataFrame):
    df = df[["Libellé compte cash","Devise compte","Date comptable","Montant mouvement (devise compte)","Description mouvement", "Libellé compte cash"]]
    
    rows = []
    
    
    for row in df.itertuples(index = False):
        new_row_1 = {
            "Libellé compte cash": row[-1],
            "Date": pd.to_datetime(row[2]).strftime("%d/%m/%Y"),        # Date comptable
            "journal": "",         # fill with your desired value
            "Compte": "47100000",      # Libellé compte cash
            "N° Piéce": "",
            "Libellé": row[-2],     # Description mouvement
            "Débit": -1*(row[3]) if row[3] < 0 else "",
            "Crédit": row[3] if row[3] > 0 else "",
            "Monnaie": row[1][0],      # Devise compte
        }
        
        new_row_2 = {
            "Libellé compte cash": row[-1],
            "Date": pd.to_datetime(row[2]).strftime("%d/%m/%Y"),        # Date comptable
            "journal": "",         # fill with your desired value
            "Compte": "51100000",      # Libellé compte cash
            "N° Piéce": "",
            "Libellé": row[-2],     # Description mouvement
            "Crédit": -1*(row[3]) if row[3] < 0 else "",
            "Débit": row[3] if row[3] > 0 else "",
            "Monnaie": row[1][0],      # Devise compte
        }
        
        rows.append(new_row_1)
        rows.append(new_row_2)
        
    new_df = pd.DataFrame(rows, columns=["Libellé compte cash","Date","journal","Compte","N° Piéce", "Libellé", "Débit", "Crédit", "Monnaie"])
    
    return new_df


def upload_single_excel_to_sharepoint(excel_path, fund_name: str, dispo: str, au: str, file_name: str):
    df = pd.read_excel(excel_path)
    new_df = clear_data(df)

    token = get_token()
    drive_id = get_drive_id(token)

    safe_fund_name = fund_name.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-").strip()
    subfolder_name = f"{safe_fund_name}-{dispo.replace('/', '-')}_{au.replace('/', '-')}"
    parent_folder = Config.SHAREPOINT_FOLDER_EXCEL
    full_folder_path = f"{parent_folder}/{subfolder_name}"

    create_folder(token, drive_id, parent_folder, subfolder_name)

    # Serialize DataFrame to Excel bytes in memory
    buffer = io.BytesIO()
    new_df.to_excel(buffer, index=False)
    buffer.seek(0)
    excel_bytes = buffer.read()
    file_name = file_name.replace("/", "-").strip()
    upload_file_to_folder(token, drive_id, full_folder_path, file_name + ".xlsx", excel_bytes)