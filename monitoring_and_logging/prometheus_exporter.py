from prometheus_client import start_http_server, Gauge
import time
import random


REQUEST_COUNT = Gauge('total_requests', 'Total jumlah request prediksi')
PREDICTION_CONFIDENCE = Gauge('prediction_confidence_score', 'Rata-rata skor kepercayaan prediksi')
ERROR_RATE = Gauge('prediction_error_rate', 'Tingkat kesalahan prediksi')

def generate_metrics():
    """Fungsi sederhana untuk mensimulasikan perubahan metrik."""
    REQUEST_COUNT.inc(random.randint(1, 5)) 
    PREDICTION_CONFIDENCE.set(random.uniform(0.75, 0.99)) 
    ERROR_RATE.set(random.uniform(0.01, 0.05)) 

if __name__ == '__main__':
    start_http_server(8000)
    print("Prometheus exporter berjalan di http://localhost:8000")

 
    while True:
        generate_metrics()
        time.sleep(5) 