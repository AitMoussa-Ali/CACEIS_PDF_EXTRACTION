from playwright.sync_api import Page
import dotenv
from pages.caceis.login_caseis import Login
from pages.caceis.navigate_caseis_pdf import Navigate_PDF_Caceis
import pandas as pd
from Sharepoint_handeling.LoginFiles import read_excel_from_sharepoint


vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def test_example(page: Page) -> None:
    # Login
    read_excel_from_sharepoint()
    
    login_page = Login(page)
    
    df = pd.read_excel(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\Login_list_for_funds.xlsx", skiprows=1)
    df.columns = df.columns.str.replace(' ', '_')

    caceis = df[df['Banque_dépositaire'] == 'CACEIS']
        
    for row in caceis.itertuples(index=False):
        
        print(f"\n\n🚀 Starting navigation for fund: {row.Société_de_gestion}")

        page.goto(row.Adresse_internet)
        login_page.login(row.Identifiant, row.Mot_de_passe)

        # Wait for OTP field to appear for the double authentication step
        login_page.otp_login(sender=row.Email)

        # Selection of menu
        select_page = Navigate_PDF_Caceis(page)

        select_page.full_navigate(
        fund_name=row.Société_de_gestion,
        text="Extrait de compte cash",
        dispo="01/04/2026",
        au="04/05/2026",
        )
    
    
    


                                     
                                     
