from picamera2 import Picamera2, Preview
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
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, ean, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        now = time.time()
        if ean != last_ean or (now - last_detected_time) > DETECTION_PAUSE_SEC:
            logging.info(f"📦 Neuer Barcode erkannt: {ean}")
            last_ean = ean
            last_detected_time = now
            send_to_internal_api(ean)
    return frame

def main():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "BGR888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    logging.info("📷 Kamera gestartet. Halte QR/Barcode vor die Kamera (q zum Beenden).")

    try:
        while True:
            frame = picam2.capture_array()
            frame = decode_and_process(frame)
            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        logging.info("🛑 Scanner beendet.")

if __name__ == "__main__":
    main()
