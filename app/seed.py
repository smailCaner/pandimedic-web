# -*- coding: utf-8 -*-
"""Seed script: Populates DB with sample data including 10-day quizzes."""

from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.quiz import Quiz, QuizQuestion, QuizOption
from app.models.article import Article, ArticleTag
from app.models.symptom import SymptomLog
from app.core.security import hash_password

TEN_DAY_QUIZZES = [
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 1: Genel Sa\u011fl\u0131k",
        "questions": [
            {"text": "\u0130nsan v\u00fccudunda en b\u00fcy\u00fck organ hangisidir?", "explanation": "Deri, insan v\u00fccudundaki en b\u00fcy\u00fck organd\u0131r.",
             "options": [("A", "Karaci\u011fer", False), ("B", "Deri", True), ("C", "Akci\u011fer", False), ("D", "Ba\u011f\u0131rsak", False)]},
            {"text": "Normal v\u00fccut s\u0131cakl\u0131\u011f\u0131 ortalama ka\u00e7 derecedir?", "explanation": "Sa\u011fl\u0131kl\u0131 bir insanda ortalama 36.5 derecedir.",
             "options": [("A", "36.5 C", True), ("B", "38.5 C", False), ("C", "35.0 C", False), ("D", "37.5 C", False)]},
            {"text": "Yeti\u015fkin bir birey g\u00fcnde ne kadar su i\u00e7melidir?", "explanation": "G\u00fcnl\u00fck 2-2.5 litre su metabolizma i\u00e7in \u00f6nemlidir.",
             "options": [("A", "1 Litre", False), ("B", "2-2.5 Litre", True), ("C", "5 Litre", False), ("D", "500 ml", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 2: Enfeksiyon",
        "questions": [
            {"text": "Antibiyotikler hangi enfeksiyonlara etkilidir?", "explanation": "Antibiyotikler sadece bakteriyel enfeksiyonlara etkilidir.",
             "options": [("A", "Viral", False), ("B", "Bakteriyel", True), ("C", "Mantar", False), ("D", "Paraziter", False)]},
            {"text": "Grip a\u015f\u0131s\u0131 ne s\u0131kl\u0131kla yapt\u0131r\u0131lmal\u0131?", "explanation": "Grip vir\u00fcs\u00fc her y\u0131l mutasyona u\u011frar.",
             "options": [("A", "Her ay", False), ("B", "Y\u0131lda bir", True), ("C", "\u00d6m\u00fcrde bir kez", False), ("D", "5 y\u0131lda bir", False)]},
            {"text": "Alerji belirtilerini ne hafifletir?", "explanation": "Antihistaminikler alerjik reaksiyonlar\u0131 bask\u0131lar.",
             "options": [("A", "Antibiyotikler", False), ("B", "Antihistaminikler", True), ("C", "Antidepresanlar", False), ("D", "Analjezikler", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 3: Kalp ve Dola\u015f\u0131m",
        "questions": [
            {"text": "Normal dinlenme kalp at\u0131\u015f h\u0131z\u0131 dakikada ka\u00e7t\u0131r?", "explanation": "Normal yeti\u015fkin 60-100 at\u0131m/dk.",
             "options": [("A", "40-60", False), ("B", "60-100", True), ("C", "100-140", False), ("D", "140-180", False)]},
            {"text": "CPR dakikada ka\u00e7 kompresyon yap\u0131l\u0131r?", "explanation": "CPR h\u0131z\u0131 dakikada 100-120 olmal\u0131d\u0131r.",
             "options": [("A", "60-80", False), ("B", "100-120", True), ("C", "140-160", False), ("D", "200+", False)]},
            {"text": "Hangisi y\u00fcksek tansiyon riski de\u011fildir?", "explanation": "D\u00fczenli egzersiz tansiyonu d\u00fc\u015f\u00fcr\u00fcr.",
             "options": [("A", "A\u015f\u0131r\u0131 tuz", False), ("B", "D\u00fczenli egzersiz", True), ("C", "Obezite", False), ("D", "Stres", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 4: Vitaminler",
        "questions": [
            {"text": "Hangi vitamin eksikli\u011fi gece k\u00f6rl\u00fc\u011f\u00fcne yol a\u00e7ar?", "explanation": "A vitamini retina sa\u011fl\u0131\u011f\u0131 i\u00e7in hayatidir.",
             "options": [("A", "C Vitamini", False), ("B", "A Vitamini", True), ("C", "D Vitamini", False), ("D", "E Vitamini", False)]},
            {"text": "C vitamini en \u00e7ok nerede bulunur?", "explanation": "Turun\u00e7giller C vitamininin en zengin kayna\u011f\u0131d\u0131r.",
             "options": [("A", "Et", False), ("B", "S\u00fct", False), ("C", "Turun\u00e7giller", True), ("D", "Tah\u0131llar", False)]},
            {"text": "Kemik sa\u011fl\u0131\u011f\u0131 i\u00e7in en \u00f6nemli vitamin?", "explanation": "D vitamini kalsiyum emilimini art\u0131r\u0131r.",
             "options": [("A", "E", False), ("B", "D", True), ("C", "B12", False), ("D", "K", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 5: \u0130lk Yard\u0131m",
        "questions": [
            {"text": "Heimlich manevrasi ne zaman uygulan\u0131r?", "explanation": "Bo\u011fulma durumunda hava yolunu a\u00e7mak i\u00e7in uygulan\u0131r.",
             "options": [("A", "K\u0131r\u0131klar", False), ("B", "Bo\u011fulma", True), ("C", "Yan\u0131klar", False), ("D", "Kanama", False)]},
            {"text": "Burun kanamas\u0131nda ba\u015f nas\u0131l tutulmal\u0131?", "explanation": "Ba\u015f hafif\u00e7e \u00f6ne e\u011filmelidir.",
             "options": [("A", "Geriye", False), ("B", "\u00d6ne e\u011fik", True), ("C", "Yatay", False), ("D", "Fark etmez", False)]},
            {"text": "Yan\u0131k durumunda ne uygulanmal\u0131?", "explanation": "15-20 dakika so\u011fuk su uygulanmal\u0131d\u0131r.",
             "options": [("A", "Di\u015f macunu", False), ("B", "So\u011fuk su", True), ("C", "Buz", False), ("D", "Tereya\u011f\u0131", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 6: Uyku ve Zihin",
        "questions": [
            {"text": "\u00d6nerilen uyku s\u00fcresi ne kadard\u0131r?", "explanation": "Yeti\u015fkinler i\u00e7in 7-8 saat ideal uyku s\u00fcresidir.",
             "options": [("A", "4-5 Saat", False), ("B", "7-8 Saat", True), ("C", "10-12 Saat", False), ("D", "3-4 Saat", False)]},
            {"text": "Uyku s\u0131ras\u0131nda beyin ne yapar?", "explanation": "Beyin uykuda haf\u0131za konsolidasyonu yapar.",
             "options": [("A", "Haf\u0131za konsolidasyonu", True), ("B", "Sindirim h\u0131zlan\u0131r", False), ("C", "Kas b\u00fcy\u00fcmesi", False), ("D", "Tansiyon y\u00fckselir", False)]},
            {"text": "Kronik stres hangi hormonu art\u0131r\u0131r?", "explanation": "Kronik stres kortizol hormonunu y\u00fckseltir.",
             "options": [("A", "\u0130ns\u00fclin", False), ("B", "Kortizol", True), ("C", "Melatonin", False), ("D", "Serotonin", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 7: Sindirim",
        "questions": [
            {"text": "Sindirim sistemi hangi organla ba\u015flar?", "explanation": "Sindirim a\u011f\u0131zda ba\u015flar.",
             "options": [("A", "Mide", False), ("B", "A\u011f\u0131z", True), ("C", "Ba\u011f\u0131rsak", False), ("D", "Yemek borusu", False)]},
            {"text": "Gastritte nelerden ka\u00e7\u0131n\u0131lmal\u0131?", "explanation": "Baharatl\u0131 ve asitli g\u0131dalar mide tahri\u015fi yapar.",
             "options": [("A", "Ha\u015flanm\u0131\u015f sebze", False), ("B", "Baharatl\u0131 g\u0131da", True), ("C", "Tam tah\u0131l", False), ("D", "Yo\u011furt", False)]},
            {"text": "Karaci\u011ferin temel g\u00f6revi nedir?", "explanation": "Karaci\u011fer toksinleri ar\u0131nd\u0131r\u0131r (detoksifikasyon).",
             "options": [("A", "Oksijen ta\u015f\u0131ma", False), ("B", "Detoksifikasyon", True), ("C", "Ses \u00fcretme", False), ("D", "Tansiyon d\u00fczenleme", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 8: Kas ve \u0130skelet",
        "questions": [
            {"text": "Yeti\u015fkin v\u00fccutta ka\u00e7 kemik var?", "explanation": "Yeti\u015fkin insanda 206 kemik bulunur.",
             "options": [("A", "150", False), ("B", "206", True), ("C", "300", False), ("D", "180", False)]},
            {"text": "Kalsiyum en \u00e7ok nerede bulunur?", "explanation": "S\u00fct \u00fcr\u00fcnleri kalsiyumun en zengin kayna\u011f\u0131d\u0131r.",
             "options": [("A", "Et", False), ("B", "S\u00fct \u00fcr\u00fcnleri", True), ("C", "Meyveler", False), ("D", "Tah\u0131llar", False)]},
            {"text": "Is\u0131nma neden \u00f6nemlidir?", "explanation": "Is\u0131nma sakatl\u0131k riskini azalt\u0131r.",
             "options": [("A", "Kilo verir", False), ("B", "Sakatl\u0131k riski azal\u0131r", True), ("C", "Performans d\u00fc\u015fer", False), ("D", "Gereksizdir", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 9: Hijyen",
        "questions": [
            {"text": "Eller ka\u00e7 saniye y\u0131kanmal\u0131?", "explanation": "DS\u00d6 en az 20 saniye sabunla y\u0131kamay\u0131 \u00f6nerir.",
             "options": [("A", "5 sn", False), ("B", "20 sn", True), ("C", "3 dk", False), ("D", "Farketmez", False)]},
            {"text": "COVID-19 nas\u0131l bula\u015f\u0131r?", "explanation": "Solunum damlac\u0131klar\u0131yla bula\u015f\u0131r.",
             "options": [("A", "Sivrisinek", False), ("B", "Solunum damlac\u0131klar\u0131", True), ("C", "Kirli su", False), ("D", "G\u0131da", False)]},
            {"text": "Tetanos a\u015f\u0131s\u0131 ka\u00e7 y\u0131lda bir yap\u0131l\u0131r?", "explanation": "Tetanos a\u015f\u0131s\u0131 her 10 y\u0131lda bir tekrarlan\u0131r.",
             "options": [("A", "Her y\u0131l", False), ("B", "5 y\u0131lda bir", False), ("C", "10 y\u0131lda bir", True), ("D", "\u00d6m\u00fcrde bir kez", False)]},
        ],
    },
    {
        "title": "G\u00fcnl\u00fck Sa\u011fl\u0131k Quiz - G\u00fcn 10: T\u0131p K\u00fclt\u00fcr\u00fc",
        "questions": [
            {"text": "Akut terimi ne anlama gelir?", "explanation": "Akut: ani ba\u015flang\u0131\u00e7l\u0131, k\u0131sa s\u00fcreli hastal\u0131k demektir.",
             "options": [("A", "Uzun s\u00fcreli", False), ("B", "Ani, k\u0131sa s\u00fcreli", True), ("C", "\u0130yi huylu", False), ("D", "Bula\u015f\u0131c\u0131", False)]},
            {"text": "Ka\u00e7 temel kan grubu vard\u0131r?", "explanation": "ABO sisteminde A, B, AB ve 0 olmak \u00fczere 4 grup vard\u0131r.",
             "options": [("A", "2", False), ("B", "4", True), ("C", "6", False), ("D", "8", False)]},
            {"text": "V\u00fccutta en \u00e7ok bulunan element?", "explanation": "Oksijen v\u00fccudun k\u00fctle olarak yuzde 65 ini olu\u015fturur.",
             "options": [("A", "Karbon", False), ("B", "Oksijen", True), ("C", "Demir", False), ("D", "Kalsiyum", False)]},
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@pandimedic.com").first()
        if not admin:
            admin = User(email="admin@pandimedic.com", password_hash=hash_password("admin123"),
                         full_name="Admin Kullan\u0131c\u0131", is_admin=True, auth_provider="local")
            db.add(admin); db.flush()
            print("Admin olusturuldu: admin@pandimedic.com / admin123")

        test_user = db.query(User).filter(User.email == "test@pandimedic.com").first()
        if not test_user:
            test_user = User(email="test@pandimedic.com", password_hash=hash_password("test123"),
                             full_name="Test Kullan\u0131c\u0131", is_admin=False, auth_provider="local",
                             current_streak=3, longest_streak=7, total_score=450)
            db.add(test_user); db.flush()
            print("Test kullanici olusturuldu: test@pandimedic.com / test123")

        today = date.today()
        quiz_count = 0
        for day_offset, quiz_data in enumerate(TEN_DAY_QUIZZES):
            quiz_date = today + timedelta(days=day_offset)
            if db.query(Quiz).filter(Quiz.quiz_date == quiz_date).first():
                continue
            quiz = Quiz(quiz_date=quiz_date, title=quiz_data["title"])
            db.add(quiz); db.flush()
            for i, q in enumerate(quiz_data["questions"]):
                question = QuizQuestion(quiz_id=quiz.id, question_text=q["text"],
                                       explanation=q["explanation"], order_index=i)
                db.add(question); db.flush()
                for label, text, is_correct in q["options"]:
                    db.add(QuizOption(question_id=question.id, option_text=text,
                                     is_correct=is_correct, label=label))
            quiz_count += 1
            print(f"Quiz olusturuldu: {quiz_date} - {quiz_data['title']}")

        if quiz_count == 0:
            print("Tum quizler zaten mevcut.")
        else:
            print(f"Toplam {quiz_count} gunluk quiz olusturuldu!")

        sample_articles = [
            {"title": "Antibiyotik Nedir?", "slug": "antibiyotik-nedir", "category": "ilac",
             "content": "Antibiyotikler bakteriyel enfeksiyonlara karsi etkilidir.",
             "tags": ["ilac", "antibiyotik"]},
            {"title": "Hipertansiyon Rehberi", "slug": "hipertansiyon-rehberi", "category": "hastalik",
             "content": "Yuksek tansiyon, kan basincinin surekli normalin uzerinde olmasidir.",
             "tags": ["hastalik", "tansiyon"]},
            {"title": "Tibbi Terimler", "slug": "tibbi-terimler-sozlugu", "category": "terim",
             "content": "Akut: Ani baslangicli. Kronik: Uzun sureli. Benign: Iyi huylu.",
             "tags": ["terim", "sozluk"]},
        ]
        for art in sample_articles:
            if not db.query(Article).filter(Article.slug == art["slug"]).first():
                article = Article(title=art["title"], slug=art["slug"], category=art["category"],
                                  content=art["content"], is_published=True, created_by=admin.id)
                db.add(article); db.flush()
                for tag in art["tags"]:
                    db.add(ArticleTag(article_id=article.id, tag=tag))
                print(f"Makale olusturuldu: {art['title']}")

        db.commit()
        print("Seed verileri basariyla yuklendi!")
    except Exception as e:
        db.rollback()
        print(f"Hata: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
