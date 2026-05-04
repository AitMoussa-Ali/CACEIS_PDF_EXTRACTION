from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import re 
from datetime import datetime


class Navigate_Excel_Caceis :    
    
    def __init__(self, page: Page):
        self.page = page

        # Page level — OK in __init__
        self.menu = page.locator("[data-test='menu-entry-MENU']")
        self.menu_item = page.locator("[data-test='menu-item']").filter(has_text="MES RAPPORTS").first
        self.generation = self.page.locator("a[data-test='menu-item'] span.ols-menu-item-label") \
            .filter(has_text=re.compile(r"^\s*Génération\s*$"))
        self.mes_rapports = self.page.locator("a[data-test='menu-item'] span.ols-menu-item-label") \
            .filter(has_text=re.compile(r"^\s*Mes Rapports\s*$", re.IGNORECASE)).nth(1)
        self.logout = page.locator("li:nth-child(7) > .p-element")

        # Non-iframe helpers
        self.date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")
        self.time_of_excel_file = 0

    # All iframe-dependent locators as @property
    @property
    def generation_frame(self):
        return self.page.locator("iframe[src*='eventName=generation']").content_frame

    @property
    def reports_frame(self):
        return self.page.locator("iframe[src*='eventName=myreports']").content_frame

    @property
    def description(self):
        return self.generation_frame.locator("td.columnheader-header:has(span.gwt-InlineHTML)") \
            .filter(has_text=re.compile(r"Code du business / Presentation Identifier / Nom"))

    @property
    def mouvement_cash(self):
        return self.generation_frame.locator("tr.grid-row") \
            .filter(has_text=re.compile(r"Mouvements\s*cash", re.IGNORECASE))

    @property
    def choose_param_button(self):
        return self.generation_frame.get_by_role("button", name="Choisir les paramètres")

    @property
    def table_param(self):
        return self.generation_frame.get_by_role("table") \
            .filter(has_text="User Agac Sélection par Tous")

    @property
    def cash_selection(self):
        return self.generation_frame.locator("#x-auto-65 > .triggerfield-wrap > .triggerfield-trigger")

    @property
    def compte_cash_option(self):
        return self.generation_frame.get_by_text("Compte cash")

    @property
    def language_selection(self):
        return self.generation_frame.locator("#x-auto-80 > .triggerfield-wrap > .triggerfield-trigger")

    @property
    def french_selection(self):
        return self.generation_frame.get_by_text("Français")

    @property
    def start_date(self):
        return self.generation_frame.locator("[id='80000082-input']")

    @property
    def end_date(self):
        return self.generation_frame.locator("[id='80000083-input']")

    @property
    def generate_report(self):
        return self.generation_frame.get_by_role("button", name="Generate Dynamic Report")

    @property
    def generation_report_body(self):
        return self.generation_frame.locator("div.PJOE2YC-e-e") \
            .filter(has_text="Dernières recherches")

    @property
    def search_button(self):
        return self.reports_frame.locator("#b02--448c7e14-t1")

    @property
    def reports_table(self):
        return self.reports_frame.locator("div") \
            .filter(has_text=re.compile(r"^Custody$")).nth(1)

    @property
    def generation_time(self):
        return self.reports_frame.locator(
            "td:nth-child(9) > .grid-cellinner > .cellContainer"
        ).first
    
    def select_menu(self):
        # Step 1: click to open the menu
        self.menu.click(delay=30)
        
        # Step 2: wait for menu items to be fully visible
        self.menu_item.wait_for(state="visible")

        # Step 3: scroll into view first, then hover slowly
        self.menu_item.scroll_into_view_if_needed()

        # Step 4: move mouse to the item slowly using position
        self.menu_item.hover(timeout=3000)

        # Step 5: wait a bit for the submenu to fully expand
        self.page.wait_for_timeout(500)

        # Step 6: wait for the submenu link and click
        self.generation.wait_for(state="visible")
        self.generation.click()
       
    def select_cash(self):
        
        while(self.description.is_visible() == False):
            print("waiting for the table to be charged")
            self.page.wait_for_timeout(1000)
        
        print("✅ table of choosing the parameteres is charged successfully !!")
        self.page.wait_for_timeout(1000)
        print("selection of mouvement cash ........")
        self.mouvement_cash.scroll_into_view_if_needed()
        
        while self.mouvement_cash.is_visible() == False :
            print("waiting for the button cash movements.....")
            self.page.wait_for_timeout(1000)
    
        self.mouvement_cash.click()
        print("✅ mouvement cash selected")
        self.choose_param_button.scroll_into_view_if_needed()
        self.choose_param_button.click()
        print("✅ button params clicked")
        self.page.wait_for_timeout(5000)        
        
    def select_dates(self, du, au):
        for field, value in [
            (self.start_date, du),
            (self.end_date, au)
        ]:
            field.wait_for(state="visible")
            # safer than click+type loop
            field.click()
            field.wait_for(timeout=2000)  # small delay to ensure focus
            field.press("Control+A")
            field.wait_for(timeout=2000)  # small delay to ensure selection
            field.press("Backspace")
            field.wait_for(timeout=2000)  # small delay to ensure selection
            
            # optional safety check (rarely needed)
            while not self.date_pattern.match(field.input_value()):
                field.fill(value)
                
            field.wait_for(timeout=2000)  # small delay to ensure selection
            field.press("Tab")   
            
        print("dates are selected correctly") 
        
    def select_parameters(self):
        
        self.table_param.wait_for(state="visible")
        
        while(self.cash_selection.is_visible() == False) : 
            print("Waiting for the page of mouvements cash to be fully charged")
            
        self.cash_selection.click()
        # option = self.frame.locator("#xComptecash")
        # print(option)
        while(self.compte_cash_option.is_visible() == False):
            print("waiting for the option compte cash to be visible .... ")
            self.page.wait_for_timeout(1000)
        self.compte_cash_option.click()
        print("compte cash is selected ✅")
    
    def select_language_and_generate(self):
        self.language_selection.wait_for(state="visible")
        self.language_selection.click()
        self.french_selection.click()
        print("The language has been selected successfully ✅ !!")
        
        self.generate_report.wait_for(state="visible")
        now = datetime.now()
        self.time_of_excel_file = now.strftime("%d/%m/%Y %H:%M:%S:") + f"{now.microsecond // 1000:03d}"
        # self.generate_report.click()
        print("Generate button has been clicked successfully ✅ !!")
        
    def parse_date(self, date_str):
        
        dt, ms = date_str.rsplit(":", 1)
        return datetime.strptime(dt, "%d/%m/%Y %H:%M:%S").replace(
        microsecond=int(ms) * 1000
    )
    
    def return_to_reporting(self):
        # Step 1: click to open the menu
        self.menu.click(delay=30)
        
        # Step 2: wait for menu items to be fully visible
        self.menu_item.wait_for(state="visible")

        # Step 3: scroll into view first, then hover slowly
        self.menu_item.scroll_into_view_if_needed()

        # Step 4: move mouse to the item slowly using position
        self.menu_item.hover(timeout=3000)

        # Step 5: wait a bit for the submenu to fully expand
        self.page.wait_for_timeout(2000)
        
        #selecting MES RAPPORTS
        self.mes_rapports.click()
        
    def download_excel_file(self):
        print(">>>>>>> Waiting for the body of report generation to load .....")
        print(self.generation_report_body)
        self.generation_report_body.wait_for(state="visible")
        # print("visible")
        # count = self.generation_report_body.count()
        # print(count)
        # self.generation_report_body.wait_for(state="visible")
        # print("The body of report generation is loaded ✅ !!")
        # print(">>>>>>> Waiting for the search button to be visible ....")
        # self.search_button.wait_for(state="visible")
        # print("The search button is visible ✅")
        # self.search_button.click()
        # print("The search button has been clicked successfully ✅")
        # print(">>>>>>> Waiting for the report table to be loaded.....")
        # self.reports_table.wait_for(state="visible")
        # print("The report table is loaded ✅")
        
        # print(">>>>>>> Waiting for the generation time to be visible ....")
        # while(self.generation_time.is_visible() == False):
        #     print("waiting fo reporting results ...")
        #     self.page.wait_for_timeout(5000)
        #     self.search_button.click()
        #     self.reports_table.wait_for(state="visible")
            
        # print("reporting results are visible now")
        
        # text = self.generation_time.inner_text()
        # print("Date enregistrer par le script", self.time_of_excel_file)
        # print("Date metier of the last file : ", text)
        
        # while(abs(self.parse_date(text) - self.parse_date(self.time_of_excel_file)).total_seconds() > 5):
        #     print("Waiting for excel file generation")
        #     self.search_button.click()
        #     self.reports_table.wait_for(state="visible")
        #     self.generation_time.wait_for(state="visible")
        #     text = self.generation_time.inner_text()
        
        print("Excel file generated ✅")
        
    def full_navigate(self):
        self.select_menu()
        self.select_cash()
        self.select_parameters()
        self.select_dates(du = "01/04/2026", au = "18/04/2026")
        self.select_language_and_generate()
        print("report generation button has been clicked successfully ✅")
        self.return_to_reporting()
        
