from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import re 
from datetime import datetime


class Navigate_Excel_Caceis :    
    
    def __init__(self, page: Page):
        self.page = page

        # Page level — OK in __init__
        self.menu = page.locator("[data-test='menu-entry-MENU']")
        self.menu_item = page.locator("[data-test='menu-item']").filter(has_text="MES RAPPORTS").first
        self.mes_rapports = self.page.locator("a[data-test='menu-item'] span.ols-menu-item-label") \
            .filter(has_text=re.compile(r"^\s*Mes Rapports\s*$", re.IGNORECASE)).nth(1)
        self.logout = page.locator("li:nth-child(7) > .p-element")


        #Generation phase
        self.generation = self.page.locator("a[data-test='menu-item'] span.ols-menu-item-label") \
            .filter(has_text=re.compile(r"^\s*Génération\s*$"))
        # self.generation_page =
        
        # Non-iframe helpers
        self.date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")
        
    def select_menu(self):
        # Step 1: click to open the menu
        self.menu.click(delay=30)
        print("menu button clicked !!")
        
        # Step 2: wait for menu items to be fully visible
        self.menu_item.wait_for(state="visible")
        print("menu is visible !")
        
        # Step 3: scroll into view first, then hover slowly and hover
        self.menu_item.scroll_into_view_if_needed()
        self.menu_item.hover()
    
    def select_dates(self, du, au):
        print("selecting dates.............................")
        self.date_du = self.page.locator("iframe").content_frame.locator("[id=\"80000082-input\"]")
        self.date_au = self.page.locator("iframe").content_frame.locator("[id=\"80000083-input\"]")
        self.date_du.fill(du)
        self.date_au.fill(au)
        print("dates are selected successfully !")
        
    def select_language(self):
        print("selecting language")
        self.language = self.page.locator("iframe").content_frame.locator("#x-auto-80-input")
        self.language.fill("Français")
        print("language selected !")
    
    def fill_informations(self):
        print("--------------waiting for information page to be charged--------------")
        self.information_page = self.page.locator("iframe").content_frame.locator("#x-auto-61-label")
        self.information_page.wait_for(state="visible")
        print("informations page charged successfully")
        
        print("------------selecting compte cash----------")
        frame = self.page.locator("iframe[src*='eventName=generation']").content_frame
        self.trigger_selection_par = self.page.locator("iframe").content_frame.locator("#x-auto-65-input")
        self.trigger_selection_par.fill("Compte cash")
        print("------------compte cash selected------------")
        
        self.select_dates(du="01/04/2026", au="18/04/2026")
        self.select_language()
        
        self.button_generation = self.page.locator("iframe").content_frame.get_by_role("button", name="Generate Dynamic Report")
        
        print("clicking on generation button")
        # self.button_generation.click()
        print("generation of excel file is done by clicking the button ...")
        
        self.page.wait_for_timeout(5000)

    def generation_phase(self):
        
        print("----------------------------------GENERATION PHASE----------------------------------")
        
        self.select_menu()
        
        self.generation.wait_for(state="visible")
        self.generation.click()
        print("generation button clicked")
        self.generation_page = self.page.locator("iframe").content_frame.get_by_text("Rapports correspondant à vos")
        print("waiting for generation page")
        self.generation_page.wait_for(state="visible")
        print("generation page is visible !")
        
        print("\n Selecting movement cash ......")
        self.mouvement_cash_button = self.page.locator("iframe").content_frame.locator("tr:nth-child(10) > .grid-cell.PJOE2YC-z-a.x-grid-cell-first > .grid-cellinner")
        self.mouvement_cash_button.wait_for(state="visible")
        self.mouvement_cash_button.click()
        print("Mouvement cash selected successfully !")
        
        print("Clicking on the generation button ...")
        self.choisir_les_parametres_button = self.page.locator("iframe").content_frame.get_by_role("button", name="Choisir les paramètres")
        
        self.choisir_les_parametres_button.wait_for(state="visible")
        print("the button of choosing parametres is visible")
        self.choisir_les_parametres_button.click()
        print("the button of choosing parametres is clicked")
        
        self.fill_informations()
        
    def mes_rapports_phase(self):
        print("----------------------------------EXCEL GENERATION PHASE----------------------------------")
        self.select_menu()
        self.mes_rapports.wait_for(state="visible")
        self.mes_rapports.click()
        print("Returning to mes rapports has been done successfully")
        
        # self.rapports_excel = self.page.locator("iframe").content_frame.locator("div.PJOE2YC-E-e:has-text('Dernières recherches')")
        frame = self.page.frame(url="*eventName=generation*")
        elements = frame.get_by_text("Dernières recherches").all()
        print(f"FOUND {len(elements)} elements")
        # self.rapports_excel.wait_for(state="visible")
        print("the page of excel reports is loaded successfully !")
    
    def full_navigate(self):
        # Step 1: Generation button
        self.generation_phase()
        self.mes_rapports_phase()
        self.page.wait_for_timeout(5000)
        
        
        
