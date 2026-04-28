import msal
import dotenv
import os
# vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")

def get_token() -> str | None:
    app = msal.ConfidentialClientApplication(
        client_id=os.environ["CLIENT_ID"],
        client_credential=os.environ["PASSWORD_MAILBOX"],
        authority=f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}"
    )
    result = app.acquire_token_for_client(
        scopes=[os.environ["SCOPES"]]
    )
    if "access_token" in result:
        print("✅ Token OK")
        return result["access_token"]
    else:
        print("❌ Token failed:", result.get("error_description"))
        return None