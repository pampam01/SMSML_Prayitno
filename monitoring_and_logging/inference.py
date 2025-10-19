import requests
import json
import time
import os
import logging
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Inference")

# --- Konfigurasi ---
MODEL_SERVER_URL = 'http://127.0.0.1:1234/invocations' 
METRICS_EXPORTER_URL = 'http://127.0.0.1:8001' # <-- URL server internal exporter
HEADERS = {'Content-Type': 'application/json'}
CLEANED_DATA_PATH = "../membangun_model/heart_disease_preprocessing/heart_cleaned_automated.csv"
COUNT_FILE = "request_count.txt" # Tetap pakai file untuk persistensi count

# --- Fungsi ambil data sample (tetap sama) ---
def get_sample_data_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        if 'target' in df.columns: df = df.drop('target', axis=1)
        sample_row = df.sample(n=1) 
        data_dict = {"dataframe_split": {"columns": sample_row.columns.tolist(), "data": sample_row.values.tolist()}}
        logger.info(f"Mengambil data sample acak dari {csv_path}")
        return data_dict
    except FileNotFoundError: logger.error(f"Error: File tidak ditemukan di {csv_path}"); return None
    except Exception as e: logger.error(f"Error saat membaca CSV: {e}"); return None

# --- Fungsi untuk MENGIRIM metrik ke exporter ---
def send_metrics_update(latency, age, prediction_value, current_count):
    """Mengirim data metrik via HTTP POST ke server internal exporter."""
    metrics_data = { 
        "latency": latency, 
        "age": age, 
        "prediction": prediction_value,
        "request_count": current_count 
    }
    try:
        # Kirim POST request ke URL exporter
        response = requests.post(METRICS_EXPORTER_URL, data=json.dumps(metrics_data), headers=HEADERS, timeout=2) # Timeout singkat
        response.raise_for_status() # Cek error HTTP
        logger.info(f"📈 Metrik berhasil dikirim ke exporter: {metrics_data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Gagal mengirim metrik ke exporter di {METRICS_EXPORTER_URL}: {e}")
    except Exception as e:
         logger.error(f"Error tak terduga saat mengirim metrik: {e}")


# --- Fungsi untuk mendapatkan & menyimpan count (tetap pakai file agar tidak reset) ---
def get_and_increment_count():
    count = 0
    # Baca count lama
    if os.path.exists(COUNT_FILE):
        try:
            with open(COUNT_FILE, 'r') as f:
                content = f.read().strip()
                if content: count = int(content)
        except Exception: pass # Abaikan jika error baca, mulai dari 0
    
    new_count = count + 1
    
    # Simpan count baru
    try:
        with open(COUNT_FILE, 'w') as f: f.write(str(new_count))
    except Exception as e: logger.warning(f"Gagal menulis count ke {COUNT_FILE}: {e}")
        
    return new_count

# --- Proses Utama Inference ---
# Dapatkan dan update request count DULU
request_number = get_and_increment_count()
logger.info(f"--- Menjalankan Inference ke-{request_number} ---")

# Ambil data sample
logger.info("Mempersiapkan data sample...")
sample_data = get_sample_data_from_csv(CLEANED_DATA_PATH)

# Inisialisasi variabel metrik
latency = 0.0
age_value = 0.0
prediction_value = -1.0 # Nilai default untuk error

if sample_data: 
    logger.info(f"Mengirim request prediksi ke {MODEL_SERVER_URL}...")
    start_time = time.time() 
    response = None 
    
    try:
        # Ambil 'age' sebelum request
        try:
            age_index = sample_data["dataframe_split"]["columns"].index("age")
            age_value = float(sample_data["dataframe_split"]["data"][0][age_index])
        except (ValueError, IndexError): age_value = 0.0; logger.warning("Kolom 'age' tidak ditemukan.")

        # Kirim request prediksi
        response = requests.post(MODEL_SERVER_URL, data=json.dumps(sample_data), headers=HEADERS, timeout=10) 
        end_time = time.time(); latency = end_time - start_time 
        response.raise_for_status() 

        # Proses hasil jika sukses
        prediction_result = response.json()
        prediction_value = float(prediction_result.get('predictions', [0])[0]) 
            
        logger.info("✅ Prediksi berhasil diterima!")
        result_text = "Sakit Jantung" if prediction_value == 1 else "Tidak Sakit Jantung"
        logger.info(f"   Hasil Prediksi: {result_text} (nilai: {prediction_value})")
        logger.info(f"   Waktu Respon (Latency): {latency:.4f} detik")
            
    # Tangani error request prediksi    
    except requests.exceptions.Timeout: end_time = time.time(); latency = end_time - start_time; logger.error("❌ Request Timeout ke server model."); prediction_value = -1.0
    except requests.exceptions.ConnectionError: end_time = time.time(); latency = end_time - start_time; logger.error("❌ Gagal terhubung ke server model."); prediction_value = -1.0 
    except requests.exceptions.RequestException as e: end_time = time.time(); latency = end_time - start_time; logger.error(f"❌ Error saat request prediksi: {e}"); (response is not None and logger.error(f"   Response: {response.text}")); prediction_value = -1.0 
    except Exception as e: end_time = time.time(); latency = end_time - start_time; logger.error(f"❌ Terjadi error tak terduga saat prediksi: {e}"); prediction_value = -1.0
    
else:
    logger.error("Gagal mengambil data sample, inference dibatalkan.")
    latency = 0.0 # Tidak ada latensi jika sample gagal
    age_value = 0.0
    prediction_value = -1.0 # Error state

# Kirim metrik TERKINI (baik sukses/gagal) ke server exporter
send_metrics_update(latency, age_value, prediction_value, request_number)

logger.info(f"--- Inference ke-{request_number} selesai ---")