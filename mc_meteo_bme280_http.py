#!/usr/bin/env python3

import re
import socket
import json
import urllib.request
from datetime import datetime

# ---------------------------
# CONFIGURAZIONE
# ---------------------------
WX_HOST = "192.168.1.143"
WX_URL = f"http://{WX_HOST}/?page=wx"
HTTP_TIMEOUT = 5.0

UDP_PORT = 1799       # (default meshcom port on lora board side)   
UDP_TIMEOUT = 2.0

DST_CALLSIGN = "22299"
LOCATION = "Sesto Fiorentino (home qth)"

# ---------------------------
# PATTERN HTML
# ---------------------------
TEMP_RE = re.compile(
    r'<tr>\s*<td>\s*Temperature\s*</td>\s*<td>\s*([+-]?\d+(?:[.,]\d+)?)\s*&deg;\s*C',
    re.IGNORECASE
)

HUM_RE = re.compile(
    r'<tr>\s*<td>\s*Humidity\s*</td>\s*<td>\s*([+-]?\d+(?:[.,]\d+)?)\s*%\s*rH',
    re.IGNORECASE
)

QFE_RE = re.compile(
    r'<tr>\s*<td>\s*QFE\s*</td>\s*<td>\s*([+-]?\d+(?:[.,]\d+)?)\s*hPa',
    re.IGNORECASE
)

QNH_RE = re.compile(
    r'<tr>\s*<td>\s*QNH\s*</td>\s*<td>\s*([+-]?\d+(?:[.,]\d+)?)\s*hPa',
    re.IGNORECASE
)

# ---------------------------
# PARSING HTML
# ---------------------------
def parse_wx_from_html(html):
    data = {"temp": None, "hum": None, "qfe": None, "qnh": None}
    debug = []

    def extract(regex, key):
        m = regex.search(html)
        if not m:
            return
        s = m.group(1).replace(',', '.')
        try:
            val = float(s)
            data[key] = val
            debug.append((key.upper(), s))
        except ValueError:
            debug.append((f"{key.upper()}_parse_error", s))

    extract(TEMP_RE, "temp")
    extract(HUM_RE, "hum")
    extract(QFE_RE, "qfe")
    extract(QNH_RE, "qnh")

    return data, debug

# ---------------------------
# INVIO UDP (MC JSON)
# ---------------------------
def send_udp_message(message_text):
    payload = {
        "type": "msg",
        "dst": DST_CALLSIGN,
        "msg": message_text
    }

    data = json.dumps(payload).encode("utf-8")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDP_TIMEOUT)
        sock.sendto(data, (WX_HOST, UDP_PORT))
        sock.close()

        current_dateTime = datetime.now()
        print(f"Inviato ({current_dateTime}): {data} -> {WX_HOST}:{UDP_PORT}")
        return True

    except Exception as e:
        print(f"Errore invio UDP: {e}")
        return False

# ---------------------------
# FUNZIONE PRINCIPALE
# ---------------------------
def query_wx_http_and_send_udp():
    print(f"[{datetime.now()}] Lettura dati meteo via HTTP")
    print(f"[{datetime.now()}] URL: {WX_URL}")

    try:
        with urllib.request.urlopen(WX_URL, timeout=HTTP_TIMEOUT) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Errore HTTP: {e}")
        return False

    data, debug = parse_wx_from_html(html)

    print("=== Debug parsing ===")
    for d in debug:
        print(f"  {d[0]} -> {d[1]}")

    if data["temp"] is None or data["hum"] is None:
        print(f"[{datetime.now()}] Valori mancanti: TEMP={data['temp']} HUM={data['hum']}")
        return False

    temp_str = f"{round(data['temp'], 1)}"
    hum_str = f"{int(round(data['hum']))}"

    parts = [
        LOCATION,
        f"Temp: {temp_str}C",
        f"Umid: {hum_str}%"
    ]

    if data["qfe"] and data["qfe"] != 0.0:
        parts.append(f"QFE: {round(data['qfe'], 1)}hPa")

    if data["qnh"] and data["qnh"] != 0.0:
        parts.append(f"QNH: {round(data['qnh'], 1)}hPa")

    message_text = " ".join(parts)

    return send_udp_message(message_text)

# ---------------------------
# ESECUZIONE
# ---------------------------
if __name__ == "__main__":
    ok = query_wx_http_and_send_udp()
    if ok:
        print("Operazione completata: messaggio MC inviato via UDP.")
    else:
        print("Operazione terminata senza invio.")
