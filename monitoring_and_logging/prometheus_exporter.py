from prometheus_client import start_http_server, Gauge
import time
import random

# Buat tiga metrik berbeda untuk dipantau
REQUEST_COUNT = Gauge('total_requests', 'Total jumlah request prediksi')
PREDICTION_CONFIDENCE = Gauge('prediction_confidence_score', 'Rata-rata skor kepercayaan prediksi')
ERROR_RATE = Gauge('prediction_error_rate', 'Tingkat kesalahan prediksi')

def generate_metrics():
    """Fungsi sederhana untuk mensimulasikan perubahan metrik."""
    REQUEST_COUNT.inc(random.randint(1, 5)) # Simulasikan ada request baru
    PREDICTION_CONFIDENCE.set(random.uniform(0.75, 0.99)) # Simulasikan skor kepercayaan
    ERROR_RATE.set(random.uniform(0.01, 0.05)) # Simulasikan tingkat error yang rendah

if __name__ == '__main__':
    # Mulai server HTTP untuk mengekspos metrik di port 8000
    start_http_server(8000)
    print("Prometheus exporter berjalan di http://localhost:8000")

    # Terus menerus menghasilkan nilai metrik baru
    while True:
        generate_metrics()
        time.sleep(5) # Update setiap 5 detik