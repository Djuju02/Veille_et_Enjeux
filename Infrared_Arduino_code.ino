#include <Wire.h>
#include <Adafruit_AMG88xx.h>

// Créez une instance de la bibliothèque AMG88xx
Adafruit_AMG88xx amg;

float pixels[64]; // Tableau pour stocker les données des pixels

// Variables GPS simulées (remplacez par un module GPS si disponible)
float gps_lat = 34.05;
float gps_lon = -118.25;

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; } // Attendre que la connexion série soit établie
  Serial.println(F("Serial initialized"));

  // Initialisation du capteur AMG88xx
  Serial.println(F("Initializing AMG88xx..."));
  if (!amg.begin()) {
    Serial.println(F("Failed to initialize AMG88xx!"));
    while (1); // Arrêter l'exécution si l'initialisation échoue
  }
  Serial.println(F("AMG88xx initialized"));
}

void loop() {
  Serial.println(F("Reading AMG88xx data..."));

  // Lire les données du Grid-EYE
  amg.readPixels(pixels); // Cette fonction ne retourne rien

  Serial.println(F("AMG88xx data read successfully"));
  sendFrame();

  delay(2000); // Attendre 2 secondes avant la prochaine lecture
}

void sendFrame() {
  Serial.println(F("BEGIN_FRAME"));
  Serial.print(F("GPS_LAT="));
  Serial.println(gps_lat, 6);
  Serial.print(F("GPS_LON="));
  Serial.println(gps_lon, 6);

  for (int i = 0; i < 64; i++) {
    Serial.print(F("PIXEL_"));
    Serial.print(i);
    Serial.print(F("="));
    Serial.println(pixels[i], 2);
  }

  Serial.println(F("END_FRAME"));
}
