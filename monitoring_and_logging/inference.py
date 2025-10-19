import requests
import json
import os # Tambahkan ini

# Nama file untuk menyimpan hitungan
COUNT_FILE = "request_count.txt"

def increment_request_count():
    count = 0
    if os.path.exists(COUNT_FILE):
        try:
            with open(COUNT_FILE, 'r') as f:
                count = int(f.read().strip())
        except ValueError:
            count = 0 # Jika file berisi teks aneh, mulai dari 0
    count += 1
    with open(COUNT_FILE, 'w') as f:
        f.write(str(count))
    return count

# ... (kode sample_data, url, headers tetap sama) ...
sample_data = {
    "dataframe_records": [
        {
            "age": 63,
            "sex": 1,
            "cp": 3,
            "trestbps": 145,
            "chol": 233,
            "fbs": 1,
            "restecg": 0,
            "thalch": 150,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 0,
            "ca": 0,
            "thal": 1
        }
    ]
}
url = 'http://127.0.0.1:1234/invocations'
headers = {'Content-Type': 'application/json'}

# Kirim request POST
try:
    response = requests.post(url, data=json.dumps(sample_data), headers=headers)
    
    # TAMBAHKAN: Panggil fungsi increment setelah request (berhasil atau gagal)
    current_count = increment_request_count()
    print(f"📈 Request ke-{current_count} dicatat.")

    if response.status_code == 200:
        print("✅ Prediksi berhasil diterima!")
        prediction = response.json().get('predictions', [])
        result = "Sakit Jantung" if prediction and prediction[0] == 1 else "Tidak Sakit Jantung"
        print(f"   Hasil Prediksi: {result} (nilai: {prediction})")
    else:
        print(f"❌ Gagal melakukan prediksi. Status Code: {response.status_code}")
        print(f"   Response: {response.text}")

except requests.exceptions.ConnectionError as e:
    # TAMBAHKAN: Catat juga jika gagal terhubung
    current_count = increment_request_count()
    print(f"📈 Request (gagal koneksi) ke-{current_count} dicatat.")
    print("❌ Gagal terhubung ke server model di port 1234.")
    print("   Pastikan server 'mlflow models serve' sudah berjalan.")