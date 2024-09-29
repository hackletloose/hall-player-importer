import requests
import os
import logging
from dotenv import load_dotenv

# Logging konfigurieren
logging.basicConfig(
    filename = os.getenv("LOGFILE"),  # Logdatei
    level=logging.INFO,  # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Format der Logs
)

# Umgebungsvariablen aus der .env-Datei laden
load_dotenv()

# Variablen aus der .env-Datei lesen
blacklist_file_path = os.getenv("BLACKLIST_FILE_PATH")
active_seeder_file_path = os.getenv("ACTIVE_SEEDER_FILE_PATH")
passive_seeder_file_path = os.getenv("PASSIVE_SEEDER_FILE_PATH")
blacklist_name = os.getenv("BLACKLIST_NAME")
reason = os.getenv("REASON")
admin_name = os.getenv("ADMIN_NAME")
# URLs basierend auf der API_URL aus der .env
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")
create_blacklist_url = f"{api_url}/api/create_blacklist"
get_blacklists_url = f"{api_url}/api/get_blacklists"
add_blacklist_record_url = f"{api_url}/api/add_blacklist_record"
add_vip_url = f"{api_url}/api/add_vip"
flag_player_url = f"{api_url}/api/flag_player"
# Header mit API-Key
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Logge den Start des Skripts
logging.info("Blacklist-Import startet")
logging.debug(f"Pfad zur Blacklist-Datei: {blacklist_file_path}")
logging.debug(f"Pfad zur Active Seeder-Datei: {active_seeder_file_path}")


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
    with open(blacklist_file_path, 'r') as file:
        for line in file:
            steam_id, name = line.strip().split(',')
            spieler.append({"steam_id": steam_id, "name": name})
    logging.info(f"{len(spieler)} Spieler erfolgreich aus der Datei {blacklist_file_path} eingelesen.")
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

# Spieler aus der VIP-Datei einlesen
try:
    vip_spieler = []
    with open(active_seeder_file_path, 'r') as file:
        for line in file:
            steam_id, description = line.strip().split(',')
            vip_spieler.append({"steam_id": steam_id, "description": description})
    logging.info(f"{len(vip_spieler)} VIP-Spieler erfolgreich aus der Datei {active_seeder_file_path} eingelesen.")
except Exception as e:
    logging.error(f"Fehler beim Einlesen der VIP-Spielerdatei: {e}")
    exit()

# VIP-Status für Spieler hinzufügen
for player in vip_spieler:
    vip_data = {
        "player_id": player["steam_id"],
        "description": player["description"],
        "expiration": None  # Keine Ablaufzeit
    }

    try:
        logging.debug(f"Füge VIP-Status für Spieler {player['steam_id']} mit Daten {vip_data} hinzu")
        response = requests.post(add_vip_url, headers=headers, json=vip_data)
        
        if response.status_code == 200:
            logging.info(f"VIP-Status für Spieler {player['steam_id']} erfolgreich hinzugefügt.")
        else:
            logging.error(f"Fehler beim Hinzufügen des VIP-Status für {player['steam_id']}: {response.status_code}")
            logging.error(f"Antwort: {response.text}")
    except Exception as e:
        logging.critical(f"Fehler bei der Anfrage zum Hinzufügen des VIP-Status für {player['steam_id']}: {e}")
        
# Funktion, um einen Spieler zu flaggen
def flag_player(player_id, player_name, flag, comment=None):
    flag_data = {
        "player_id": player_id,
        "flag": flag,
        "player_name": player_name,
        "comment": comment
    }

    try:
        logging.debug(f"Füge Flag {flag} für Spieler {player_name} (ID: {player_id}) hinzu mit Daten {flag_data}")
        response = requests.post(flag_player_url, headers=headers, json=flag_data)
        
        if response.status_code == 200:
            logging.info(f"Flag {flag} erfolgreich für Spieler {player_name} (ID: {player_id}) hinzugefügt.")
        else:
            logging.error(f"Fehler beim Hinzufügen von Flag {flag} für {player_name}: {response.status_code}")
            logging.error(f"Antwort: {response.text}")
    except Exception as e:
        logging.critical(f"Fehler bei der Anfrage zum Hinzufügen von Flag {flag} für {player_name}: {e}")

# Spieler aus der active_seeder_file einlesen und Flaggen hinzufügen
try:
    with open(active_seeder_file_path, 'r') as file:
        for line in file:
            steam_id, name = line.strip().split(',')
            # Erstes Flag :seeding:
            flag_player(steam_id, name, "🌱")
            # Zweites Flag :grinning:
            flag_player(steam_id, name, "😀")
except Exception as e:
    logging.error(f"Fehler beim Einlesen der Spielerdatei oder Hinzufügen der Flags: {e}")
    exit()

# Spieler aus der PASSIVE_SEEDERS_FILE_PATH einlesen
try:
    passive_seeder_spieler = []
    with open(passive_seeder_file_path, 'r') as file:
        for line in file:
            steam_id, description = line.strip().split(',')
            passive_seeder_spieler.append({"steam_id": steam_id, "description": description})
    logging.info(f"{len(passive_seeder_spieler)} passive Seeder erfolgreich aus der Datei {os.getenv('PASSIVE_SEEDERS_FILE_PATH')} eingelesen.")
except Exception as e:
    logging.error(f"Fehler beim Einlesen der passiven Seeder-Datei: {e}")
    exit()

# VIP-Status für passive Seeder hinzufügen
for player in passive_seeder_spieler:
    vip_data = {
        "player_id": player["steam_id"],
        "description": player["description"],
        "expiration": "2024-01-01T13:00:00+00:00"  # Keine Ablaufzeit
    }

    try:
        logging.debug(f"Füge VIP-Status für passiven Seeder {player['steam_id']} mit Daten {vip_data} hinzu")
        response = requests.post(add_vip_url, headers=headers, json=vip_data)
        
        if response.status_code == 200:
            logging.info(f"VIP-Status für passiven Seeder {player['steam_id']} erfolgreich hinzugefügt.")
        else:
            logging.error(f"Fehler beim Hinzufügen des VIP-Status für passiven Seeder {player['steam_id']}: {response.status_code}")
            logging.error(f"Antwort: {response.text}")
    except Exception as e:
        logging.critical(f"Fehler bei der Anfrage zum Hinzufügen des VIP-Status für passiven Seeder {player['steam_id']}: {e}")

# Flaggen für passive Seeder hinzufügen
try:
    for player in passive_seeder_spieler:
        # Flag für passiven Seeder :passive:
        flag_player(player['steam_id'], player['description'], "🌱")
except Exception as e:
    logging.error(f"Fehler beim Einlesen der passiven Seeder-Datei oder Hinzufügen der Flags: {e}")
    exit()
