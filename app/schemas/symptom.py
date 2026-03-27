"""Pydantic schemas for symptom analysis."""

from datetime import datetime
from pydantic import BaseModel


# â”€â”€ Request â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class SymptomAnalyzeRequest(BaseModel):
    symptoms: list[str]  # ["karÄ±n aÄŸrÄ±sÄ±", "ateÅŸ", "bulantÄ±"]


# â”€â”€ Response â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class PolyclinicRecommendation(BaseModel):
    department: str            # Dahiliye, Kardiyoloji, Acil...
    confidence: str            # yÃ¼ksek / orta / dÃ¼ÅŸÃ¼k
    description: str           # KÄ±sa aÃ§Ä±klama
    enabiz_url: str            # E-NabÄ±z randevu linki
    warning: str | None = None # Acil uyarÄ± varsa


class SymptomAnalyzeResponse(BaseModel):
    input_symptoms: list[str]
    recommendations: list[PolyclinicRecommendation]
    disclaimer: str  # "Bu bir tÄ±bbi tanÄ± deÄŸildir" uyarÄ±sÄ±


# â”€â”€ History â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class SymptomLogOut(BaseModel):
    id: str
    symptoms: list[str]
    result: dict
    created_at: datetime

    model_config = {"from_attributes": True}

