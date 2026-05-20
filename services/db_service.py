from supabase import create_client, Client
from core.config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL or "", SUPABASE_KEY or "")

def get_or_create_lead(phone_number: str) -> dict:
    try:
        response = supabase.table("leads").select("*").eq("phone_number", phone_number).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # Create new lead
        new_lead = {"phone_number": phone_number}
        insert_response = supabase.table("leads").insert(new_lead).execute()
        return insert_response.data[0]
    except Exception as e:
        print(f"Error getting/creating lead: {e}")
        return None

def update_lead(lead_id: str, data: dict) -> dict:
    try:
        response = supabase.table("leads").update(data).eq("id", lead_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error updating lead: {e}")
        return None

def get_or_create_conversation(lead_id: str) -> dict:
    try:
        response = supabase.table("conversations").select("*").eq("lead_id", lead_id).eq("status", "active").execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # Create new conversation
        new_conversation = {"lead_id": lead_id, "status": "active"}
        insert_response = supabase.table("conversations").insert(new_conversation).execute()
        return insert_response.data[0]
    except Exception as e:
        print(f"Error getting/creating conversation: {e}")
        return None

def save_message(conversation_id: str, sender: str, content: str) -> dict:
    try:
        new_message = {
            "conversation_id": conversation_id,
            "sender": sender,
            "content": content
        }
        response = supabase.table("messages").insert(new_message).execute()
        return response.data[0]
    except Exception as e:
        print(f"Error saving message: {e}")
        return None

def get_conversation_history(conversation_id: str, limit: int = 20) -> list:
    try:
        response = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching conversation history: {e}")
        return []

def mark_conversation_handed_over(conversation_id: str):
    try:
        supabase.table("conversations").update({"status": "handed_over"}).eq("id", conversation_id).execute()
    except Exception as e:
        print(f"Error updating conversation status: {e}")
