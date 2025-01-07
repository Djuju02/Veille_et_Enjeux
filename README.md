**Projet Capteur Infrarouge avec Arduino et Flask**

**Description**  
Ce projet utilise un capteur infrarouge (Grid-EYE AMG8833) connecté à un Arduino pour collecter des données thermiques et des coordonnées GPS. Les données sont sauvegardées dans un fichier CSV et accessibles via des APIs Flask. Une interface web interactive permet de visualiser les données en temps réel, d'explorer l'historique et de cartographier les points GPS.

**Fonctionnalités**  
- Collecte de données infrarouges (64 pixels) et coordonnées GPS (réelles ou simulées).
- APIs pour accéder aux données en temps réel et à l'historique :
  - `/api/live` : Dernière mesure.
  - `/api/history` : Historique filtré.
  - `/api/frame/<frame_id>` : Détails d'une mesure spécifique.
- Interface web interactive pour visualiser les données en temps réel, explorer l'historique et afficher les points sur une carte.

**Installation**  
Clonez le dépôt :  
```
git clone https://github.com/your-user/infrared-project.git
cd infrared-project
```

Installez les dépendances Python :  
```
pip install -r requirements.txt
```

Configurez le port série et le baud rate dans `server.py` :  
```python
SERIAL_PORT = "COM3"
BAUD_RATE = 9600
```

Téléversez `Infrared_Arduino_code.ino` sur votre Arduino.

Lancez le serveur Flask :  
```
python server.py
```

Ouvrez l'interface web à l'adresse : [http://localhost:5000](http://localhost:5000).

---

**Infrared Sensor Project with Arduino and Flask**

**Description**  
This project uses an infrared sensor (Grid-EYE AMG8833) connected to an Arduino to collect thermal data and GPS coordinates. The data is stored in a CSV file and made accessible via Flask APIs. An interactive web interface allows real-time data visualization, historical data exploration, and GPS point mapping.

**Features**  
- Infrared data collection (64-pixel array) and GPS coordinates (real or simulated).
- APIs to access real-time and historical data:
  - `/api/live`: Latest data.
  - `/api/history`: Filtered historical data.
  - `/api/frame/<frame_id>`: Specific frame details.
- Interactive web dashboard for real-time visualization, historical exploration, and GPS mapping.

**Setup**  
Clone the repository:  
```
git clone https://github.com/your-user/infrared-project.git
cd infrared-project
```

Install Python dependencies:  
```
pip install -r requirements.txt
```

Update the serial port and baud rate in `server.py`:  
```python
SERIAL_PORT = "COM3"
BAUD_RATE = 9600
```

Upload `Infrared_Arduino_code.ino` to your Arduino.

Start the Flask server:  
```
python server.py
```

Open the web interface at: [http://localhost:5000](http://localhost:5000).

---

**Licence**  
Ce projet est sous licence MIT. Veuillez consulter le fichier `LICENSE` pour plus de détails.  
This project is licensed under the MIT License. See the `LICENSE` file for details.  
