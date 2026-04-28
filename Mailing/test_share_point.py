import requests
import dotenv
import msal

vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")
 
def get_token():
    app = msal.ConfidentialClientApplication(
        client_id=vars["CLIENT_ID"],
        client_credential=vars["PASSWORD_MAILBOX"],
        authority=f"https://login.microsoftonline.com/{vars['TENANT_ID']}"
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" in result:
        print("✅ Token OK")
        # print('Token:', result["access_token"])
        return result["access_token"]
    else:
        print("❌ Token failed:", result.get("error_description"))
        return None
    
    
def get_site_id(token):
    """
    site_url example: yourcompany.sharepoint.com:/sites/yoursite
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{vars["URL_SHARE_POINT"]}"
    response = requests.get(url="https://graph.microsoft.com/v1.0/sites/aplitecgroupe.sharepoint.com:/sites/Equipes59", headers=headers)
    data = response.json()
    print(f"data: {data}")
    # return data

token = get_token()
if token:
    get_site_id(token)  
