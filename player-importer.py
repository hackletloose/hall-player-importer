import requests
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    filename = os.getenv("LOGFILE"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
load_dotenv()
blacklist_file_path = os.getenv("BLACKLIST_FILE_PATH")
vip_players_file_path = os.getenv("VIP_PLAYERS_FILE_PATH")
vip_players_flag_1 = os.getenv("VIP_PLAYERS_FLAG_1")
vip_players_flag_2 = os.getenv("VIP_PLAYERS_FLAG_2")
non_vip_players_flag = os.getenv("NON_VIP_PLAYERS_FLAG")
non_vip_players_file_path = os.getenv("NON_VIP_PLAYERS_FILE_PATH")
blacklist_name = os.getenv("BLACKLIST_NAME")
reason = os.getenv("REASON")
admin_name = os.getenv("ADMIN_NAME")
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")
create_blacklist_url = f"{api_url}/api/create_blacklist"
get_blacklists_url = f"{api_url}/api/get_blacklists"
add_blacklist_record_url = f"{api_url}/api/add_blacklist_record"
add_vip_url = f"{api_url}/api/add_vip"
flag_player_url = f"{api_url}/api/flag_player"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
logging.info("Blacklist-Import startet")
logging.debug(f"Pfad zur Blacklist-Datei: {blacklist_file_path}")
logging.debug(f"Pfad zur Active Seeder-Datei: {vip_players_file_path}")
blacklist_data = {
    "name": blacklist_name,
    "servers": None
}
try:
    logging.debug(f"Create Blacklist: {blacklist_data}")
    response = requests.post(create_blacklist_url, headers=headers, json=blacklist_data)
    
    if response.status_code == 200:
        logging.info("Blacklist created successfully.")
    else:
        logging.error(f"Error on creating blacklist: {response.status_code}")
        logging.error(f"Response: {response.text}")
        exit()
except Exception as e:
    logging.critical(f"Error on query to create Blacklist: {e}")
    exit()
try:
    response = requests.get(get_blacklists_url, headers=headers)
    
    if response.status_code == 200:
        blacklists = response.json().get('result', [])
        logging.info(f"{len(blacklists)} Blacklists found.")
        blacklist_id = None
        for bl in blacklists:
            if bl.get('name') == blacklist_name:
                blacklist_id = bl.get('id')
                logging.info(f"Blacklist matched: ID = {blacklist_id}, Name = {blacklist_name}")
                break

        if not blacklist_id:
            logging.error(f"No blacklist matched {blacklist_name}.")
            exit()
    else:
        logging.error(f"Error on fetching the Blacklists: {response.status_code}")
        logging.error(f"Antwort: {response.text}")
        exit()
except Exception as e:
    logging.critical(f"Error on fetching query for Blacklists: {e}")
    exit()
try:
    players = []
    with open(blacklist_file_path, 'r') as file:
        for line in file:
            steam_id, name = line.strip().split(',')
            players.append({"steam_id": steam_id, "name": name})
    logging.info(f"{len(players)} Getting players from {blacklist_file_path} successfully.")
except Exception as e:
    logging.error(f"Error on fetching blacklist data: {e}")
    exit()
for player in players:
    blacklist_record_data = {
        "player_id": player["steam_id"],
        "blacklist_id": blacklist_id,
        "reason": reason,
        "expires_at": None,
        "admin_name": admin_name
    }
    try:
        logging.debug(f"Added Player {player['name']} with data {blacklist_record_data} to blacklist")
        response = requests.post(add_blacklist_record_url, headers=headers, json=blacklist_record_data)
        
        if response.status_code == 200:
            logging.info(f"Player {player['name']} successfully added.")
        else:
            logging.error(f"Error on adding Player {player['name']}: {response.status_code}")
            logging.error(f"Response: {response.text}")
    except Exception as e:
        logging.critical(f"Error on getting query for adding the Player {player['name']}: {e}")
try:
    vip_player = []
    with open(vip_players_file_path, 'r') as file:
        for line in file:
            steam_id, description = line.strip().split(',')
            vip_player.append({"steam_id": steam_id, "description": description})
    logging.info(f"{len(vip_player)} VIP-Player successfully loaded from {vip_players_file_path}")
except Exception as e:
    logging.error(f"Error on getting VIP-Players: {e}")
    exit()
for player in vip_player:
    vip_data = {
        "player_id": player["steam_id"],
        "description": player["description"],
        "expiration": None
    }
    try:
        logging.debug(f"Adding VIP for Player {player['steam_id']} with {vip_data}")
        response = requests.post(add_vip_url, headers=headers, json=vip_data)
        
        if response.status_code == 200:
            logging.info(f"Successfully added VIP-state to player {player['steam_id']}.")
        else:
            logging.error(f"Error on adding VIP state to Player {player['steam_id']}: {response.status_code}")
            logging.error(f"Response: {response.text}")
    except Exception as e:
        logging.critical(f"Error on query for VIP State on Player {player['steam_id']}: {e}")

def flag_player(player_id, player_name, flag, comment=None):
    flag_data = {
        "player_id": player_id,
        "flag": flag,
        "player_name": player_name,
        "comment": comment
    }
    try:
        logging.debug(f"Adding Flag {flag} to Player {player_name} (ID: {player_id}) with {flag_data}")
        response = requests.post(flag_player_url, headers=headers, json=flag_data)
        
        if response.status_code == 200:
            logging.info(f"Flag {flag} added successfully to player {player_name} (ID: {player_id})")
        else:
            logging.error(f"Error on Adding the Flag {flag} to Player {player_name}: {response.status_code}")
            logging.error(f"Response: {response.text}")
    except Exception as e:
        logging.critical(f"Error on Query to adding the Flag {flag} to Player {player_name}: {e}")
try:
    with open(vip_players_file_path, 'r') as file:
        for line in file:
            steam_id, name = line.strip().split(',')
            flag_player(steam_id, name, {vip_players_flag_1})
            flag_player(steam_id, name, {vip_players_flag_2})
except Exception as e:
    logging.error(f"Error on Reading the query for Flags: {e}")
    exit()
try:
    non_vip_players = []
    with open(non_vip_players_file_path, 'r') as file:
        for line in file:
            steam_id, description = line.strip().split(',')
            non_vip_players.append({"steam_id": steam_id, "description": description})
    logging.info(f"{len(non_vip_players)} Non VIP Players loaded from {os.getenv('PASSIVE_SEEDERS_FILE_PATH')}.")
except Exception as e:
    logging.error(f"Error on Reading the Non VIP Player List: {e}")
    exit()
for player in non_vip_players:
    vip_data = {
        "player_id": player["steam_id"],
        "description": player["description"],
        "expiration": "2024-01-01T13:00:00+00:00"
    }
    try:
        logging.debug(f"Adding Expired VIP to Player {player['steam_id']} with data {vip_data}")
        response = requests.post(add_vip_url, headers=headers, json=vip_data)
        
        if response.status_code == 200:
            logging.info(f"Expired VIP to Player {player['steam_id']} added successfully.")
        else:
            logging.error(f"Error on query to add expired vip to player {player['steam_id']}: {response.status_code}")
            logging.error(f"Response: {response.text}")
    except Exception as e:
        logging.critical(f"Error on query to add expired vip to player {player['steam_id']}: {e}")
try:
    for player in non_vip_players:
        flag_player(player['steam_id'], player['description'], {non_vip_players_flag})
except Exception as e:
    logging.error(f"Error on reading data from file to the flags of a Non VIP Player: {e}")
    exit()
