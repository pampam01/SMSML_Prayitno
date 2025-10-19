from prometheus_client import start_http_server, Gauge
import time
import json
import logging
import threading # Diperlukan untuk menjalankan server internal
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver # Diperlukan untuk server HTTP

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Exporter")

# --- Variabel Global untuk menyimpan nilai metrik terakhir ---
# Gunakan lock untuk memastikan update aman dari thread berbeda
current_metrics = {
    "latency": 0.0,
    "age": 0.0,
    "prediction": 0.0,
    "request_count": 0
}
metrics_lock = threading.Lock() 

# --- Definisikan Metrik Prometheus ---
PREDICTION_LATENCY = Gauge('prediction_latency_seconds', 'Waktu prediksi terakhir (detik)')
FEATURE_INPUT_AGE = Gauge('feature_input_age_last', 'Nilai fitur "age" terakhir')
PREDICTION_RESULT = Gauge('prediction_result_last', 'Hasil prediksi terakhir (0/1)')
REQUEST_COUNT = Gauge('total_inference_runs', 'Total berapa kali inference.py dijalankan')

# --- Handler untuk Server HTTP Internal (Menerima Update Metrik) ---
class MetricsUpdateHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global current_metrics
        try:
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            new_metrics = json.loads(post_data_bytes.decode('utf-8'))
            
            # Update variabel global dengan aman menggunakan lock
            with metrics_lock:
                 # Update hanya nilai yang ada di data POST
                 for key in current_metrics:
                     if key in new_metrics:
                         current_metrics[key] = new_metrics[key]
            
            logger.info(f"Metrik diterima via HTTP POST: {new_metrics}")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Metrics updated')
        except json.JSONDecodeError:
            logger.error("Data POST tidak valid (bukan JSON).")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Bad Request: Invalid JSON')
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')

    # Abaikan log standar dari BaseHTTPRequestHandler agar tidak terlalu ramai
    def log_message(self, format, *args):
        return

# --- Fungsi untuk Menjalankan Server HTTP Internal di Thread Terpisah ---
def run_internal_server(port=8001):
    """Menjalankan server yang menerima update metrik."""
    try:
        # Gunakan ThreadingHTTPServer agar bisa handle request sambil loop utama jalan
        server_address = ('', port)
        httpd = HTTPServer(server_address, MetricsUpdateHandler)
        logger.info(f"Server internal untuk update metrik berjalan di port {port}")
        httpd.serve_forever() # Akan berjalan sampai program utama berhenti
    except OSError as e:
         logger.error(f"Gagal memulai server internal di port {port}: {e}. Port mungkin sudah dipakai.")
         # Anda bisa tambahkan exit() jika ini fatal
    except Exception as e:
        logger.error(f"Error tak terduga di server internal: {e}")


# --- Fungsi Utama Exporter ---
def update_prometheus_from_global_metrics():
    """Update Gauge Prometheus dari variabel global."""
    global current_metrics
    try:
        with metrics_lock: # Akses variabel global dengan aman
            # Ambil nilai terbaru dari dictionary global
            latency = current_metrics.get("latency", 0.0)
            age = current_metrics.get("age", 0.0)
            prediction = current_metrics.get("prediction", 0.0)
            count = current_metrics.get("request_count", 0)

        # Set nilai Gauge Prometheus
        PREDICTION_LATENCY.set(latency)
        FEATURE_INPUT_AGE.set(age)
        PREDICTION_RESULT.set(prediction)
        REQUEST_COUNT.set(count)

        logger.info(f"Prometheus metrics updated: count={count}, latency={latency:.4f}s, age={age}, prediction={prediction}")
    except Exception as e:
        logger.error(f"Error saat update Prometheus metrics: {e}")


if __name__ == '__main__':
    # 1. Mulai Server HTTP Internal di thread baru (daemon=True agar mati saat program utama mati)
    internal_port = 8001
    internal_server_thread = threading.Thread(target=run_internal_server, args=(internal_port,), daemon=True)
    internal_server_thread.start()

    # Beri waktu sedikit agar server internal siap (opsional tapi aman)
    time.sleep(1) 
    if not internal_server_thread.is_alive():
         logger.error("Gagal memulai server internal. Exporter tidak bisa menerima update.")
         exit()

    # 2. Mulai Server Prometheus Exporter (di thread utama)
    prometheus_port = 8000
    try:
        start_http_server(prometheus_port)
        logger.info(f"Prometheus exporter berjalan di http://localhost:{prometheus_port}")
    except Exception as e:
        logger.error(f"Gagal memulai server Prometheus exporter di port {prometheus_port}: {e}")
        exit()

    # 3. Loop utama untuk memperbarui Prometheus dari variabel global
    while True:
        try:
            update_prometheus_from_global_metrics()
            time.sleep(5) # Update Prometheus setiap 5 detik
        except KeyboardInterrupt:
            logger.info("Exporter dihentikan.")
            break
        except Exception as e:
            logger.error(f"Error di loop utama exporter: {e}")
            time.sleep(5) # Coba lagi setelah delay jika ada error