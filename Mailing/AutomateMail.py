# test_connection.py
import requests
import dotenv 
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from GetToken import get_token
import os

vars = dotenv.dotenv_values(r"C:\Users\aaitmoussa\Desktop\Projet Aplitec\Automation\.env")


def extract_otp_from_html(body: str) -> str | None:
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(separator="\n")
    # Method 1: look near keywords first
    keywords = ["code de sécurité", "code à usage unique", "voici le code"]
    for keyword in keywords:
        idx = text.lower().find(keyword)
        if idx != -1:
            # Search for 6-digit number within 200 chars after the keyword
            nearby_text = text[idx:idx+200]
            match = re.search(r'\b(\d{6})\b', nearby_text)
            if match:
                return match.group(1)
    
    # Method 2: fallback - first 6-digit number in the whole text
    match = re.search(r'\b(\d{6})\b', text)
    if match:
        return match.group(1)
    
    return None

def fetch_otp_from_outlook(
    sender: str,
    timeout: int = 300,
    poll_interval: int = 5
) -> str:
    
    mailbox = vars["SHARED_MAILBOX"]
    start_datetime = (datetime.utcnow() - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = (
        f"https://graph.microsoft.com/v1.0/users/{mailbox}"
        f"/mailFolders/inbox/messages"
        f"?$filter=from/emailAddress/address eq '{sender}'"
        f" and isRead eq false"
        f" and receivedDateTime ge {start_datetime}"
        f"&$top=1"
    )

    start_time = time.time()
    while time.time() - start_time < timeout:
        
        # ✅ Refresh token on every iteration to avoid expiry
        token = get_token()
        if not token:
            raise Exception("Failed to get token")
            
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        messages = response.json().get("value", [])

        if messages:
            body = messages[0].get("body", {}).get("content", "")
            otp = extract_otp_from_html(body)
            print(f"Extracted OTP: {otp}")

            if otp:
                print('>>> OTP received:', otp)
                message_id = messages[0]["id"]

                requests.patch(
                    f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{message_id}",
                    headers={**headers, "Content-Type": "application/json"},
                    json={"isRead": True}
                )
                return otp

        time.sleep(poll_interval)

    raise TimeoutError("OTP not received within timeout period")
