Voici le fichier README en français et en anglais :

```markdown
# Projet Capteur Infrarouge avec Arduino et Flask

## Description

Ce projet intègre un capteur infrarouge (Grid-EYE AMG8833) connecté à un Arduino pour collecter des données thermiques et des coordonnées GPS. Les données sont stockées dans un fichier CSV et accessibles via des APIs Flask. Une interface web permet la visualisation des données en temps réel, l'exploration de l'historique et la cartographie.

---

# Infrared Sensor Project with Arduino and Flask

## Description

This project integrates an infrared sensor (Grid-EYE AMG8833) with Arduino to collect thermal data and GPS coordinates. Data is stored in a CSV file and made available via Flask APIs. A web interface provides real-time data visualization, historical exploration, and mapping.

---

## Fonctionnalités / Features

- **Collecte de données / Data Collection** :
  - Capteur infrarouge (tableau 64 pixels) et coordonnées GPS (réelles ou simulées).
  - Sauvegarde des données dans un fichier CSV.
  - Infrared sensor (64-pixel array) and GPS coordinates (real or simulated).
  - Data storage in a CSV file.

- **APIs** :
  - **Dernière mesure / Latest data** : `/api/live`
  - **Historique filtré / Historical data** : `/api/history` (avec filtres / with filters)
  - **Données spécifiques / Specific frame** : `/api/frame/<frame_id>`

- **Interface web interactive / Interactive Web Dashboard** :
  - Visualisation des données en temps réel.
  - Exploration de l'historique avec filtres et pagination.
  - Visualisation des points GPS sur une carte.
  - Real-time data visualization.
  - Historical data exploration with filters and pagination.
  - Mapping of GPS points.

---

## Structure du Projet / Project Structure

- `Infrared_Arduino_code.ino` : Code Arduino pour collecter les données / Arduino code for sensor data collection.
- `server.py` : Serveur Flask pour gérer les données et exposer les APIs / Flask server for data management and API exposure.
- `grideye_data.csv` : Fichier CSV contenant les données collectées / CSV file storing collected data.
- `index.html` : Interface web pour visualiser les données / Web interface for data visualization.

---

## Prérequis / Requirements

- **Logiciels / Software** :
  - Python 3.x
  - IDE Arduino
  - Bibliothèques Python / Python libraries : Flask, pandas, numpy, pyserial

- **Matériel / Hardware** :
  - Capteur Grid-EYE AMG8833
  - Arduino
  - (Optionnel / Optional) Module GPS

---

## Installation / Setup

### Étapes en français :

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/your-user/infrared-project.git
   cd infrared-project
   ```

2. Installez les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez le port série et le baud rate dans `server.py` :
   ```python
   SERIAL_PORT = "COM3"
   BAUD_RATE = 9600
   ```

4. Téléversez `Infrared_Arduino_code.ino` sur votre Arduino.

5. Lancez le serveur Flask :
   ```bash
   python server.py
   ```

6. Ouvrez l'interface web à l'adresse : `http://localhost:5000`.

---

### Steps in English:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-user/infrared-project.git
   cd infrared-project
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update the serial port and baud rate in `server.py`:
   ```python
   SERIAL_PORT = "COM3"
   BAUD_RATE = 9600
   ```

4. Upload `Infrared_Arduino_code.ino` to your Arduino.

5. Start the Flask server:
   ```bash
   python server.py
   ```

6. Open the web interface at: `http://localhost:5000`.

---

## Licence

Ce projet est sous licence MIT. Veuillez consulter le fichier `LICENSE` pour plus de détails.

This project is licensed under the MIT License. See the `LICENSE` file for details.
``` 

Cela couvre les deux langues tout en restant structuré et facile à lire.
