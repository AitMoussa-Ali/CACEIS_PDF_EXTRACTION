from io import BytesIO

import pandas as pd
import pdfplumber
import re
from pathlib import Path
import json

date_pattern = r"(\d{2}[/-]\d{2}[/-](?:\d{2}|\d{4})|(?:\d{2}|\d{4})[/-]\d{2}[/-]\d{2})"
amount_pattern = r"^\d{1,3}(?:\s\d{3})*(?:[.,]\d{2})$"

path_json = Path(__file__).resolve().parent.parent.parent/"utils"/"Config.json"

def loading_config_json(path_json = path_json):
    with open(path_json, "r", encoding="utf-8") as file:
        data_json = json.load(file)
    return data_json


# Function to generate excel file from a PDF file
def generate_excel_file(dict : dict):
    
    df = pd.DataFrame.from_dict(dict)
    
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    buffer.seek(0)
    return buffer.getvalue()  
  
def extract_tables_from_pdf(pdf_content : bytes, bank_name : str, dict: dict, fund):
    
    data_json = loading_config_json()
    indexes = data_json[bank_name]
    tables = []
    columns = indexes["columns"]

            
    def is_a_valid_row(row, columns):
        try:
            return (
                re.match(date_pattern, (row[columns["Date"]])) and
                re.match(date_pattern, str(row[columns["Date_valeur"]]))
            )
        except:
                return False
    
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    
    clean_rows = []
    for row in tables:
        clean_rows.extend([r for r in row if is_a_valid_row(r, columns)])
        
    
    for row in clean_rows:
        # Premiere ligne
        dict['Date'].append(row[columns["Date"]])

        dict["Compte"].append(4710000)
        
        dict['Libellé'].append(row[columns["Libellé"]["index"]][:50])
        if row[columns["Débit"]] : 
            dict['Débit'].append(row[columns["Débit"]])
        else : 
            dict['Débit'].append(0)
        if row[columns["Crédit"]] : 
            dict["Crédit"].append(row[columns["Crédit"]]) 
        else : 
            dict["Crédit"].append(0)
            
        dict["Monnaie"].append("E")
        dict["Journal"].append(fund)
        dict["N° Piéce"].append("")
            
            
        #Doublement de ligne
        dict['Date'].append(row[columns["Date"]])
        dict['Libellé'].append(row[columns["Libellé"]["index"]])
        
        if row[columns["Crédit"]] : 
            dict['Débit'].append(row[columns["Crédit"]])
        else : 
            dict['Débit'].append(0)
            
        if row[columns["Débit"]] : 
            dict["Crédit"].append(row[columns["Débit"]]) 
        else : 
            dict["Crédit"].append(0)
            
        dict["Compte"].append(51100000)
        dict["N° Piéce"].append("")
        dict["Monnaie"].append("E")
        dict["Journal"].append(fund)
    
    dict['Débit'].append("")
    dict["Crédit"].append("")
    dict['Date'].append("")
    dict['Libellé'].append("")
    dict["Compte"].append("")
    dict["N° Piéce"].append("")
    dict["Monnaie"].append("")
    dict["Journal"].append("")
            

def generate_excel_content_from_pdf(bank_name, excel_data, funds):
    
    dict = {
        "Date": [],
        "Journal":[],
        "Compte":[],
        "N° Piéce":[],
        "Libellé": [],
        "Débit": [],
        "Crédit": [],
        "Monnaie":[],
    }
    
    for data, fund in zip(excel_data, funds) :
        extract_tables_from_pdf(data, bank_name, dict, fund)
    
    excel_content = generate_excel_file(dict)
    
    
    return excel_content