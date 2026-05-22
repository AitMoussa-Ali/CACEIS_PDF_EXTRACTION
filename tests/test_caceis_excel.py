from playwright.sync_api import Page
import dotenv
from pages.caceis.login_caseis import Login
from pages.caceis.navigate_caceis_excel import Navigate_Excel_Caceis
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
df = pd.read_excel(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\Login_list_for_funds.xlsx", skiprows=1)
df.columns = df.columns.str.replace(' ', '_')

caceis = df[df['Banque_dépositaire'] == 'CACEIS']

vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def test_example(page: Page) -> None:
    # Login
    login_page = Login(page)
    page.set_default_timeout(10000) #10 seconds of waiting for maximum
    
    for row in caceis.itertuples(index=False):
        flag = True
        while flag :
            
            try :
            
                print(f"\n\n🚀 Starting navigation for fund: {row.Société_de_gestion}")
                # 🔄 Reset page state before each attempt
                page.goto("about:blank")
                time.sleep(2)
                
                page.goto(row.Adresse_internet)
                login_page.login(row.Identifiant, row.Mot_de_passe)

                # Wait for OTP field to appear for the double authentication step
                login_page.otp_login(sender=row.Email)

                # Selection of menu
                select_page = Navigate_Excel_Caceis(page)

                select_page.full_navigate(dispo="01/04/2026",au = "05/05/2026", fund_name=row.Société_de_gestion)

                flag = False
            
            except PlaywrightTimeoutError:
                
                print(f"💥 Timeout on '{row.Société_de_gestion}'. Re-run the script to resume from here.")
                print("Retrying in 3 seconds")
                time.sleep(3)
        
        
    
    
    


                                     
                                     
