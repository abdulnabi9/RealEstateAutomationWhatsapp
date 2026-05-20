import json
import google.generativeai as genai

from core.config import GEMINI_API_KEY
from core.prompts import SYSTEM_PROMPT
from models.schemas import GeminiResponse

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Create model
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_ai_response(conversation_history: list, current_state: dict) -> GeminiResponse:

    # Format conversation history
    history_str = ""

    for msg in conversation_history:
        role = "Assistant" if msg["sender"] == "ai" else "User"
        history_str += f"{role}: {msg['content']}\n"

    # Current lead state
    state_str = json.dumps(current_state, indent=2)

    # Final prompt
    prompt = f"""
    {SYSTEM_PROMPT}

    Current Known Lead Data:
    {state_str}

    Conversation History:
    {history_str}

    Respond as Priya and return ONLY valid JSON.
    """

    try:

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        )

        data = json.loads(response.text)

        return GeminiResponse(**data)

    except Exception as e:
        print("Gemini Error:", e)
        print("Raw Response:", response.text if 'response' in locals() else "No response")

        raise ValueError("AI did not return valid JSON")