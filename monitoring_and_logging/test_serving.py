import requests

url = "http://127.0.0.1:1234/invocations"


data = {
    "dataframe_records": [
        {
            "age": 63,
            "sex": 1,
            "cp": 3,
            "trestbps": 145,
            "chol": 233,
            "fbs": 1,
            "restecg": 0,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 0,
            "ca": 0,
            "thal": 1
        }
    ]
}

try:
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Prediksi berhasil diterima!")
        prediction = response.json().get('predictions', [])
        result = "Sakit Jantung" if prediction and prediction[0] == 1 else "Tidak Sakit Jantung"
        print(f"   Hasil Prediksi: {result} (nilai: {prediction})")
    else:
        print(f"❌ Gagal melakukan prediksi. Status Code: {response.status_code}")
        print(f"   Response: {response.text}")

except requests.exceptions.ConnectionError as e:
    print("❌ Gagal terhubung ke server model di port 1234.")
    print("   Pastikan server 'mlflow models serve' sudah berjalan.")
except Exception as e:
    print(f"❌ Terjadi kesalahan: {e}")
