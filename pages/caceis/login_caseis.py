from playwright.sync_api import Page
# import dotenv
from Mailing.AutomateMail import fetch_otp_from_outlook
# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

class Login:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_role("textbox", name="Veuillez saisir votre login")
        self.password_input = page.get_by_role("textbox", name="Mot de passe")
        self.login_button = page.get_by_role("button", name="Go")
        self.otp_input = page.get_by_role("textbox", name="Entrer le code de sécurité ici")
        self.error_message = page.locator("#ols-error-login")
        self.menu = page.locator("[data-test='menu-entry-MENU']")
        self.confirmer_mdp = page.get_by_role("textbox", name="Confirmer nouveau mot de passe")
        self.captcha = page.get_by_role("img", name="Retype the CAPTCHA code from")
        
    def type_username(self, username):
        self.username_input.type(username)
        
    def type_password(self, password):
        self.password_input.type(password)
        
    def click_login(self):
        self.login_button.click()
    
    def login(self, username, password):
        self.type_username(username)
        self.click_login()
        
        while self.captcha.is_visible() == False and self.password_input.is_visible() == False :
            print("⏳ Waiting for password field or captcha to appear...")
            self.page.wait_for_timeout(500)  # Wait a bit before checking again
        
        if self.captcha.is_visible() :
            return False
        else :
            print("Password field appeared, proceeding with login.")
            self.type_password(password)
            self.click_login()
            return True
        
    
    def otp_login(self, sender: str, timeout = 600):
        logged_in = False
        while logged_in == False:
            print("\n>>> Check the otp code ......")
            self.otp_input.wait_for()
            
            otp = fetch_otp_from_outlook(sender=sender, timeout=timeout)
            
            if not otp:
                print("❌ Failed to retrieve OTP. Please check the mailbox and try again.")
                return
            
            print('>>> OTP received:', otp)
            self.otp_input.type(otp)
            self.click_login()
            
            while self.error_message.is_visible() == False and self.menu.is_visible() == False and self.confirmer_mdp.is_visible() == False :
                print("⏳ Waiting for login to complete...")
                self.page.wait_for_timeout(1000)  # Wait a bit before checking again
                
            if self.error_message.is_visible():
                print("❌ OTP failed, retrying...")
                self.otp_input.fill("")  # Clear the input for the next attempt
                
                
            elif self.confirmer_mdp.is_visible() : 
                print("Password needs to be changed")
                return False
            else: 
                logged_in = True
                print("✅ Logged in successfully!")
                
        return True
    
    