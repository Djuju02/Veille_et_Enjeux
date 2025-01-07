import os
import time
import threading
import datetime
import csv
import random  # Import nécessaire pour la simulation
import numpy as np  # Import de NumPy pour la rotation des matrices

from flask import Flask, render_template, request, jsonify
import pandas as pd
import serial
import logging

app = Flask(__name__)

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
SERIAL_PORT = "COM3"                     # <-- Remplacez par votre port série
BAUD_RATE = 9600                        # <-- Assurez-vous que l'Arduino utilise le même baud rate
CSV_FILE = "grideye_data.csv"
MAX_HISTORY_FRAMES = None                # Nombre maximum de frames à renvoyer pour éviter la surcharge
SIMULATION = True                       # <-- Activer la simulation de données GPS uniquement

# Variables globales pour le thread de lecture
running = True                           # Contrôle la boucle de lecture
in_frame = False
frame_data = {}
last_matrix = [0.0] * 64
last_lat = 0.0
last_lon = 0.0
data_lock = threading.Lock()            # Pour protéger l'accès aux variables partagées
history_lock = threading.Lock()         # Pour protéger l'accès à l'historique en mémoire
history_frames = []                      # Stocke les frames en mémoire pour une lecture rapide

# ---------------------------------------------------------------------
# CONFIGURATION DU LOGGING
# ---------------------------------------------------------------------
logger = logging.getLogger('GrideyeServer')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(message)s')
console_handler.setFormatter(formatter)

# Ajout du handler au logger
logger.addHandler(console_handler)
logger.propagate = False

# ---------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ---------------------------------------------------------------------
def create_csv_if_not_exists(csv_file):
    """Crée un fichier CSV avec les en-têtes si le fichier n'existe pas."""
    if not os.path.exists(csv_file):
        cols = ["timestamp", "GPS_LAT", "GPS_LON"] + [f"PIXEL_{i}" for i in range(64)]
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cols)
        logger.debug(f"CSV créé : {csv_file}")

def append_frame_to_csv(row_data):
    """
    Ajoute une nouvelle ligne au fichier CSV.
    row_data = [timestamp, GPS_LAT, GPS_LON, PIXEL_0, ..., PIXEL_63]
    """
    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row_data)
        logger.debug(f"Frame ajoutée au CSV à {row_data[0]}")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans le CSV : {e}")

def load_history_into_memory():
    """Charge les frames du CSV dans la mémoire pour une lecture rapide."""
    global history_frames
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
            df = df.sort_values("timestamp")
            with history_lock:
                history_frames = df.to_dict(orient='records')[-MAX_HISTORY_FRAMES:]
            logger.debug(f"Historique chargé en mémoire avec {len(history_frames)} frames.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique : {e}")

# ---------------------------------------------------------------------
# THREAD DE LECTURE SÉRIE
# ---------------------------------------------------------------------
def reader_thread():
    global running, in_frame, frame_data, last_matrix, last_lat, last_lon, history_frames

    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Attendre que la connexion série soit établie
        logger.debug(f"Port série '{SERIAL_PORT}' ouvert avec succès.")
    except Exception as e:
        logger.error(f"Impossible d'ouvrir {SERIAL_PORT}: {e}")
        return

    while running:
        try:
            line = ser.readline().decode("utf-8").strip()
            logger.debug(f"Ligne reçue: {line}")  # Log de chaque ligne reçue

            if not line:
                continue

            if line == "BEGIN_FRAME":
                in_frame = True
                frame_data = {}
                logger.debug("Début d'une nouvelle frame.")
                continue

            if line == "END_FRAME":
                in_frame = False
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [now_str]
                pix_array = []

                if SIMULATION:
                    # Générer des coordonnées GPS aléatoires en France
                    gps_lat = random.uniform(41.0, 51.0)   # Latitude entre 41°N et 51°N
                    gps_lon = random.uniform(-5.0, 10.0)   # Longitude entre 5°W et 10°E
                    row.append(f"{gps_lat:.6f}")
                    row.append(f"{gps_lon:.6f}")
                    logger.debug(f"GPS simulé: lat={gps_lat}, lon={gps_lon}")
                else:
                    # Récupère GPS_LAT et GPS_LON depuis frame_data
                    gps_lat_str = frame_data.get("GPS_LAT", "0")
                    gps_lon_str = frame_data.get("GPS_LON", "0")
                    try:
                        gps_lat = float(gps_lat_str)
                    except ValueError:
                        gps_lat = None
                        logger.warning(f"GPS_LAT invalide: '{gps_lat_str}'. Frame ignorée.")
                    try:
                        gps_lon = float(gps_lon_str)
                    except ValueError:
                        gps_lon = None
                        logger.warning(f"GPS_LON invalide: '{gps_lon_str}'. Frame ignorée.")

                    # Vérifier si GPS_LAT et GPS_LON sont valides
                    if gps_lat is None or gps_lon is None:
                        logger.warning("Frame avec GPS invalide. Frame ignorée.")
                        continue

                    row.append(f"{gps_lat:.6f}")
                    row.append(f"{gps_lon:.6f}")

                # Récupère les 64 pixels depuis frame_data
                pixels_valid = True
                for i in range(64):
                    key = f"PIXEL_{i}"
                    if key not in frame_data:
                        logger.warning(f"{key} manquant. Frame ignorée.")
                        pixels_valid = False
                        break
                    val_str = frame_data.get(key, "0")
                    try:
                        valf = float(val_str)
                    except ValueError:
                        valf = None
                        pixels_valid = False
                        logger.warning(f"{key} invalide: '{val_str}'. Frame ignorée.")
                        break
                    pix_array.append(valf)
                    row.append(f"{valf:.2f}")
                    logger.debug(f"{key} = {valf}")  # Log des pixels

                # Vérifier si tous les pixels sont valides
                if not pixels_valid or None in pix_array:
                    logger.warning("Frame avec pixels invalides ou manquants. Frame ignorée.")
                    continue

                # Appliquer la rotation de 90 degrés vers la gauche
                matrix = np.array(pix_array).reshape((8, 8))
                rotated_matrix = np.rot90(matrix, 1)  # Rotation anti-horaire
                rotated_pix_array = rotated_matrix.flatten().tolist()

                # Utiliser les pixels rotés pour l'enregistrement et l'affichage
                pix_array = rotated_pix_array
                row = [now_str, f"{gps_lat:.6f}", f"{gps_lon:.6f}"] + [f"{val:.2f}" for val in pix_array]

                logger.debug(f"Frame rotée : {pix_array}")
                append_frame_to_csv(row)

                with data_lock:
                    last_matrix = pix_array
                    last_lat = gps_lat
                    last_lon = gps_lon

                with history_lock:
                    history_frames.append({
                        "timestamp": now_str,
                        "GPS_LAT": gps_lat,
                        "GPS_LON": gps_lon
                    } | {f"PIXEL_{i}": pix_array[i] for i in range(64)})
                    if MAX_HISTORY_FRAMES is not None and len(history_frames) > MAX_HISTORY_FRAMES:
                        history_frames.pop(0)  # Supprimer la frame la plus ancienne

                logger.debug(f"Frame simulée ajoutée avec GPS: lat={gps_lat}, lon={gps_lon}")
                continue

            if in_frame:
                if "=" in line:
                    key, val = line.split("=", 1)
                    frame_data[key] = val
                    logger.debug(f"{key} = {val}")

        except Exception as e:
            logger.error(f"Erreur dans le thread série : {e}")
            if ser:
                ser.close()
                ser = None
            break


# ---------------------------------------------------------------------
# ROUTES FLASK
# ---------------------------------------------------------------------

@app.route("/")
def index():
    """Page principale (HTML)."""
    return render_template("index.html")

@app.route("/api/live")
def api_live():
    """
    Retourne la dernière frame enregistrée.
    Format JSON : { "lat": float, "lon": float, "pixels": [float, ...] }
    """
    with data_lock:
        mat_copy = list(last_matrix)
        lat_copy = last_lat
        lon_copy = last_lon
    return jsonify({
        "lat": lat_copy,
        "lon": lon_copy,
        "pixels": mat_copy
    })

@app.route("/api/history")
def api_history():
    """
    Retourne l'historique des frames en appliquant les filtres si fournis.
    Params (optionnels) :
        - dateMin (YYYY-MM-DDTHH:MM)
        - dateMax (YYYY-MM-DDTHH:MM)
        - latMin
        - latMax
        - lonMin
        - lonMax
        - pixelMin
        - pixelMax
        - page (int)       # Numéro de page
        - per_page (int)   # Nombre de frames par page
    Format JSON :
    {
        "frames": [...],
        "total": int,
        "page": int,
        "per_page": int
    }
    """
    dateMin = request.args.get("dateMin", "").strip()
    dateMax = request.args.get("dateMax", "").strip()
    latMin  = request.args.get("latMin", "").strip()
    latMax  = request.args.get("latMax", "").strip()
    lonMin  = request.args.get("lonMin", "").strip()
    lonMax  = request.args.get("lonMax", "").strip()
    pixelMin = request.args.get("pixelMin", "").strip()
    pixelMax = request.args.get("pixelMax", "").strip()
    page    = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))

    logger.debug(f"/api/history appelé avec les filtres: dateMin={dateMin}, dateMax={dateMax}, latMin={latMin}, latMax={latMax}, lonMin={lonMin}, lonMax={lonMax}, pixelMin={pixelMin}, pixelMax={pixelMax}, page={page}, per_page={per_page}")

    with history_lock:
        if not history_frames:
            logger.debug("Aucune frame dans l'historique.")
            return jsonify({"frames": [], "total": 0, "page": page, "per_page": per_page})

        df = pd.DataFrame(history_frames)

    if df.empty:
        logger.debug("DataFrame vide après chargement.")
        return jsonify({"frames": [], "total": 0, "page": page, "per_page": per_page})

    # Convertir les types de données
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["GPS_LAT"]    = pd.to_numeric(df["GPS_LAT"], errors="coerce")
    df["GPS_LON"]    = pd.to_numeric(df["GPS_LON"], errors="coerce")

    # Appliquer les filtres
    if dateMin:
        try:
            dmin = pd.to_datetime(dateMin)
            df = df[df["timestamp"] >= dmin]
            logger.debug(f"Filtrage par dateMin: {dmin}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par dateMin: {e}")
    if dateMax:
        try:
            dmax = pd.to_datetime(dateMax)
            df = df[df["timestamp"] <= dmax]
            logger.debug(f"Filtrage par dateMax: {dmax}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par dateMax: {e}")
    if latMin:
        try:
            latMinf = float(latMin)
            df = df[df["GPS_LAT"] >= latMinf]
            logger.debug(f"Filtrage par latMin: {latMinf}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par latMin: {e}")
    if latMax:
        try:
            latMaxf = float(latMax)
            df = df[df["GPS_LAT"] <= latMaxf]
            logger.debug(f"Filtrage par latMax: {latMaxf}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par latMax: {e}")
    if lonMin:
        try:
            lonMinf = float(lonMin)
            df = df[df["GPS_LON"] >= lonMinf]
            logger.debug(f"Filtrage par lonMin: {lonMinf}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par lonMin: {e}")
    if lonMax:
        try:
            lonMaxf = float(lonMax)
            df = df[df["GPS_LON"] <= lonMaxf]
            logger.debug(f"Filtrage par lonMax: {lonMaxf}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par lonMax: {e}")
    if pixelMin:
        try:
            pixelMinf = float(pixelMin)
            # Filtrer les frames où **tous les pixels** >= pixelMinf
            df = df[df[[f"PIXEL_{i}" for i in range(64)]].min(axis=1) >= pixelMinf]
            logger.debug(f"Filtrage par pixelMin: {pixelMinf}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par pixelMin: {e}")
    if pixelMax:
        try:
            pixelMaxf = float(pixelMax)
            # Filtrer les frames où **tous les pixels** <= pixelMaxf
            df = df[df[[f"PIXEL_{i}" for i in range(64)]].max(axis=1) <= pixelMaxf]
            logger.debug(f"Filtrage par pixelMax: {pixelMaxf}")
        except Exception as e:
            logger.warning(f"Erreur de filtrage par pixelMax: {e}")

    df = df.sort_values("timestamp").reset_index(drop=True)

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    df_page = df.iloc[start:end]

    logger.debug(f"Nombre de frames après filtrage et limitation: {len(df_page)}")

    result = []
    for idx, row in df_page.iterrows():
        try:
            pixel_values = [float(row[f"PIXEL_{i}"]) for i in range(64)]
        except Exception as e:
            logger.warning(f"Erreur lors de la lecture des pixels pour l'index {idx}: {e}")
            pixel_values = [0.0] * 64
        frame = {
            "index": int(start + idx),
            "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if not pd.isna(row["timestamp"]) else "",
            "lat": float(row["GPS_LAT"]) if not pd.isna(row["GPS_LAT"]) else None,
            "lon": float(row["GPS_LON"]) if not pd.isna(row["GPS_LON"]) else None,
            "pixels": pixel_values
        }
        result.append(frame)

    logger.debug(f"Donnees retournees: {len(result)} frames sur un total de {total}")
    return jsonify({
        "frames": result,
        "total": total,
        "page": page,
        "per_page": per_page
    })


@app.route("/api/frame/<int:frame_id>")
def api_frame(frame_id):
    """
    Retourne une frame spécifique par son index.
    Format JSON :
    {
        "index": int,
        "timestamp": "YYYY-MM-DD HH:MM:SS",
        "lat": float,
        "lon": float,
        "pixels": [float, ...]
    }
    """
    with history_lock:
        if frame_id < 0 or frame_id >= len(history_frames):
            logger.warning(f"Frame ID {frame_id} non trouvée.")
            return jsonify({"error": "Frame not found"}), 404

        frame = history_frames[frame_id]
    
    try:
        pixels = [frame[f"PIXEL_{i}"] for i in range(64)]
    except Exception as e:
        logger.warning(f"Erreur lors de la lecture des pixels pour l'index {frame_id}: {e}")
        pixels = [0.0] * 64

    response = {
        "index": int(frame_id),
        "timestamp": frame["timestamp"],
        "lat": float(frame["GPS_LAT"]) if not pd.isna(frame["GPS_LAT"]) else None,
        "lon": float(frame["GPS_LON"]) if not pd.isna(frame["GPS_LON"]) else None,
        "pixels": pixels
    }

    logger.debug(f"Frame ID {frame_id} retourne.")
    return jsonify(response)

@app.route("/shutdown")
def shutdown():
    """Route pour arrêter proprement le serveur Flask et le thread de lecture série."""
    global running
    running = False
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    logger.debug("Serveur en cours d'arrêt...")
    return "Server shutting down..."

# ---------------------------------------------------------------------
# LANCEMENT DU SERVEUR
# ---------------------------------------------------------------------
def start_background_thread():
    create_csv_if_not_exists(CSV_FILE)
    load_history_into_memory()
    t = threading.Thread(target=reader_thread, daemon=True)
    t.start()
    logger.debug("Thread série démarré.")

if __name__ == "__main__":
    start_background_thread()
    app.run(debug=False, host="0.0.0.0", port=5000)
