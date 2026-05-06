from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import re 
from datetime import datetime
import pandas as pd
import time
from pages.caceis.Data_cleaning_excel import upload_single_excel_to_sharepoint
class Navigate_Excel_Caceis :    
    
    def __init__(self, page: Page):
        self.page = page

        # Page level — OK in __init__
        self.menu = page.locator("[data-test='menu-entry-MENU']")
        self.menu_item = page.locator("[data-test='menu-item']").filter(has_text="MES RAPPORTS").first
        self.mes_rapports = self.page.locator("a[data-test='menu-item'] span.ols-menu-item-label") \
            .filter(has_text=re.compile(r"^\s*Mes Rapports\s*$", re.IGNORECASE)).nth(1)
        self.logout = page.locator("li:nth-child(7) > .p-element")
        self.generation_time = 0


        #Generation phase
        self.generation = self.page.locator("a[data-test='menu-item'] span.ols-menu-item-label") \
            .filter(has_text=re.compile(r"^\s*Génération\s*$"))
        # self.generation_page =
        
        # Non-iframe helpers
        self.date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")
        
    def loading_spin_reports(self):
        self.loading = (
        self.page.locator("iframe[src*='eventName=myreports']")
        .content_frame
        .locator(".mask-box .mask-text")
        .filter(has_text="tab")
        )
        
        self.loading.wait_for(state="visible", timeout=60000)
        print("loading started...")
        # Now wait for it to disappear
        self.loading.wait_for(state="hidden", timeout=60000)
        print("loading finished ....")
        
    def loading_spin_generation(self):
        self.loading = (
        self.page.locator("iframe[src*='eventName=generation']")
        .content_frame
        .locator(".mask-box .mask-text")
        .filter(has_text="tab")
        )
        
        self.loading.wait_for(state="visible", timeout=60000)
        print("loading started...")
        # Now wait for it to disappear
        self.loading.wait_for(state="hidden", timeout=60000)
        print("loading finished ....")
        
            
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
        self.date_du = self.page.locator("iframe").content_frame.locator("div.x-field-component:has(.x-th:text-is('Du')) input")
        self.date_au = self.page.locator("iframe").content_frame.locator("div.x-field-component:has(.x-th:text-is('Au')) input")
        self.date_au.wait_for(state='visible')
        print("selecting dates.............................")
        self.date_du.fill(du)
        self.date_au.fill(au)
        print("dates are selected successfully !")
        
    def select_language(self):
        print("selecting language")
        self.language = self.page.locator("iframe").content_frame.locator("div.x-field-component:has(.x-th:text-is('Langue')) input")
        self.language.fill("Français")
        print("language selected !")
    
    def fill_informations(self, dispo, au):
        print("--------------waiting for information page to be charged--------------")
        self.trigger_selection_par = self.page.locator("iframe").content_frame.locator("div.x-field-component:has(.x-th:text-is('Sélection par')) input")
        self.trigger_selection_par.wait_for(state="visible")
        print("--------------waiting for information page charged !!!! --------------")
        print("------------selecting compte cash----------")
        self.trigger_selection_par.fill("Compte cash")
        print("------------compte cash selected !!!!!------------")
        
        self.select_dates(du=dispo, au=au)
        self.select_language()
        
        self.button_generation = self.page.locator("iframe").content_frame.get_by_role("button", name="Generate Dynamic Report")
        
        print("clicking on generation button")
        # self.button_generation.click()
        # self.loading_spin_generation()
        print("generation of excel file is done by clicking the button ...")
        self.generation_time = datetime.now()
        
    def generation_phase(self, dispo, au):
        
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
        
        self.fill_informations(dispo, au)
        
    def parse_date(self, date_str: str):
        return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S:%f")
    
    def download_excel_file(self, dispo, au, fund_name):
        try:
            self.elements = (
            self.page.locator("iframe[src*='eventName=myreports']")
            .content_frame
            .locator("#mainBody").get_by_text("Mouvements cash.xlsx")
            ).first
            
            flag = False
            while(flag == False):
                print("button search is clicked")
                self.loading_spin_reports()
                
                if(self.elements.is_visible() == True):
                    flag = True
                #     self.time_generation_file = (
                #     self.page.locator("iframe[src*='eventName=myreports']")
                #     .first
                #     .content_frame
                #     .locator("td:nth-child(9) > .grid-cellinner > .cellContainer").first.inner_text()
                #     )
                    
                #     self.time_generation_file = self.parse_date(self.time_generation_file)

                #     print(f"-----------------generation file time : {self.time_generation_file}------------------")
                #     print(f"-----------------generation script time : {self.generation_time}------------------")
                    
                #     print(f"the difference is {abs((self.time_generation_file - self.generation_time).total_seconds())}")
                    
                #     if( abs((self.time_generation_file - self.generation_time).total_seconds()) < 60 ):
                #         print("file found !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                #         flag=True
                #         break
                    
                    
                # print("no results, clicking on the search button after 5 seconds")
                else : 
                    print("no results, clicking on the search button after 5 seconds")
                    
                time.sleep(5)
                self.search_button.click()
            
            print("loaded !!!!!!")
            
            file_checked = (
            self.page.locator("iframe[src*='eventName=myreports']")
            .content_frame
            .locator(".grid-cellinner").first
            )
            
            file_checked.click()
            self.download_button = (
                                    self.page.locator("iframe[src*='eventName=myreports']")
                                    .first
                                    .content_frame
                                    .get_by_text("Télécharger")
                                    )
            self.download_button.wait_for(state="visible")
            print(f"⬇️ Downloading excel file:")
            
            with self.page.expect_download() as download_info:
                self.download_button.click()
            
            download = download_info.value
            file_path = download.path()
            file_name = fund_name+"_"+dispo.replace("/", "-")+"_"+au.replace("/", "-")
            upload_single_excel_to_sharepoint(file_path, fund_name, dispo, au, file_name)
            
        except PlaywrightTimeout:
            # Loading spinner never appeared or already gone
            print("loaded (no spinner detected)")
        
    def mes_rapports_phase(self, dispo, au, fund_name):
        print("----------------------------------EXCEL GENERATION PHASE----------------------------------")
        self.select_menu()
        self.mes_rapports.wait_for(state="visible")
        self.mes_rapports.click()
        print("Returning to mes rapports has been done successfully")

        print("waiting for excel reports page to be download")
        self.loading_spin_reports()
        
        print("report excel pages is loaded")

        # ✅ Target the specific iframe instead of a generic locator("iframe")
        self.search_button = (
            self.page.locator("iframe[src*='eventName=myreports']")
            .content_frame
            .locator("#b02--448c7e14-t1")
            .first
        )
        self.search_button.wait_for(state='visible')
        print("the search button is visible")
        self.search_button.click()

        # Wait for loading to appear (it might be brief, so use a short timeout)
        self.download_excel_file(dispo, au, fund_name=fund_name)
        
    def full_navigate(self, dispo, au, fund_name):
        # Step 1: Generation button
        self.generation_phase(dispo=dispo, au=au)
        self.mes_rapports_phase(dispo=dispo, au=au, fund_name=fund_name)
        self.page.wait_for_timeout(5000)
        
        
        
