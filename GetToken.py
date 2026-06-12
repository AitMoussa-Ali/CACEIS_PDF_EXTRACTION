import msal
import dotenv
import os
from utils.Config import Config
# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def get_token() -> str | None:
    app = msal.ConfidentialClientApplication(
        client_id=Config.CLIENT_ID,
        client_credential=Config.PASSWORD_MAILBOX,
        authority=f"https://login.microsoftonline.com/{Config.TENANT_ID}"
    )
    result = app.acquire_token_for_client(
        scopes=[Config.SCOPES]
    )
    if "access_token" in result:
        print("✅ Token OK")
        return result["access_token"]
    else:
        print("❌ Token failed:", result.get("error_description"))
        return None