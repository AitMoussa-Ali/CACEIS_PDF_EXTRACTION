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
    
    def fill_informations(self):
        print("--------------waiting for information page to be charged--------------")
        self.information_page = self.page.locator("iframe").content_frame.locator("#x-auto-61-label")
        self.information_page.wait_for(state="visible")
        print("informations page charged successfully")
        
        print("------------waiting for trigger----------")
        self.input_selection_par = self.page.locator("iframe").content_frame.locator("#x-auto-65-input")
        self.input_selection_par.click()
        self.page.wait_for_timeout(300)
        self.trigger1 = self.page.locator("iframe").content_frame.locator("#x-auto-65 .triggerfield-trigger")
        self.trigger1.click()
        print("the trigger is clicked !")
        self.page.wait_for_timeout(10000)
    
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
    
    def full_navigate(self):
        # Step 1: Generation button
        self.generation_phase()
        self.mes_rapports_phase()
        self.page.wait_for_timeout(10000)
        
        
        
