```python
#!/usr/bin/env python3
"""
JARVIS - cliente local.

Escucha tu micrófono, envía el audio a tu flujo de n8n, reproduce la voz de
respuesta (Fish Audio) y ejecuta en tu PC las acciones permitidas
(abrir webs, apps y carpetas de una lista blanca).

Instalación:   pip install requests numpy sounddevice pygame
Variables:     JARVIS_URL    URL del webhook (producción), p. ej. https://tu-n8n/webhook/jarvis
               JARVIS_TOKEN  el mismo token que pusiste en el nodo "¿Token válido?"
Uso:           python jarvis.py            (pulsas ENTER y hablas)
               python jarvis.py --continuo (escucha siempre, manos libres)
               python jarvis.py --texto    (escribes en vez de hablar)
"""
import argparse
import base64
import collections
import io
import os
import platform
import queue
import subprocess
import sys
import time
import unicodedata
import wave
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import requests
import sounddevice as sd

URL = os.getenv("JARVIS_URL", "https://TU-N8N/webhook/jarvis")
TOKEN = os.getenv("JARVIS_TOKEN", "CAMBIA_ESTE_TOKEN")
SESSION = os.getenv("JARVIS_SESSION", "name")

SR = 16000            # frecuencia de muestreo
BLOCK = 1024          # muestras por bloque (~64 ms)
SILENCIO_FIN = 1.3    # segundos de silencio para dar por terminada la frase
MAX_FRASE = 30        # segundos máximos por frase
MIN_FRASE = 0.6       # frases más cortas se descartan (ruidos)

SO = platform.system()  # Windows / Darwin / Linux
HOME = Path.home()

# --- Lista blanca de apps (nombre -> comando según sistema). Añade las tuyas. ---
APPS = {
    "chrome": {"Windows": "chrome", "Darwin": "Google Chrome", "Linux": "google-chrome"},
    "spotify": {"Windows": "spotify:", "Darwin": "Spotify", "Linux": "spotify"},
    "vscode": {"Windows": "code", "Darwin": "Visual Studio Code", "Linux": "code"},
    "calculadora": {"Windows": "calc", "Darwin": "Calculator", "Linux": "gnome-calculator"},
    "bloc de notas": {"Windows": "notepad", "Darwin": "TextEdit", "Linux": "gedit"},
    "discord": {"Windows": "discord:", "Darwin": "Discord", "Linux": "discord"},
    "whatsapp": {"Windows": "whatsapp:", "Darwin": "WhatsApp", "Linux": "whatsapp-desktop"},
    "telegram": {"Windows": "tg:", "Darwin": "Telegram", "Linux": "telegram-desktop"},
    "explorador": {"Windows": "explorer", "Darwin": "Finder", "Linux": "xdg-open"},
}

# --- Lista blanca de carpetas. Añade las tuyas. ---
CARPETAS = {
    "descargas": HOME / "Downloads",
    "documentos": HOME / "Documents",
    "escritorio": HOME / "Desktop",
    "imagenes": HOME / "Pictures",
    "videos": HOME / "Videos",
    "musica": HOME / "Music",
}


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().strip())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# ----------------------------------------------------------------- audio ----
def rms(bloque) -> float:
    return float(np.sqrt(np.mean(bloque.astype(np.float32) ** 2)))


def grabar(espera_max=None):
    """Graba una frase con detección de silencio. Devuelve int16 o None."""
    q = queue.Queue()

    def callback(indata, frames, t, status):
        q.put(indata.copy())

    with sd.InputStream(samplerate=SR, channels=1, dtype="int16", blocksize=BLOCK, callback=callback):
        ruido = [rms(q.get()) for _ in range(int(0.5 * SR / BLOCK))]
        umbral = max(float(np.mean(ruido)) * 3.0, 350.0)

        previo = collections.deque(maxlen=6)
        frames, hablando, silencio = [], False, 0.0
        t0 = time.time()
        t_habla = t0
        while True:
            bloque = q.get()
            nivel = rms(bloque)
            if not hablando:
                previo.append(bloque)
                if nivel > umbral:
                    hablando = True
                    t_habla = time.time()
                    frames.extend(previo)
                elif espera_max and time.time() - t0 > espera_max:
                    return None
                continue
            frames.append(bloque)
            silencio = silencio + BLOCK / SR if nivel < umbral else 0.0
            if silencio >= SILENCIO_FIN or time.time() - t_habla > MAX_FRASE:
                break

    audio = np.concatenate(frames)
    if len(audio) / SR < MIN_FRASE:
        return None
    return audio


def a_wav(audio) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(audio.tobytes())
    return buf.getvalue()


_mixer_listo = False


def reproducir(b64: str):
    global _mixer_listo
    import pygame
    if not _mixer_listo:
        pygame.mixer.init()
        _mixer_listo = True
    datos = base64.b64decode(b64)
    pygame.mixer.music.load(io.BytesIO(datos), "mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)


# ------------------------------------------------------------------- n8n ----
def enviar(audio=None, texto=None):
    cabeceras = {"x-jarvis-token": TOKEN}
    try:
        if audio is not None:
            r = requests.post(
                URL, headers=cabeceras, timeout=120,
                files={"audio": ("voz.wav", a_wav(audio), "audio/wav")},
                data={"sessionId": SESSION},
            )
        else:
            r = requests.post(URL, headers=cabeceras, timeout=120,
                              data={"texto": texto, "sessionId": SESSION})
    except requests.RequestException as e:
        print(f"[!] No he podido contactar con n8n: {e}")
        return None
    if r.status_code == 401:
        print("[!] Token incorrecto: revisa JARVIS_TOKEN y el nodo '¿Token válido?'.")
        return None
    if r.status_code != 200:
        print(f"[!] n8n respondió {r.status_code}: {r.text[:200]}")
        return None
    try:
        return r.json()
    except ValueError:
        print("[!] Respuesta no válida de n8n.")
        return None


# -------------------------------------------------------------- acciones ----
def lanzar_app(clave: str):
    cmd = APPS.get(normalizar(clave))
    if not cmd:
        print(f"[acción] App no permitida: {clave}")
        return
    valor = cmd.get(SO)
    if not valor:
        print(f"[acción] App sin configurar para {SO}: {clave}")
        return
    if SO == "Windows":
        subprocess.Popen(["cmd", "/c", "start", "", valor])
    elif SO == "Darwin":
        subprocess.Popen(["open", "-a", valor])
    else:
        subprocess.Popen([valor])


def abrir_carpeta(clave: str):
    ruta = CARPETAS.get(normalizar(clave))
    if not ruta or not ruta.exists():
        print(f"[acción] Carpeta no permitida o inexistente: {clave}")
        return
    if SO == "Windows":
        os.startfile(str(ruta))  # type: ignore[attr-defined]
    elif SO == "Darwin":
        subprocess.Popen(["open", str(ruta)])
    else:
        subprocess.Popen(["xdg-open", str(ruta)])


def ejecutar(acciones) -> bool:
    """Ejecuta acciones de la lista blanca. Devuelve True si hay que salir."""
    salir = False
    for a in acciones or []:
        tipo, valor = a.get("tipo"), str(a.get("valor", "")).strip()
        try:
            if tipo == "abrir_web" and valor.lower().startswith(("http://", "https://")):
                webbrowser.open(valor)
            elif tipo == "buscar_google" and valor:
                webbrowser.open("https://www.google.com/search?q=" + quote_plus(valor))
            elif tipo == "buscar_youtube" and valor:
                webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(valor))
            elif tipo == "abrir_app":
                lanzar_app(valor)
            elif tipo == "abrir_carpeta":
                abrir_carpeta(valor)
            elif tipo == "salir":
                salir = True
            else:
                print(f"[acción] Ignorada: {a}")
        except Exception as e:  # una acción fallida no debe tumbar a JARVIS
            print(f"[acción] Error con {a}: {e}")
        time.sleep(0.3)
    return salir


# ------------------------------------------------------------------ main ----
def procesar(resp) -> bool:
    if not resp:
        return False
    print(f"\nJARVIS: {resp.get('respuesta', '')}")
    if resp.get("pantalla"):
        print("\n" + resp["pantalla"] + "\n")
    salir = ejecutar(resp.get("acciones"))
    if resp.get("audio_base64"):
        try:
            reproducir(resp["audio_base64"])
        except Exception as e:
            print(f"[!] No he podido reproducir el audio: {e}")
    else:
        print("[i] Sin audio (revisa la credencial/voz de Fish Audio en n8n).")
    return salir


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--continuo", action="store_true", help="escucha siempre, manos libres")
    p.add_argument("--texto", action="store_true", help="escribe en vez de hablar")
    args = p.parse_args()

    print("JARVIS en línea. Ctrl+C para salir.")
    try:
        while True:
            if args.texto:
                texto = input("\nTú: ").strip()
                if not texto:
                    continue
                resp = enviar(texto=texto)
            else:
                if args.continuo:
                    print("\nEscuchando...")
                    audio = grabar()
                else:
                    input("\nPulsa ENTER y habla...")
                    print("Te escucho...")
                    audio = grabar(espera_max=8)
                if audio is None:
                    print("No he oído nada.")
                    continue
                print("Procesando...")
                resp = enviar(audio=audio)
            if procesar(resp):
                break
    except KeyboardInterrupt:
        pass
    print("\nJARVIS desconectado.")
    sys.exit(0)


if __name__ == "__main__":
    main()
```
