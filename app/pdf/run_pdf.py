from playwright.sync_api import sync_playwright
from pages.caceis.login_caseis import Login
from pages.caceis.navigate_caseis_pdf import Navigate_PDF_Caceis
import pandas as pd
from pathlib import Path
import dotenv
import os
from Sharepoint_handeling.LoginFiles import read_excel_from_sharepoint
from Sharepoint_handeling.Delete_files import delete_files
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # /app
print(f"📁 Base directory: {BASE_DIR}")
societes_de_gestion = []

societes_de_gestion_mdp_errors = []
societes_de_gestion_refresh_pwd = []

def run_extract_pdf(dispo="01/04/2026", au="18/04/2026") -> None:
    #Deleting the files in the download folder before downloading new ones
    # This is to avoid having multiple files in the download folder and to make sure that we
    print("deleting files..........")
    delete_files()
    
    # Reading the excel file from sharepoint and downloading it to the local folder
    read_excel_from_sharepoint()
    
    df = pd.read_excel(BASE_DIR / "Login_list_for_funds.xlsx", skiprows=1)
    df.columns = df.columns.str.replace(' ', '_')

    caceis = df[df['Banque_dépositaire'] == 'CACEIS']


    with sync_playwright() as p:
        browser = p.chromium.launch(
                                    headless=True,
                                    args=[
                                        "--lang=fr-FR",
                                        "--disable-features=Translate",
                                        "--disable-blink-features=AutomationControlled",  # hides headless detection
                                        "--no-sandbox",
                                        "--disable-dev-shm-usage",
                                    ]
                                    )
        context = browser.new_context(
                                    locale="fr-FR",
                                    extra_http_headers={"Accept-Language": "fr-FR,fr;q=0.9"},
                                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                                    viewport={"width": 1080, "height": 800}  # headless default is too small sometimes
        )
        
        
        
        page = context.new_page()

        login_page = Login(page)
        
        

        # for row in caceis.itertuples(index=False):
        #     flag = True
        #     i = 0
        #     while flag and i < 3 :
        #         try :
        #             print(f"\n\n🚀 Starting navigation for fund: {row.Société_de_gestion}")

        #             page.goto("about:blank")
        #             time.sleep(2)

        #             page.goto(row.Adresse_internet)
        #             login_page.login(row.Identifiant, row.Mot_de_passe)


        #             try :
        #                 # Wait for OTP field to appear for the double authentication step
        #                 login_page.otp_login(sender=row.Email)
        #             except :
        #                 print(f"OTP not reveived for fund {row.Société_de_gestion}")
        #                 print(f"Skipping the fund {row.Société_de_gestion}")
        #                 societes_de_gestion.append(row.Société_de_gestion)


        #             # Selection of menu
        #             select_page = Navigate_PDF_Caceis(page)

        #             select_page.full_navigate(
        #             fund_name=row.Société_de_gestion,
        #             text="Extrait de compte cash",
        #             dispo=dispo,
        #             au=au,
        #             )

        #             flag = False
        #             i = 0
        #         except PlaywrightTimeoutError:
        #             print(f"💥 Timeout on '{row.Société_de_gestion}'. Re-run the script to resume from here.")
        #             print("Retrying in 3 seconds")
        #             time.sleep(3)
        #             i+=1
        #             if i == 3 :
        #                 flag = True
        #                 print(f"💥 3 tries and no response the pdf files of {row.Société_de_gestion} are not downloaded")
        #                 societes_de_gestion.append(row.Société_de_gestion)
        for row in caceis.itertuples(index=False):
            flag = True
            i = 0
            while flag and i < 3 :
                try :
                    print(f"\n\n🚀 Starting navigation for fund: {row.Société_de_gestion}")

                    page.goto("about:blank")
                    time.sleep(2)

                    page.goto(row.Adresse_internet)
                    login_page.login(row.Identifiant, row.Mot_de_passe)


                    try :
                        # Wait for OTP field to appear for the double authentication step
                        flag_pwd = login_page.otp_login(sender=row.Email)
                        if flag_pwd == False : 
                            societes_de_gestion_refresh_pwd.append(row.Société_de_gestion)
                            flag = False
                        else :
                            # Selection of menu
                            select_page = Navigate_PDF_Caceis(page)

                            select_page.full_navigate(
                            fund_name=row.Société_de_gestion,
                            text="Extrait de compte cash",
                            dispo=dispo,
                            au=au,
                            )

                            flag = False
                            i = 0
                    except :
                        print(f"OTP not reveived for fund {row.Société_de_gestion}")
                        print(f"Skipping the fund {row.Société_de_gestion}")
                        societes_de_gestion_mdp_errors.append(row.Société_de_gestion)

                except PlaywrightTimeoutError:
                    print(f"💥 Timeout on '{row.Société_de_gestion}'. Re-run the script to resume from here.")
                    print("Retrying in 3 seconds")
                    time.sleep(3)
                    i+=1
                    if i == 3 :
                        flag = True
                        print(f"💥 3 tries and no response the pdf files of {row.Société_de_gestion} are not downloaded")
                        societes_de_gestion_mdp_errors.append(row.Société_de_gestion)

        if societes_de_gestion == [] : 
            print("All the funds has been downloaded")
        else : 
            print("All the funds has been downloaded except : ")
            for s in societes_de_gestion:
                print(f" - {s} \n ")
                
        browser.close()