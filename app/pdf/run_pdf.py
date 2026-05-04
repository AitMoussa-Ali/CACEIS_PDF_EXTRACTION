from playwright.sync_api import sync_playwright
from pages.caceis.login_caseis import Login
from pages.caceis.navigate_caseis_pdf import Navigate_PDF_Caceis
import pandas as pd
from pathlib import Path
import dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # /app
print(f"📁 Base directory: {BASE_DIR}")
def run_extract_pdf(dispo="01/04/2026", au="18/04/2026") -> None:
    df = pd.read_excel(BASE_DIR / "Login_list_for_funds.xlsx", skiprows=1)
    df.columns = df.columns.str.replace(' ', '_')

    caceis = df[(
                df['Banque_dépositaire'] == 'CACEIS') & 
                (
                (df['Email'] == "eric.belloche@groupe-aplitec.com") |
                (df['Email'] == "akim.bouzeboudja@groupe-aplitec.com")
                )]

    dotenv.load_dotenv(BASE_DIR / ".env")

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
            dispo=dispo,
            au=au,
            )
    
        browser.close()