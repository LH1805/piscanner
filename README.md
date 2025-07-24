# piscanner

# Fridge Barcode Scanner

Ein einfacher Barcode-Scanner für den Raspberry Pi mit:
- Webcam-Stream
- Barcode-Erkennung (EAN)
- Anfrage an lokale API im VPN
- Visuelle Darstellung (optional)

## Voraussetzungen

- Python 3.9+
- USB-Webcam oder Raspberry Pi Camera (mit V4L2)
- Installierte Pakete:
  ```bash
  pip install -r requirements.txt
