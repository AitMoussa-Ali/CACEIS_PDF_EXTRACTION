from GetToken import get_token
import requests
from utils.Config import Config
def send_email(subject: str, body: str, recipients: list[str]) -> bool:
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    sender = Config.MAIL_SENDER  # e.g. "notifications@yourcompany.com"

    email_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": email}} for email in recipients
            ]
        },
        "saveToSentItems": "true"
    }

    try:
        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail",
            headers=headers,
            json=email_payload
        )
        response.raise_for_status()
        print(f"✅ Email sent successfully to {len(recipients)} recipient(s)")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False  

send_email(
    "testing mail",
    "<p>Ce mail a été envoyé pour le test</p>",
    ["ali.aitmoussa@groupe-aplitec.com"]
)