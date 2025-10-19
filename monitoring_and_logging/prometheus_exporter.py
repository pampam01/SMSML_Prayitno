from prometheus_client import start_http_server, Gauge
import time
import math # Ganti random dengan math
import os   # Tambahkan os

# Nama file hitungan request
COUNT_FILE = "request_count.txt"

# 1. Definisikan 3 metrik
REQUEST_COUNT = Gauge('total_requests', 'Total jumlah request prediksi (dari file)')
PREDICTION_CONFIDENCE = Gauge('prediction_confidence_score', 'Rata-rata skor kepercayaan prediksi (dummy non-random)')
ERROR_RATE = Gauge('prediction_error_rate', 'Tingkat kesalahan prediksi (dummy non-random)')

# Inisialisasi nilai dummy non-random
confidence_base = 0.85
error_base = 0.03

def update_metrics_from_file():
    """Baca request count dari file, update dummy metrics lainnya."""
    
    # a. Baca request count dari file
    count = 0
    if os.path.exists(COUNT_FILE):
        try:
            with open(COUNT_FILE, 'r') as f:
                count = int(f.read().strip())
        except ValueError:
            count = 0 # Default ke 0 jika file error
    REQUEST_COUNT.set(count)

    # b. Update dummy confidence (non-random)
    confidence_fluctuation = math.sin(time.time() * 0.1) * 0.1
    PREDICTION_CONFIDENCE.set(confidence_base + confidence_fluctuation)

    # c. Update dummy error rate (non-random)
    error_fluctuation = abs(math.cos(time.time() * 0.05)) * 0.02
    ERROR_RATE.set(error_base + error_fluctuation)

    print(f"Metrics updated: requests={REQUEST_COUNT._value.get()}, confidence={PREDICTION_CONFIDENCE._value.get():.2f}, error={ERROR_RATE._value.get():.2f}")

if __name__ == '__main__':
    # Pastikan file count dimulai dari 0 jika belum ada
    if not os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, 'w') as f:
            f.write('0')

    start_http_server(8000)
    print("Prometheus exporter (request count asli) berjalan di http://localhost:8000")

    while True:
        update_metrics_from_file() # Panggil fungsi yang baru
        time.sleep(5)