import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import mlflow

# 1. Mengaktifkan autologging MLflow untuk Scikit-learn
# Ini akan secara otomatis mencatat parameter, metrik, dan model Anda.
mlflow.sklearn.autolog()

# 2. Memuat dataset yang sudah bersih
print("Memuat dataset...")
df = pd.read_csv('membangun_model/heart_disease_preprocessing\heart_cleaned_automated.csv')

# 3. Memisahkan fitur (X) dan target (y)
# 'target' adalah kolom yang ingin kita prediksi
X = df.drop('target', axis=1)
y = df['target']

# 4. Membagi data menjadi data latih dan data uji (80% latih, 20% uji)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print("Dataset berhasil dibagi menjadi data latih dan uji.")

# 5. Memulai MLflow run
# Semua yang terjadi di dalam blok 'with' ini akan dicatat sebagai satu eksperimen.
with mlflow.start_run():
    
    print("Memulai pelatihan model Logistic Regression...")
    # Kita gunakan model yang sederhana 
    model = LogisticRegression(max_iter=1000, random_state=42)
    
    # Melatih model menggunakan data latih
    model.fit(X_train, y_train)
    print("Model berhasil dilatih.")
    
    # Melakukan prediksi pada data uji
    y_pred = model.predict(X_test)
    
    # Menghitung akurasi
    accuracy = accuracy_score(y_test, y_pred)
    
    # MLflow autolog akan mencatat metrik ini secara otomatis,
    # tapi kita cetak manual untuk melihat hasilnya langsung di terminal.
    print(f"Akurasi Model: {accuracy:.4f}")
    
print("\nEksperimen selesai. Jalankan 'mlflow ui' untuk melihat hasilnya.")