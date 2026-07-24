import os
import base64
import pandas as pd
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "gmail_token.json")
SENDER_EMAIL = "circuitsaver.alerts@gmail.com"
USER_PROFILES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "synthetic", "user_profiles.csv")

APPLIANCE_DISPLAY_NAMES = {
    "ev_charger": "EV charger",
    "dishwasher": "dishwasher",
    "dryer": "dryer",
    "washing_machine": "washing machine",
    "hvac": "HVAC system",
    "water_heater": "water heater",
    "pool_pump": "pool pump",
}


def _load_credentials():
    with open(TOKEN_PATH, "r") as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=token_data["scopes"],
    )

    if creds.expired or not creds.valid:
        creds.refresh(Request())

    return creds


def get_user_contact_info(user_id: str):
    df = pd.read_csv(USER_PROFILES_PATH)
    row = df[df["user_id"] == user_id]
    if row.empty:
        return None
    return {
        "notification_method": row.iloc[0]["notification_method"],
        "email_address": row.iloc[0]["email_address"],
    }


def format_appliance_name(appliance: str) -> str:
    if appliance in APPLIANCE_DISPLAY_NAMES:
        return APPLIANCE_DISPLAY_NAMES[appliance]
    return appliance.replace("_", " ")


def build_html_body(appliance: str, delay_minutes: int, cost_saved: float, carbon_saved: float) -> str:
    appliance_display = format_appliance_name(appliance)
    cost_saved_str = f"{cost_saved:.2f}"
    carbon_saved_str = f"{carbon_saved:.2f}"

    return f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link href="https://fonts.googleapis.com/css2?family=Baloo+Tammudu+2:wght@400;500;600;700&display=swap" rel="stylesheet">

    <title>CircuitSaver</title>
    </head>

    <body style="margin:0;padding:0;background:#f5fdf7;">

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5fdf7;padding:40px 20px;">

    <tr>
    <td align="center">

    <table role="presentation" width="620" cellpadding="0" cellspacing="0"
    style="
    background:#ffffff;
    border-radius:22px;
    overflow:hidden;
    box-shadow:0 10px 30px rgba(0,0,0,.08);
    ">

    <!-- Header -->

    <tr>
    <td align="center"
    style="
    background:#56d16d;
    padding:35px 20px 28px 20px;
    ">

    <h1
    style="
    margin:0;
    font-family:'Baloo Tammudu 2',Arial,sans-serif;
    font-size:34px;
    font-weight:700;
    color:white;
    line-height:1;
    ">

    CircuitSaver

    </h1>

    <p
    style="
    margin-top:14px;
    font-family:'Baloo Tammudu 2',Arial,sans-serif;
    font-size:18px;
    color:#edfdf0;
    ">

    Smarter Energy. Lower Costs.

    </p>

    </td>
    </tr>

    <!-- BODY -->

    <tr>

    <td
    style="
    padding:45px;
    font-family:'Baloo Tammudu 2',Arial,sans-serif;
    color:#404040;
    ">

    <h2
    style="
    margin-top:0;
    font-size:28px;
    color:#56d16d;
    ">

    Hi there!

    </h2>

    <p style="font-size:17px;line-height:1.8;">

    Your
    <strong>{appliance_display}</strong>
    is a great candidate for a smart delay based on current electricity demand.

    By waiting approximately
    <strong>{delay_minutes} minutes</strong>,
    you can reduce costs while helping create a cleaner, more reliable electric grid.

    </p>

    <!-- Savings Card -->

    <table
    role="presentation"
    width="100%"
    style="
    margin:35px 0;
    background:#f3fff6;
    border:2px solid #d7f7df;
    border-radius:18px;
    ">

    <tr>

    <td style="padding:28px;">

    <h3
    style="
    margin-top:0;
    color:#56d16d;
    font-size:22px;
    ">

    Estimated Benefits

    </h3>

    <p style="font-size:17px;margin:18px 0;">

    <strong>Save:</strong>
    <strong>${cost_saved_str}</strong>
    on your electric bill
    </p>

    <p style="font-size:17px;margin:18px 0;">

    <strong>Reduce:</strong>
    <strong>{carbon_saved_str} lbs</strong>
    of CO&#8322; emissions
    </p>

    <p style="font-size:17px;margin-bottom:0;">

    <strong>Recommended Delay:</strong>
    {delay_minutes} minutes
    </p>

    </td>

    </tr>

    </table>

    <p style="font-size:17px;line-height:1.8;">

    Small changes make a big difference.
    Thank you for helping your neighborhood use energy more efficiently while reducing environmental impact.

    </p>

    <p
    style="
    margin-top:40px;
    font-size:18px;
    ">

    Best regards,

    <br><br>

    <strong>The CircuitSaver Team</strong>

    </p>

    </td>

    </tr>

    <!-- Footer -->

    <tr>

    <td
    align="center"
    style="
    background:#f9fbf9;
    padding:28px;
    font-family:Arial,sans-serif;
    font-size:13px;
    color:#888;
    ">

    This message was automatically generated by CircuitSaver using real-time grid conditions.

    <br><br>

    Helping communities save money while building a smarter, greener electric grid.

    </td>

    </tr>

    </table>

    </td>

    </tr>

    </table>

    </body>
    </html>
    """


def send_email_notification(to_address: str, subject: str, html_body: str):
    creds = _load_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(html_body, "html")
    message["to"] = to_address
    message["from"] = SENDER_EMAIL
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw},
    ).execute()

    return sent