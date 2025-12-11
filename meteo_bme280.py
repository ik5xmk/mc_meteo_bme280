#!/usr/bin/env python3

import re
import time
from datetime import datetime
import serial

# ---------------------------
# CONFIGURAZIONE
# ---------------------------
SERIAL_PORT = "/dev/ttyUSB0"   # Default richiesto
BAUD_RATE = 115200
CMD_TIMEOUT = 6.0              # secondi totali per leggere la risposta
READ_DELAY = 0.05              # pausa tra read loop
WRITE_SETTLE = 0.2             # pausa breve dopo l'invio del comando --wx
TIMEOUT_OPEN = 3               # timeout apertura seriale

# Destinatario MeshCom (modifica se serve)
DST_CALLSIGN = "22299"

# ---------------------------
# PATTERN (richiedono etichetta)
# ---------------------------
TEMP_RE = re.compile(
    r'\b(?:TEMP|TEMPERATURE|T)\b[\s:=]*([+-]?\d+(?:[.,]\d+)?)\s*(?:°\s*C|°C|C)?',
    re.IGNORECASE
)
# HUM: accetta % , %rH, RH, ecc.
HUM_RE = re.compile(
    r'\b(?:HUM|HUMIDITY|RH|RELATIVE_HUMIDITY)\b[\s:=]*([+-]?\d+(?:[.,]\d+)?)\s*(?:%rH|%|rH)?',
    re.IGNORECASE
)

# ---------------------------
# FUNZIONI DI PARSING (prendono l'ultima occorrenza etichettata)
# ---------------------------
def parse_last_labeled_temp_hum(lines):
    """
    Cerca tutte le occorrenze etichettate e ritorna l'ultima trovata per TEMP e HUM.
    Restituisce (temp_or_None, hum_or_None, debug_list).
    debug_list contiene tuple (line_index, line_text, which_pattern, matched_str)
    """
    temp_matches = []
    hum_matches = []
    debug = []

    for idx, line in enumerate(lines):
        # TEMP
        m_temp = TEMP_RE.search(line)
        if m_temp:
            s = m_temp.group(1).replace(',', '.')
            try:
                val = float(s)
                temp_matches.append((idx, line, s))
                debug.append((idx, line, 'TEMP_RE', s))
            except ValueError:
                debug.append((idx, line, 'TEMP_RE_parse_error', m_temp.group(1)))

        # HUM
        m_hum = HUM_RE.search(line)
        if m_hum:
            s = m_hum.group(1).replace(',', '.')
            try:
                val = float(s)
                hum_matches.append((idx, line, s))
                debug.append((idx, line, 'HUM_RE', s))
            except ValueError:
                debug.append((idx, line, 'HUM_RE_parse_error', m_hum.group(1)))

    temp = None
    hum = None
    if temp_matches:
        # scegli l'ultima occorrenza (massimo idx)
        last = max(temp_matches, key=lambda t: t[0])
        temp = float(last[2])
    if hum_matches:
        last = max(hum_matches, key=lambda t: t[0])
        hum = float(last[2])

    return temp, hum, debug

# ---------------------------
# FUNZIONE PRINCIPALE
# ---------------------------
def query_wx_and_send():
    print(f"[{datetime.now()}] Apertura seriale {SERIAL_PORT} @ {BAUD_RATE} baud")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5) as ser:
            # pulizia buffer se disponibile
            try:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
            except Exception:
                pass

            # INVIO COMANDO --wx
            cmd = "--wx\n"
            print(f"[{datetime.now()}] Invio comando: {cmd.strip()}")
            ser.write(cmd.encode('utf-8'))
            ser.flush()

            # breve attesa per far partire la risposta (alcuni moduli impiegano qualche decina di ms)
            time.sleep(WRITE_SETTLE)

            # Leggi per CMD_TIMEOUT secondi tutte le righe
            start = time.time()
            collected = []
            while (time.time() - start) < CMD_TIMEOUT:
                try:
                    line = ser.readline()
                except Exception as e:
                    print(f"Errore durante readline(): {e}")
                    break

                if not line:
                    time.sleep(READ_DELAY)
                    continue

                try:
                    text = line.decode('utf-8', errors='replace').strip()
                except Exception:
                    text = str(line)
                if text:
                    # Normalizza eventuali caratteri di controllo tipici (es. caratteri non-ASCII)
                    print(f"[RX] {text}")
                    collected.append(text)

            # Parse: prendi l'ultima occorrenza etichettata TEMP e HUM
            temp, hum, debug = parse_last_labeled_temp_hum(collected)

            # Debug parsing
            print("=== Debug parsing ===")
            if debug:
                for d in debug:
                    print(f"  line {d[0]} pattern {d[2]} -> matched '{d[3]}' in: {d[1]}")
            else:
                print("  Nessun match etichettato trovato nelle righe ricevute.")

            # Se non troviamo entrambi, non inviamo
            if (temp is None) or (hum is None):
                print(f"[{datetime.now()}] Mancano valori etichettati: TEMP={temp} HUM={hum} -> nessun invio via MeshCom.")
                return False

            # Normalizza i valori per il messaggio
            temp_str = f"{round(temp, 1)}"
            hum_str = f"{int(round(hum))}"

            # Composizione messaggio e invio MeshCom (::{{CALL}} messaggio)
            # personalizzare a piacere con località, etc.
            messaggio = f"Poggio a Caiano (PO) - Temp: {temp_str}C Umid: {hum_str}%"
            comando_mesh = f"::{{{DST_CALLSIGN}}} {messaggio}\n"
            print(f"[{datetime.now()}] Invio MeshCom: {comando_mesh.strip()}")

            try:
                ser.write(comando_mesh.encode('utf-8'))
                ser.flush()
                print(f"[{datetime.now()}] Messaggio inviato correttamente.")
                return True
            except Exception as e:
                print(f"Errore invio MeshCom: {e}")
                return False

    except serial.SerialException as e:
        print(f"ERRORE apertura seriale {SERIAL_PORT}: {e}")
        return False
    except Exception as e:
        print(f"Errore generico: {e}")
        return False

# ---------------------------
# ESECUZIONE
# ---------------------------
if __name__ == "__main__":
#    print("Esempio di output atteso (per riferimento):")
#    print("--wx")
#    print("...TEMP: 15.9 °C off 0.000")
#    print("...HUM: 49.4 %rH")
#    print("----------")
    sent = query_wx_and_send()
    if sent:
        print("Operazione completata: messaggio inviato.")
    else:
        print("Operazione terminata senza invio.")
