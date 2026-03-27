"""Unit tests for the MockSymptomAnalyzer."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.symptom_analyzer import MockSymptomAnalyzer, AnalysisResult


def test_analyzer():
    analyzer = MockSymptomAnalyzer()

    print("=" * 60)
    print("MOCK SEMPTOM ANALİZÖRÜ TESTLERİ")
    print("=" * 60)

    test_cases = [
        {
            "name": "Göğüs ağrısı + nefes darlığı → Acil",
            "symptoms": ["göğüs ağrısı", "nefes darlığı"],
            "expected_dept": "Acil Servis / Kardiyoloji",
        },
        {
            "name": "Karın ağrısı + bulantı → Gastroenteroloji",
            "symptoms": ["karın ağrısı", "bulantı"],
            "expected_dept": "Gastroenteroloji",
        },
        {
            "name": "Ateş + baş ağrısı → Dahiliye",
            "symptoms": ["ateş", "baş ağrısı"],
            "expected_dept": "Dahiliye (İç Hastalıkları)",
        },
        {
            "name": "Ateş + öksürük → Göğüs Hastalıkları",
            "symptoms": ["ateş", "öksürük"],
            "expected_dept": "Göğüs Hastalıkları",
        },
        {
            "name": "Döküntü + kaşıntı → Dermatoloji",
            "symptoms": ["döküntü", "kaşıntı"],
            "expected_dept": "Dermatoloji",
        },
        {
            "name": "Bilinmeyen semptomlar → Genel Dahiliye",
            "symptoms": ["kulak çınlaması", "uyuşma"],
            "expected_dept": "Dahiliye (İç Hastalıkları)",
        },
        {
            "name": "Boş semptom listesi",
            "symptoms": [],
            "expected_dept": "Dahiliye (İç Hastalıkları)",
        },
    ]

    passed = 0
    failed = 0

    for tc in test_cases:
        result = analyzer.analyze(tc["symptoms"])
        assert isinstance(result, AnalysisResult)

        first_dept = result.recommendations[0].department if result.recommendations else "YOK"
        status = "✅" if first_dept == tc["expected_dept"] else "❌"

        if first_dept == tc["expected_dept"]:
            passed += 1
        else:
            failed += 1

        print(f"\n{status} {tc['name']}")
        print(f"   Semptomlar: {tc['symptoms']}")
        print(f"   Beklenen:   {tc['expected_dept']}")
        print(f"   Dönen:      {first_dept}")

        if result.recommendations[0].warning:
            print(f"   Uyarı:      {result.recommendations[0].warning}")

    print(f"\n{'=' * 60}")
    print(f"Sonuç: {passed} başarılı, {failed} başarısız / {len(test_cases)} test")
    print(f"{'=' * 60}")

    # Also show disclaimer
    sample = analyzer.analyze(["ateş"])
    print(f"\nDisclaimer: {sample.disclaimer}")

    return failed == 0


if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
