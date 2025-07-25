from picamera2 import Picamera2
import cv2
import time
from pyzbar.pyzbar import decode
import requests
import logging

# Konfiguration
API_URL = "http://141.72.13.72:8000/api/product-trigger/trigger-popup"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJTZXJ2aWNlX0FjY291bnQiLCJleHAiOjIwNjg3MDYyNDh9.MgzTarNa8w7TTXVN16oBpEP4h07qWhh4EWT1yPFBNwo"
DETECTION_PAUSE_SEC = 2
DEBUG = True

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

DEVICE_ID = "barcode_scanner"
TRIGGER_TYPE = "ean"

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

last_detected_time = 0
last_ean = None

def send_to_api(ean):
    payload = {
        "ean": ean,
        "trigger_type": TRIGGER_TYPE,
        "device_id": DEVICE_ID
    }
    try:
        res = requests.post(API_URL, json=payload, headers=HEADERS, timeout=3)
        if res.status_code == 200:
            logging.info(f"✅ API-Trigger erfolgreich: {res.json().get('message')}")
        else:
            logging.warning(f"⚠️ API-Fehler: Status {res.status_code}, Response: {res.text}")
    except Exception as e:
        logging.error(f"❌ Fehler beim API-Request: {e}")

def decode_and_process(frame):
    global last_detected_time, last_ean
    barcodes = decode(frame)
    for barcode in barcodes:
        ean = barcode.data.decode('utf-8')
        now = time.time()
        if ean != last_ean or (now - last_detected_time) > DETECTION_PAUSE_SEC:
            logging.info(f"📦 Neuer Barcode erkannt: {ean}")
            last_ean = ean
            last_detected_time = now
            send_to_api(ean)
            # 🕒 Kurze Pause zur besseren Sichtbarkeit in Konsole
            logging.debug("⏸️ Pause nach Scan zur Anzeige von Logs...")
            time.sleep(2)  # 2 Sekunden Pause


def main():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    logging.info("📷 Kamera gestartet. Warte auf Barcodes...")

    try:
        while True:
            frame = picam2.capture_array()
            decode_and_process(frame)
    finally:
        picam2.stop()
        logging.info("🛑 Scanner beendet.")

if __name__ == "__main__":
    main()
