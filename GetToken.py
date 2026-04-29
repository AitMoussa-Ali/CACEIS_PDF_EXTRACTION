import msal
import dotenv
import os
vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def get_token() -> str | None:
    app = msal.ConfidentialClientApplication(
        client_id=vars["CLIENT_ID"],
        client_credential=vars["PASSWORD_MAILBOX"],
        authority=f"https://login.microsoftonline.com/{vars['TENANT_ID']}"
    )
    result = app.acquire_token_for_client(
        scopes=[vars["SCOPES"]]
    )
    if "access_token" in result:
        print("✅ Token OK")
        return result["access_token"]
    else:
        print("❌ Token failed:", result.get("error_description"))
        return None