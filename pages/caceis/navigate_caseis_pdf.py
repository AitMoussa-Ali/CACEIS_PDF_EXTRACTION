from dataclasses import field

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import time
from Sharepoint_handeling.uploader import upload_single_pdf_to_sharepoint
import re

class Navigate_PDF_Caceis:
    def __init__(self, page: Page):
        self.page = page

        # Navigation elements (lazy, no content_frame)
        self.menu = page.locator("[data-test='menu-entry-MENU']")
        self.menu_item = page.locator("[data-test='menu-item']").filter(has_text="MES RAPPORTS")

        self.menu_rapport = page.locator("[data-test='mega-menu-content'] a").filter(has_text="Rapports standards")

        # All iframe locators using frame_locator (consistent + lazy)
        self.frame = page.frame_locator("iframe").frame_locator("iframe[name='firstTabiframe']")

        self.select_document   = self.frame.locator("#ext-gen47")
        self.dispoonibility    = self.frame.get_by_role("textbox", name="* Disponible depuis le :")
        self.date_au           = self.frame.get_by_role("textbox", name="* au :")
        self.rechercher        = self.frame.locator("#submit").get_by_role("cell", name="Rechercher")
        self.download          = self.frame.locator("#telecharger").get_by_role("cell", name="Télécharger")
        self.error             = self.frame.get_by_role("cell", name="ERREUR", exact=True)
        self.check_boxes = self.frame.get_by_role("row")

        # All iframe1 locators using frame_locator (consistent + lazy)
        self.frame1 = page.locator("iframe").first.content_frame.locator("iframe[name=\"firstTabiframe\"]").content_frame
        self.table             = self.frame1.get_by_text("1", exact=True)
        self.periodicity       = self.frame.get_by_role("textbox", name="Périodicité :")
        
        self.files_names = self.frame.locator("div:not(:has(div))").filter(has_text=re.compile(r'^\d{11}/\d{11}'))
        self.next_button = self.frame1.locator("#ext-gen215")
        
        self.logout = page.locator("li:nth-child(7) > .p-element")
        
        self.date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")  # pattern to extract dates from fund name

# Function to select menu items with proper waiting
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
        self.menu_rapport.wait_for(state="visible")
        self.menu_rapport.click()

# Function to select document type with proper waiting
    def select_type_document(self, text):
        self.select_document.click()
        option = self.frame.get_by_text(text)
        option.wait_for(state="visible")
        option.click()
        
# Function to select the periodicity
    def select_periodicity(self, periodicity="MEN : Mensuelle"):
        self.periodicity.click()
        option = self.frame.get_by_text(periodicity)
        option.wait_for(state="visible")
        option.click()
        
        
# Function to select dates with proper waiting and error handling 
    def select_dates(self, dispo, au):
        for field, value in [
            (self.dispoonibility, dispo),
            (self.date_au, au)
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
            
            
# Function to select all checkboxes in the results table
    def select_all_checkboxes(self):
        for row in self.check_boxes.all():
            checkbox = row.get_by_role("checkbox")
            if checkbox.count() > 0 and not checkbox.is_checked():
                checkbox.check()

# Function to wait for either results or error, then act accordingly
    
    def wait_for_results(self, dispo: str, au: str, fund_name: str):
        while self.table.is_visible() == False and self.error.is_visible() == False:
            print("Waiting for results or error...")
            self.page.wait_for_timeout(1000)

        if self.error.is_visible():
            print("No document found.")
            return False
        else:
            print("Documents found, processing downloads...")

        text_for_pages = self.frame.get_by_text("sur").first.inner_text()
        print("Text for pages:", text_for_pages)
        match = re.search(r"sur\s+(\d+)", text_for_pages)
        number_of_pages = int(match.group(1)) if match else 1
        print(f"Total pages: {number_of_pages}")

        for i in range(1, number_of_pages + 1):
            print(f"\n📄 Page {i}/{number_of_pages}")

            rows = self.check_boxes.all()
            checkbox_rows = [r for r in rows if r.get_by_role("checkbox").count() > 0]

            already_downloaded = set()

            for row in checkbox_rows:
                row_text = row.inner_text().strip()

                # Extract fund code from row text to use as unique key
                code_match = re.search(r'(\d{11})/\d{11}', row_text)
                if not code_match:
                    continue

                fund_code = code_match.group(1)

                # Skip if already downloaded
                if fund_code in already_downloaded:
                    print(f"⏭️ Skipping duplicate: {fund_code}")
                    continue

                already_downloaded.add(fund_code)

                # Build clean filename from row text
                name_match = re.search(r'(\d{11}/\d{11}.*?)(?:\n|$)', row_text)
                if not name_match:
                    continue
                full_name = name_match.group(1).strip()
                fund_code = full_name.split('/')[0]
                file_name = full_name.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-").strip()

                # Uncheck all, then check only this row
                for r in checkbox_rows:
                    cb = r.get_by_role("checkbox")
                    if cb.count() > 0 and cb.is_checked():
                        cb.uncheck()

                row.get_by_role("checkbox").check()

                print(f"⬇️ Downloading: {file_name}")
                with self.page.expect_download(timeout=0) as download_info:
                    self.download.click()

                download = download_info.value
                temp_path = download.path()

                upload_single_pdf_to_sharepoint(temp_path, fund_name, dispo, au, file_name)

            if i < number_of_pages:
                self.next_button.click()
                self.table.wait_for(state="visible", timeout=0) 

        print("\n >>>>> Download done !!")
        return True
    
    def logout_user(self):
        self.logout.wait_for(state="visible")
        self.logout.click()


#------------------------------------------------------------------------------------------
# Main function to perform the full navigation flow
    def full_navigate(self, text, dispo, au, fund_name):
        self.select_menu()
        self.select_type_document(text)
        self.select_dates(dispo, au)
        self.select_periodicity()
        self.rechercher.click()
        print("Waiting for results...")
        self.wait_for_results(dispo=dispo, au=au, fund_name=fund_name)
        self.logout_user()
