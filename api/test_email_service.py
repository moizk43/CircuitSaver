from app.services.notifications.email_service import send_email_notification, build_html_body

html = build_html_body(
    appliance="ev_charger",
    delay_minutes=45,
    cost_saved=0.12,
    carbon_saved=0.67,
)

result = send_email_notification(
    to_address="moizkothawala@gmail.com",
    subject="CircuitSaver Test Email",
    html_body=html,
)

print("Sent! Message ID:", result["id"])