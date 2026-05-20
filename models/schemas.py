from pydantic import BaseModel
from typing import Optional

class QualificationData(BaseModel):
    customer_name: Optional[str] = None
    budget: Optional[str] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    timeline: Optional[str] = None
    loan_status: Optional[str] = None
    intent_score: int = 0
    lead_type: str = "COLD"
    conversation_complete: bool = False

class GeminiResponse(BaseModel):
    reply: str
    data: QualificationData
