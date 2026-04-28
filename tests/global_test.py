import pandas as pd
import re
from Sharepoint_handeling.LoginFiles import read_excel_from_sharepoint

read_excel_from_sharepoint()

df = pd.read_excel(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\Login_list_for_funds.xlsx", skiprows=1)
df.columns = df.columns.str.replace(' ', '_')

caceis = df[df['Banque_dépositaire'] == 'CACEIS']
caceis = caceis[caceis['Email'] == "eric.belloche@groupe-aplitec.com"]

for row in caceis.itertuples(index=False):
    print(row.Société_de_gestion)