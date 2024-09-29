import requests
import os
import logging
from dotenv import load_dotenv

# Logging konfigurieren
logging.basicConfig(
    filename="blacklist_importer.log",  # Logdatei
    level=logging.DEBUG,  # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Format der Logs
)

# Umgebungsvariablen aus der .env-Datei laden
load_dotenv()

# Variablen aus der .env-Datei lesen
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")
blacklist_name = os.getenv("BLACKLIST_NAME")
reason = os.getenv("REASON")
admin_name = os.getenv("ADMIN_NAME")
player_file_path = os.getenv("PLAYER_FILE_PATH")

# URLs basierend auf der API_URL aus der .env
create_blacklist_url = f"{api_url}/api/create_blacklist"
get_blacklists_url = f"{api_url}/api/get_blacklists"
add_blacklist_record_url = f"{api_url}/api/add_blacklist_record"

# Header mit API-Key
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Logge den Start des Skripts
logging.info("Blacklist-Import startet")

# Daten für das Erstellen der Blacklist
blacklist_data = {
    "name": blacklist_name,
    "servers": None  # Setze 'servers' auf 'null'
}

# Versuche, die Blacklist zu erstellen
try:
    logging.debug(f"Erstelle Blacklist mit Daten: {blacklist_data}")
    response = requests.post(create_blacklist_url, headers=headers, json=blacklist_data)
    
    if response.status_code == 200:
        logging.info("Blacklist erfolgreich erstellt.")
    else:
        logging.error(f"Fehler beim Erstellen der Blacklist: {response.status_code}")
        logging.error(f"Antwort: {response.text}")
        exit()
except Exception as e:
    logging.critical(f"Fehler bei der Anfrage zum Erstellen der Blacklist: {e}")
    exit()

# Abrufen aller Blacklists über den get_blacklists-Endpunkt und die passende Blacklist-ID ermitteln
try:
    response = requests.get(get_blacklists_url, headers=headers)
    
    if response.status_code == 200:
        blacklists = response.json().get('result', [])
        logging.info(f"{len(blacklists)} Blacklists abgerufen.")
        
        # Suche nach der Blacklist mit dem Namen, der in der .env angegeben wurde
        blacklist_id = None
        for bl in blacklists:
            if bl.get('name') == blacklist_name:
                blacklist_id = bl.get('id')
                logging.info(f"Passende Blacklist gefunden: ID = {blacklist_id}, Name = {blacklist_name}")
                break

        if not blacklist_id:
            logging.error(f"Keine Blacklist mit dem Namen {blacklist_name} gefunden.")
            exit()
    else:
        logging.error(f"Fehler beim Abrufen der Blacklists: {response.status_code}")
        logging.error(f"Antwort: {response.text}")
        exit()
except Exception as e:
    logging.critical(f"Fehler bei der Anfrage zum Abrufen der Blacklists: {e}")
    exit()

# Spieler aus der Textdatei einlesen, der Pfad kommt aus der .env-Datei
try:
    spieler = []
    with open(player_file_path, 'r') as file:
        for line in file:
            steam_id, name = line.strip().split(',')
            spieler.append({"steam_id": steam_id, "name": name})
    logging.info(f"{len(spieler)} Spieler erfolgreich aus der Datei {player_file_path} eingelesen.")
except Exception as e:
    logging.error(f"Fehler beim Einlesen der Spielerdatei: {e}")
    exit()

# Spieler zur Blacklist hinzufügen
for player in spieler:
    blacklist_record_data = {
        "player_id": player["steam_id"],
        "blacklist_id": blacklist_id,  # Verwende die abgerufene Blacklist-ID
        "reason": reason,
        "expires_at": None,  # Keine Ablaufzeit
        "admin_name": admin_name
    }

    try:
        logging.debug(f"Füge Spieler {player['name']} mit Daten {blacklist_record_data} zur Blacklist hinzu")
        response = requests.post(add_blacklist_record_url, headers=headers, json=blacklist_record_data)
        
        if response.status_code == 200:
            logging.info(f"Spieler {player['name']} erfolgreich zur Blacklist hinzugefügt.")
        else:
            logging.error(f"Fehler beim Hinzufügen von {player['name']}: {response.status_code}")
            logging.error(f"Antwort: {response.text}")
    except Exception as e:
        logging.critical(f"Fehler bei der Anfrage zum Hinzufügen von {player['name']}: {e}")
