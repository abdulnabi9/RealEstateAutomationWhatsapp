from twilio.rest import Client
from core.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, AGENT_WHATSAPP_NUMBER

def get_twilio_client():
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return None
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to: str, body: str):
    client = get_twilio_client()
    if not client:
        print("Twilio credentials missing. Skipping message send.")
        return False
    
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=body,
            to=to
        )
        return message.sid
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False

def notify_agent(lead_data: dict, summary: str):
    if not AGENT_WHATSAPP_NUMBER:
        print("AGENT_WHATSAPP_NUMBER not set. Skipping agent notification.")
        return
    
    message = (
        f"🚨 *HOT LEAD ALERT* 🚨\n\n"
        f"👤 *Name*: {lead_data.get('customer_name', 'N/A')}\n"
        f"📱 *Phone*: {lead_data.get('phone_number', 'N/A')}\n"
        f"💰 *Budget*: {lead_data.get('budget', 'N/A')}\n"
        f"📍 *Location*: {lead_data.get('location', 'N/A')}\n"
        f"🏠 *Property Type*: {lead_data.get('property_type', 'N/A')}\n"
        f"🕒 *Timeline*: {lead_data.get('timeline', 'N/A')}\n"
        f"🏦 *Loan Status*: {lead_data.get('loan_status', 'N/A')}\n"
        f"📊 *Intent Score*: {lead_data.get('intent_score', 0)}\n\n"
        f"💬 *Conversation Summary*: {summary}"
    )
    send_whatsapp_message(AGENT_WHATSAPP_NUMBER, message)
