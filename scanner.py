from picamera2 import Picamera2
import cv2
import time
from pyzbar.pyzbar import decode
import requests
import logging

# Konfiguration
SEND_API_ENDPOINT = "http://<VPN-IP>/api/receive-ean"
DETECTION_PAUSE_SEC = 2
DEBUG = True

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

last_detected_time = 0
last_ean = None

def send_to_internal_api(ean):
    try:
        res = requests.post(SEND_API_ENDPOINT, json={"ean": ean}, timeout=3)
        if res.status_code == 200:
            logging.info(f"✅ EAN {ean} erfolgreich gesendet.")
        else:
            logging.warning(f"⚠️ API meldete Status {res.status_code}.")
    except Exception as e:
        logging.error(f"❌ Fehler beim Senden an API: {e}")

def decode_and_process(frame):
    global last_detected_time, last_ean
    barcodes = decode(frame)
    for barcode in barcodes:
        ean = barcode.data.decode('utf-8')
        x, y, w, h = barcode.rect
        # Hier kannst du das Bild markieren, aber nicht anzeigen
        now = time.time()
        if ean != last_ean or (now - last_detected_time) > DETECTION_PAUSE_SEC:
            logging.info(f"📦 Neuer Barcode erkannt: {ean}")
            last_ean = ean
            last_detected_time = now
            send_to_internal_api(ean)
    return frame

def main():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    logging.info("📷 Kamera gestartet. Halte QR/Barcode vor die Kamera.")

    try:
        while True:
            frame = picam2.capture_array()
            decode_and_process(frame)
            # Kein cv2.imshow oder cv2.waitKey nötig
    finally:
        picam2.stop()
        logging.info("🛑 Scanner beendet.")

if __name__ == "__main__":
    main()
