import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os

print("Makine öğrenmesi modeli eğitiliyor (Gelişmiş Türkçe Sürüm)...")

df = pd.read_csv('symptoms_data.csv', sep=';', encoding='utf-8')
X = df['Şikayet_Cumlesi'].str.lower()
y = df['Poliklinik']

# char_wb n-gram'lar Türkçe gibi eklemeli dillerde kelime köklerini yakalamak için harikadır
model = Pipeline([
    ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 6))),
    ('clf', LogisticRegression(C=5.0, class_weight='balanced', max_iter=200))
])

model.fit(X, y)

joblib.dump(model, 'symptom_model.pkl')
print(f"Eğitim tamamlandı! Yeni model kaydedildi.")
