from fastapi import APIRouter, BackgroundTasks, Form
from pydantic import BaseModel

from services.db_service import (
    get_or_create_lead,
    update_lead,
    get_or_create_conversation,
    save_message,
    get_conversation_history,
    mark_conversation_handed_over
)

from services.llm_service import generate_ai_response
from services.whatsapp_service import send_whatsapp_message, notify_agent

from core.prompts import INITIAL_MESSAGE

router = APIRouter()


async def process_whatsapp_message(phone_number: str, message_content: str):

    print("\n========== NEW MESSAGE ==========")
    print("FROM:", phone_number)
    print("MESSAGE:", message_content)

    # STEP 1 — CREATE/GET LEAD
    lead = get_or_create_lead(phone_number)

    if not lead:
        print("❌ Lead creation failed")
        return

    print("✅ Lead Loaded:", lead)

    # STEP 2 — CREATE/GET CONVERSATION
    conversation = get_or_create_conversation(lead["id"])

    if not conversation:
        print("❌ Conversation creation failed")
        return

    print("✅ Conversation Loaded:", conversation)

    # STEP 3 — IGNORE IF HANDOVER
    if conversation.get("status") == "handed_over":
        print("⚠️ Conversation already handed over")
        return

    # STEP 4 — SAVE USER MESSAGE
    save_message(conversation["id"], "user", message_content)

    # STEP 5 — GET HISTORY
    history = get_conversation_history(conversation["id"])

    print("✅ History Count:", len(history))

    # FIRST MESSAGE FLOW
    if len(history) <= 1:

        ai_reply = INITIAL_MESSAGE

        print("✅ Sending Initial Message")

        save_message(conversation["id"], "ai", ai_reply)

        send_whatsapp_message(phone_number, ai_reply)

        return

    # STEP 6 — CURRENT STATE
    current_state = {
        "customer_name": lead.get("customer_name"),
        "budget": lead.get("budget"),
        "location": lead.get("location"),
        "property_type": lead.get("property_type"),
        "timeline": lead.get("timeline"),
        "loan_status": lead.get("loan_status"),
        "intent_score": lead.get("intent_score", 0),
        "lead_type": lead.get("lead_type", "COLD")
    }

    print("✅ Current State:", current_state)

    # STEP 7 — AI RESPONSE
    try:

        response = generate_ai_response(history, current_state)

        print("✅ AI Response Generated")

    except Exception as e:

        print("❌ LLM ERROR:", str(e))

        ai_reply = (
            "I'm having a little trouble right now. "
            "Please give me a moment 😊"
        )

        save_message(conversation["id"], "ai", ai_reply)

        send_whatsapp_message(phone_number, ai_reply)

        return

    # STEP 8 — EXTRACT DATA
    ai_reply = response.reply
    data = response.data

    print("✅ AI Reply:", ai_reply)
    print("✅ AI Data:", data)

    # STEP 9 — SAVE AI MESSAGE
    save_message(conversation["id"], "ai", ai_reply)

    # STEP 10 — UPDATE LEAD
    update_data = {
        "customer_name": data.customer_name,
        "budget": data.budget,
        "location": data.location,
        "property_type": data.property_type,
        "timeline": data.timeline,
        "loan_status": data.loan_status,
        "intent_score": data.intent_score,
        "lead_type": data.lead_type
    }

    # REMOVE NONE VALUES
    update_data = {
        k: v for k, v in update_data.items()
        if v is not None
    }

    print("✅ Update Data:", update_data)

    if update_data:

        update_lead(lead["id"], update_data)

        lead.update(update_data)

        print("✅ Lead Updated")

    # STEP 11 — SEND WHATSAPP MESSAGE
    try:

        send_whatsapp_message(phone_number, ai_reply)

        print("✅ WhatsApp Reply Sent")

    except Exception as e:

        print("❌ WhatsApp Send Error:", str(e))

    # STEP 12 — HANDOVER
    if data.conversation_complete or len(history) > 15:

        if data.lead_type == "HOT":

            mark_conversation_handed_over(conversation["id"])

            notify_agent(
                lead,
                "🔥 HOT LEAD qualified by AI"
            )

            print("✅ Agent Notified")


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(...)
):

    print("\n🔥 WEBHOOK HIT")

    background_tasks.add_task(
        process_whatsapp_message,
        From,
        Body
    )

    return {
        "status": "ok"
    }


class TestMessage(BaseModel):
    phone_number: str
    message: str


@router.post("/chat/process")
async def process_chat_test(
    msg: TestMessage,
    background_tasks: BackgroundTasks
):

    background_tasks.add_task(
        process_whatsapp_message,
        msg.phone_number,
        msg.message
    )

    return {
        "status": "processing"
    }