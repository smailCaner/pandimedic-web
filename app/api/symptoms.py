"""Symptom analysis API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.symptom import SymptomLog
from app.schemas.symptom import (
    SymptomAnalyzeRequest, SymptomAnalyzeResponse,
    PolyclinicRecommendation, SymptomLogOut,
)
from app.services.symptom_analyzer import get_symptom_analyzer

router = APIRouter(prefix="/api/symptoms", tags=["Symptoms"])


@router.post("/analyze", response_model=SymptomAnalyzeResponse)
def analyze_symptoms(
    payload: SymptomAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının girdiği belirtileri analiz et ve poliklinik önerisi döndür.
    Sonuçlar veritabanına kaydedilir.
    """
    analyzer = get_symptom_analyzer()
    result = analyzer.analyze(payload.symptoms)

    # Sonucu veritabanına kaydet
    log = SymptomLog(
        user_id=current_user.id,
        symptoms=payload.symptoms,
        result={
            "recommendations": [
                {
                    "department": r.department,
                    "confidence": r.confidence,
                    "description": r.description,
                    "enabiz_url": r.enabiz_url,
                    "warning": r.warning,
                }
                for r in result.recommendations
            ]
        },
    )
    db.add(log)
    db.commit()

    return SymptomAnalyzeResponse(
        input_symptoms=result.input_symptoms,
        recommendations=[
            PolyclinicRecommendation(
                department=r.department,
                confidence=r.confidence,
                description=r.description,
                enabiz_url=r.enabiz_url,
                warning=r.warning,
            )
            for r in result.recommendations
        ],
        disclaimer=result.disclaimer,
        question=result.question,
    )


@router.get("/history", response_model=list[SymptomLogOut])
def symptom_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kullanıcının geçmiş semptom analizleri."""
    logs = (
        db.query(SymptomLog)
        .filter(SymptomLog.user_id == current_user.id)
        .order_by(SymptomLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [SymptomLogOut.model_validate(log) for log in logs]
