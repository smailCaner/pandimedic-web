import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

print("Makine öğrenmesi modeli eğitiliyor...")

# Load dataset
df = pd.read_csv('symptoms_data.csv', sep=';', encoding='utf-8')

# Basic clean up
X = df['Şikayet_Cumlesi'].str.lower()
y = df['Poliklinik']

# Pipeline: TF-IDF for text vectorization -> Naive Bayes for classification
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
    ('clf', MultinomialNB())
])

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, 'symptom_model.pkl')
print(f"Eğitim tamamlandı! Model 'symptom_model.pkl' {os.path.abspath('symptom_model.pkl')} konumuna kaydedildi.")
