# Robust barcode scanner with local API forwarding and Raspberry Pi compatibility

import cv2
from pyzbar.pyzbar import decode
import time
import requests
import logging
import os

# --- Konfiguration ---
SEND_API_ENDPOINT = "http://<VPN-IP>/api/receive-ean"  # z.B. http://192.168.1.10:5001/api/receive-ean
DETECTION_PAUSE_SEC = 2
DEBUG = True

# --- Logger Setup ---
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

# --- EAN-Cache ---
last_detected_time = 0
last_ean = None

def send_to_internal_api(ean):
    try:
        response = requests.post(SEND_API_ENDPOINT, json={"ean": ean}, timeout=3)
        if response.status_code == 200:
            logging.info(f"✅ EAN {ean} erfolgreich an interne API gesendet.")
        else:
            logging.warning(f"⚠️ API antwortete mit Status {response.status_code}.")
    except Exception as e:
        logging.error(f"❌ Fehler beim Senden an interne API: {e}")

def decode_and_process(frame):
    global last_detected_time, last_ean
    barcodes = decode(frame)

    for barcode in barcodes:
        ean = barcode.data.decode('utf-8')
        x, y, w, h = barcode.rect

        # Visualisierung
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, ean, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        now = time.time()
        if ean != last_ean or (now - last_detected_time) > DETECTION_PAUSE_SEC:
            logging.info(f"📦 Neuer Barcode erkannt: {ean}")
            last_ean = ean
            last_detected_time = now
            send_to_internal_api(ean)

    return frame

def main():
    logging.info("🔄 Starte Barcode-Erkennung...")

    cap = cv2.VideoCapture(10)  # Raspberry Pi: ggf. cv2.VideoCapture(0, cv2.CAP_V4L)

    if not cap.isOpened():
        logging.critical("❌ Kamera konnte nicht geöffnet werden.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("⚠️ Fehler beim Lesen des Kamerabildes.")
            continue

        frame = decode_and_process(frame)
        cv2.imshow("Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logging.info("🛑 Scanner beendet.")

if __name__ == "__main__":
    main()
