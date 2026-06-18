from playwright.sync_api import sync_playwright
from pages.caceis.login_caseis import Login
from pages.caceis.navigate_caseis_pdf import Navigate_PDF_Caceis
import pandas as pd
from pathlib import Path
import dotenv
from Mailing.AutomateMail import send_email
import os
from Sharepoint_handeling.LoginFiles import read_excel_from_sharepoint
from Sharepoint_handeling.Delete_files import delete_files
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime, timedelta
from utils.Logger import logger
import calendar
from utils.Config import Config

def is_last_day_of_month() -> bool:
    today = datetime.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return last_day == today.day

def get_periodicity() -> str:
    return "MEN : Mensuelle" if is_last_day_of_month() else "QUO : Quotidienne"

def get_week_dates():
    today = datetime.today()
    print(get_periodicity())
    
    if (get_periodicity() == "QUO : Quotidienne"):
        # Previous Saturday
        last_saturday = today - timedelta(days=7)

        de = last_saturday.strftime("%d/%m/%Y")
        au = today.strftime("%d/%m/%Y")

    else:
        de = today.replace(day=1).strftime("%d/%m/%Y")
        last_day_num = calendar.monthrange(today.year, today.month)[1]
        au = today.replace(day=last_day_num).strftime("%d/%m/%Y")
    
    return de, au

societes_de_gestion_mdp_errors = []
societes_de_gestion_refresh_pwd = []


def run_extract_pdf() -> None:

    # Reading the excel file from sharepoint and downloading it to the local folder
    de,au = get_week_dates()
    
    print(f"📅 Running test for date range: {de} to {au}")
    periodicity = get_periodicity()
    if periodicity == "MEN : Mensuelle" : 
        print("Execution en mensuelle ...")
    else : 
        print("Execution en Quotidienne")
    
    df = read_excel_from_sharepoint()
    
    if df is None:
        logger.error("Failed to load Excel file")
        raise RuntimeError("Failed to load Excel from SharePoint")

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
        
        j=0
        for row in caceis.itertuples(index=False):
            flag = True
            i = 0

            if row.Identifiant is None or row.Mot_de_passe is None:
                print(f"❌ Missing identifier for fund {row.Société_de_gestion}, skipping...")
                logger.error(f"❌ Missing identifier for fund {row.Société_de_gestion}")
                societes_de_gestion_mdp_errors.append(row.Société_de_gestion)
                continue


            
            while flag and i < 3 :
                try :
                    print(f"\n\n🚀 Starting navigation for fund: {row.Société_de_gestion}")

                    time.sleep(1)

                    page.goto(row.Adresse_internet)
                    login = login_page.login(row.Identifiant, row.Mot_de_passe)

                    if login == False :
                        societes_de_gestion_refresh_pwd.append(row.Société_de_gestion)
                        print(f"❌ Password needs to be changed for fund {row.Société_de_gestion}, skipping...")
                        logger.error(f"❌ Password needs to be changed for fund {row.Société_de_gestion}")
                        flag = False
                        break
                    
                    
                    try :
                        # Wait for OTP field to appear for the double authentication step
                        flag_pwd = login_page.otp_login(sender=row.Email, timeout=1200)
                        if flag_pwd == False : 
                            societes_de_gestion_refresh_pwd.append(row.Société_de_gestion)
                            flag = False
                        else :
                            # Selection of menu
                            select_page = Navigate_PDF_Caceis(page)

                            result = select_page.full_navigate(
                            fund_name=row.Société_de_gestion,
                            text="Extrait de compte cash",
                            dispo=de,
                            au=au,
                            management_company=row.Société_de_gestion,
                            periodicity=periodicity
                            )
                            if result == row.Société_de_gestion :
                                print(f"Erreur de telechargement des fichiers PDF depuis le site d'OLIS pour la societe {row.Société_de_gestion}")
                                logger.error(f"Erreur de telechargement des fichiers PDF depuis le site d'OLIS pour la societe {row.Société_de_gestion}")
                                break
                            flag = False
                            i = 0
                    except PlaywrightTimeoutError:
                        print(f"OTP not reveived for fund {row.Société_de_gestion}")
                        print(f"Skipping the fund {row.Société_de_gestion}")
                        societes_de_gestion_mdp_errors.append(row.Société_de_gestion)

                except PlaywrightTimeoutError:
                    print(f"💥 Timeout on '{row.Société_de_gestion}'. Re-run the script to resume from here.")
                    logger.error(f"💥 Timeout on '{row.Société_de_gestion}'. Re-run the script to resume from here.")
                    print("Retrying in 3 seconds")
                    time.sleep(3)
                    i+=1
                    if i == 3 :
                        flag = True
                        print(f"💥 3 tries and no response the pdf files of {row.Société_de_gestion} are not downloaded")
                        logger.error(f"💥 3 tries and no response the pdf files of {row.Société_de_gestion} are not downloaded")
                        societes_de_gestion_mdp_errors.append(row.Société_de_gestion)

        print("all the funds are downloaded ")
        if societes_de_gestion_refresh_pwd != [] :
            text = ""
            print("Funds where password needs to be changed are : ")
            for s in societes_de_gestion_refresh_pwd : 
                text += (f"- {s} \n")
            send_email(
                "IMPORTANT : Changement de mots de passe", 
                f"Bonjour, les mots de passes de ses sociétés de gestion doivent être changer : \n {text}",
                ["ali.aitmoussa@groupe-aplitec.com"]
                )
        
        if societes_de_gestion_mdp_errors != [] :
            text = ""
            print("\n Funds where the password is incorrect are :")
            for s in societes_de_gestion_mdp_errors : 
                text += (f"- {s} \n")

            send_email(
                "IMPORTANT : Mots de passe erroné", 
                f"Bonjour, les mots de passes de ses sociétés de gestion sont erroné : \n {text} \n Merci de bien vouloir les mettre a jour",
                [Config.MAIL_SENDER]
                )
    
    
        
        