"""
Mock Symptom Analyzer — Strategy Pattern

Şu anki implementasyon basit kural tabanlı (sözlük eşleştirmesi).
İleride `MLSymptomAnalyzer` veya `DatasetSymptomAnalyzer` sınıfıyla
gerçek tıbbi veri seti / makine öğrenmesi modeli entegre edilecek.

Kullanım:
    analyzer = get_symptom_analyzer()  # Factory fonksiyon
    result = analyzer.analyze(["karın ağrısı", "bulantı"])
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import joblib
import os


# ─── Veri Modelleri ────────────────────────────────────────────────────────────

@dataclass
class PolyclinicResult:
    department: str
    confidence: str  # yüksek / orta / düşük
    description: str
    enabiz_url: str
    warning: str | None = None


@dataclass
class AnalysisResult:
    input_symptoms: list[str]
    recommendations: list[PolyclinicResult]
    disclaimer: str = (
        "⚠️ Bu sonuç bir tıbbi tanı değildir. Lütfen bir sağlık kuruluşuna başvurunuz. "
        "Bu uygulama yalnızca bilgilendirme amaçlıdır."
    )


# ─── Temel Sınıf (Abstract) ───────────────────────────────────────────────────

class BaseSymptomAnalyzer(ABC):
    """İlerideki tüm semptom analiz motorları bu sınıftan türeyecek."""

    @abstractmethod
    def analyze(self, symptoms: list[str]) -> AnalysisResult:
        ...


# ─── Mock Implementasyon ──────────────────────────────────────────────────────

# E-Nabız temel URL
ENABIZ_BASE_URL = "https://enabiz.gov.tr/"

# Semptom → Poliklinik eşleştirme kuralları
# Her kural: (semptom seti, sonuç)
SYMPTOM_RULES: list[tuple[set[str], PolyclinicResult]] = [
    # ── Acil durumlar (öncelikli) ──
    (
        {"göğüs ağrısı", "nefes darlığı"},
        PolyclinicResult(
            department="Acil Servis / Kardiyoloji",
            confidence="yüksek",
            description="Göğüs ağrısı ve nefes darlığı birlikte görülmesi acil değerlendirme gerektirebilir.",
            enabiz_url=ENABIZ_BASE_URL,
            warning="🚨 Bu belirtiler acil tıbbi müdahale gerektirebilir. Lütfen en yakın acil servise başvurun.",
        ),
    ),
    (
        {"göğüs ağrısı"},
        PolyclinicResult(
            department="Kardiyoloji",
            confidence="yüksek",
            description="Göğüs ağrısı kalp ile ilgili sorunlara işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
            warning="⚠️ Şiddetli veya ani göğüs ağrısı varsa acil servise başvurun.",
        ),
    ),

    # ── Gastroenteroloji ──
    (
        {"karın ağrısı", "bulantı", "kusma"},
        PolyclinicResult(
            department="Gastroenteroloji",
            confidence="yüksek",
            description="Karın ağrısı, bulantı ve kusma sindirim sistemi hastalıklarına işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
    (
        {"karın ağrısı", "bulantı"},
        PolyclinicResult(
            department="Gastroenteroloji",
            confidence="orta",
            description="Karın ağrısı ve bulantı mide-bağırsak sorunlarına işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
    (
        {"karın ağrısı", "ishal"},
        PolyclinicResult(
            department="Gastroenteroloji",
            confidence="orta",
            description="Karın ağrısı ve ishal sindirim sistemi enfeksiyonuna işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),

    # ── Dahiliye (Genel) ──
    (
        {"ateş", "baş ağrısı"},
        PolyclinicResult(
            department="Dahiliye (İç Hastalıkları)",
            confidence="orta",
            description="Ateş ve baş ağrısı enfeksiyon belirtisi olabilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
    (
        {"ateş", "öksürük"},
        PolyclinicResult(
            department="Göğüs Hastalıkları",
            confidence="orta",
            description="Ateş ve öksürük solunum yolu enfeksiyonuna işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
    (
        {"ateş"},
        PolyclinicResult(
            department="Dahiliye (İç Hastalıkları)",
            confidence="düşük",
            description="Ateş birçok farklı hastalığın belirtisi olabilir. Genel değerlendirme önerilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),

    # ── Nöroloji ──
    (
        {"baş ağrısı", "baş dönmesi", "bulantı"},
        PolyclinicResult(
            department="Nöroloji",
            confidence="orta",
            description="Baş ağrısı, baş dönmesi ve bulantı nörolojik değerlendirme gerektirebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
    (
        {"baş ağrısı", "bulanık görme"},
        PolyclinicResult(
            department="Nöroloji",
            confidence="yüksek",
            description="Baş ağrısı ve görme bozukluğu nörolojik değerlendirme gerektirir.",
            enabiz_url=ENABIZ_BASE_URL,
            warning="⚠️ Ani başlayan şiddetli baş ağrısı ve görme bozukluğu acil durum olabilir.",
        ),
    ),

    # ── Ortopedi ──
    (
        {"eklem ağrısı", "şişlik"},
        PolyclinicResult(
            department="Ortopedi",
            confidence="orta",
            description="Eklem ağrısı ve şişlik ortopedik değerlendirme gerektirebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
    (
        {"bel ağrısı"},
        PolyclinicResult(
            department="Ortopedi / Fizik Tedavi",
            confidence="orta",
            description="Bel ağrısı kas-iskelet sistemi sorunlarına işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),

    # ── Dermatoloji ──
    (
        {"döküntü", "kaşıntı"},
        PolyclinicResult(
            department="Dermatoloji",
            confidence="orta",
            description="Döküntü ve kaşıntı cilt hastalıklarına işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),

    # ── KBB ──
    (
        {"boğaz ağrısı", "öksürük"},
        PolyclinicResult(
            department="Kulak Burun Boğaz (KBB)",
            confidence="orta",
            description="Boğaz ağrısı ve öksürük üst solunum yolu enfeksiyonuna işaret edebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),

    # ── Üroloji ──
    (
        {"sık idrara çıkma", "yanma"},
        PolyclinicResult(
            department="Üroloji",
            confidence="orta",
            description="İdrar yolu belirtileri ürolojik değerlendirme gerektirebilir.",
            enabiz_url=ENABIZ_BASE_URL,
        ),
    ),
]


class MockSymptomAnalyzer(BaseSymptomAnalyzer):
    """
    Kural tabanlı mock semptom analiz motoru.

    Çalışma prensibi:
    1. Kullanıcının girdiği semptomlar küme (set) olarak alınır.
    2. SYMPTOM_RULES listesi sırayla kontrol edilir.
    3. Kuralın semptom seti, kullanıcının semptomlarının alt kümesiyse eşleşme sağlanır.
    4. Eşleşme skoru: eşleşen semptom sayısı / kural semptom sayısı
    5. En iyi eşleşmeler döndürülür.
    """

    def analyze(self, symptoms: list[str]) -> AnalysisResult:
        user_symptoms = {s.lower().strip() for s in symptoms}

        if not user_symptoms:
            return AnalysisResult(
                input_symptoms=symptoms,
                recommendations=[
                    PolyclinicResult(
                        department="Dahiliye (İç Hastalıkları)",
                        confidence="düşük",
                        description="Lütfen en az bir belirti giriniz.",
                        enabiz_url=ENABIZ_BASE_URL,
                    )
                ],
            )

        matches: list[tuple[float, PolyclinicResult]] = []
        seen_departments: set[str] = set()

        for rule_symptoms, result in SYMPTOM_RULES:
            if rule_symptoms.issubset(user_symptoms):
                match_score = len(rule_symptoms) / max(len(user_symptoms), 1)
                if result.department not in seen_departments:
                    matches.append((match_score, result))
                    seen_departments.add(result.department)

        # Skor sırasına göre sırala (en iyi eşleşme önce)
        matches.sort(key=lambda x: x[0], reverse=True)

        if not matches:
            # Hiçbir kuralla eşleşme yoksa genel yönlendirme
            return AnalysisResult(
                input_symptoms=symptoms,
                recommendations=[
                    PolyclinicResult(
                        department="Dahiliye (İç Hastalıkları)",
                        confidence="düşük",
                        description=(
                            "Girdiğiniz belirtiler için kesin bir poliklinik önerisi bulunamadı. "
                            "Genel değerlendirme için Dahiliye polikliniğine başvurmanızı öneririz."
                        ),
                        enabiz_url=ENABIZ_BASE_URL,
                    )
                ],
            )

        recommendations = [result for _, result in matches[:3]]  # En fazla 3 öneri

        return AnalysisResult(
            input_symptoms=symptoms,
            recommendations=recommendations,
        )


# ─── Ilerideki gerçek implementasyon için placeholder ──────────────────────────

class MLSymptomAnalyzer(BaseSymptomAnalyzer):
    """
    Gerçek tıbbi veri seti (TF-IDF + Naive Bayes) ile eğitilmiş
    Makine Öğrenmesi destekli semptom analiz motoru.
    """

    DEPT_INFO = {
        "Dahiliye": "Girdiğiniz belirtiler doğrultusunda iç hastalıkları (Dahiliye) polikliniğine görünmeniz önerilir.",
        "Nöroloji": "Baş, sinir sistemi veya uyuşma gibi nörolojik belirtiler saptandı.",
        "Kardiyoloji": "Kalp, çarpıntı veya göğüs ağrısı ile ilgili kardiyolojik değerlendirme önerilir.",
        "Kulak Burun Boğaz (KBB)": "Kulak, burun veya boğaz yolları ile ilgili şikayetler saptandı.",
        "Göz Hastalıkları": "Görme ve göz sağlığı problemleri saptandı.",
        "Cildiye (Dermatoloji)": "Cilt, deri veya saç ile ilgili dermatolojik şikayetler saptandı.",
        "Göğüs Hastalıkları": "Solunum yolu veya nefes darlığı ile ilgili göğüs hastalıkları polikliniği önerilir.",
    }

    def __init__(self, model_path: str | None = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.model_path = os.path.join(base_dir, "ml", "symptom_model.pkl")
        else:
            self.model_path = model_path
            
        self.model = None
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)

    def analyze(self, symptoms: list[str]) -> AnalysisResult:
        if not symptoms or not self.model:
            # Fallback
            return MockSymptomAnalyzer().analyze(symptoms)

        # Cümleleri birleştir (örn: "başım ağrıyor, ateşim var")
        text = " ".join(symptoms).lower()

        try:
            # Tahmin oranlarını al
            probs = self.model.predict_proba([text])[0]
            classes = self.model.classes_

            # Skorlara göre sırala
            scored_classes = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
            
            recommendations = []
            for dept, prob in scored_classes[:2]:  # En olası 2 poliklinik
                if prob < 0.15 and len(recommendations) > 0:
                    break  # Çok düşük olasılıklıları gösterme
                
                confidence = "yüksek" if prob > 0.6 else "orta" if prob > 0.3 else "düşük"
                
                # Özel acil durum kelimesi kontrolü
                warning = None
                if any(w in text for w in ["nefes alamıyorum", "göğsümde öküz", "kalbime bıçak", "kan boşaldı"]):
                    warning = "🚨 Belirtileriniz acil bir duruma işaret ediyor olabilir. Lütfen en yakın acil servise başvurun."
                    confidence = "yüksek"

                desc = self.DEPT_INFO.get(dept, f"{dept} polikliniğine başvurmanız önerilir.")
                
                recommendations.append(PolyclinicResult(
                    department=dept,
                    confidence=confidence,
                    description=desc,
                    enabiz_url=ENABIZ_BASE_URL,
                    warning=warning
                ))
            
            return AnalysisResult(
                input_symptoms=symptoms,
                recommendations=recommendations or MockSymptomAnalyzer().analyze(symptoms).recommendations
            )
        except Exception as e:
            return MockSymptomAnalyzer().analyze(symptoms)


# ─── Factory Function ─────────────────────────────────────────────────────────

_analyzer_instance: BaseSymptomAnalyzer | None = None


def get_symptom_analyzer() -> BaseSymptomAnalyzer:
    """
    Factory: Aktif semptom analizörünü döndürür.
    Şu an MockSymptomAnalyzer, ileride değiştirilecek.
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = MLSymptomAnalyzer()
    return _analyzer_instance
