import requests
import os
import logging
from dotenv import load_dotenv
import threading
import signal
import sys

logging.basicConfig(
    filename=os.getenv("LOGFILE"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S"
)

load_dotenv()
blacklist_file_path = os.getenv("BLACKLIST_FILE_PATH")
vip_players_file_path = os.getenv("VIP_PLAYERS_FILE_PATH")
non_vip_players_file_path = os.getenv("NON_VIP_PLAYERS_FILE_PATH")
blacklist_name = os.getenv("BLACKLIST_NAME")
reason = os.getenv("REASON")
admin_name = os.getenv("ADMIN_NAME")
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")
vip_first_flag=os.getenv("VIP_FIRST_FLAG")
vip_second_flag=os.getenv("VIP_SECOND_FLAG")
non_vip_flag=os.getenv("NON_VIP_FLAG")
create_blacklist_url = f"{api_url}/api/create_blacklist"
get_blacklists_url = f"{api_url}/api/get_blacklists"
add_blacklist_record_url = f"{api_url}/api/add_blacklist_record"
add_vip_url = f"{api_url}/api/add_vip"
flag_player_url = f"{api_url}/api/flag_player"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def signal_handler(sig, frame):
    logging.info("Program exited by user by pressing CTRL+C")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def add_players_to_blacklist(players, blacklist_id):
    for player in players:
        blacklist_record_data = {
            "player_id": player["steam_id"],
            "blacklist_id": blacklist_id,
            "reason": reason,
            "expires_at": None,
            "admin_name": admin_name
        }
        try:
            response = requests.post(add_blacklist_record_url, headers=headers, json=blacklist_record_data, timeout=10)
            if response.status_code == 200:
                logging.info(f"✅ | SUCCESS  | 🚷 Add to Blacklist | ID: {player['steam_id']} | Name: {player['name']}")
            else:
                logging.error(f"⛔ | ERROR    | 🚷 Add to Blacklist | ID: {player['steam_id']} | Name: {player['name']} | Response: {response.status_code}")
                logging.error(f"Response: {response.text}")
        except Exception as e:
            logging.critical(f"⛔ | CRITICAL | 🚷 Add to Blacklist | ID: {player['steam_id']} | Name: {player['name']} | {e}")

def add_vip_status(players, url):
    for player in players:
        vip_data = {
            "player_id": player["steam_id"],
            "description": player.get("description", ""),
            "expiration": None
        }
        try:
            logging.debug(f"Adding VIP status for player {player['steam_id']} with data {vip_data}")
            response = requests.post(url, headers=headers, json=vip_data, timeout=10)
            if response.status_code == 200:
                logging.info(f"✅ | SUCCESS  | 💎 Add VIP          | ID: {player['steam_id']} | Name: {player['name']}")
            else:
                logging.error(f"⛔ | ERROR    | 💎 Add VIP          | ID: {player['steam_id']} | Name: {player['name']} |  Response: {response.status_code}")
                logging.error(f"Response: {response.text}")
        except Exception as e:
            logging.critical(f"⛔ | CRITICAL | 💎 Add VIP          | ID: {player['steam_id']} | Name: {player['name']} | {e}")

def flag_players(players, first_flag, second_flag=None):
    for player in players:
        flag_player(player['steam_id'], player['name'], first_flag)
        if second_flag:
            flag_player(player['steam_id'], player['name'], second_flag)

def flag_player(player_id, player_name, flag, comment=None):
    flag_data = {
        "player_id": player_id,
        "flag": flag,
        "player_name": player_name,
        "comment": comment
    }
    try:
        logging.debug(f"Adding flag {flag} for player {player_name} (ID: {player_id}) with data {flag_data}")
        response = requests.post(flag_player_url, headers=headers, json=flag_data, timeout=10)
        if response.status_code == 200:
            logging.info(f"✅ | SUCCESS  | 🚩 Add Flag {flag}      | ID: {player_id} | Name: {player_name} ")
        else:
            logging.error(f"⛔ | ERROR    | 🚩 Add Flag {flag}      | ID: {player_id} | Name: {player_name} | Response: {response.status_code}")
            logging.error(f"Response: {response.text}")
    except Exception as e:
        logging.critical(f"⛔ | CRITICAL | 🚩 Add Flag {flag}      | ID: {player_id} | Name: {player_name} | {e}")

def read_players_from_file(file_path):
    try:
        players = []
        with open(file_path, 'r') as file:
            for line in file:
                if ',' in line:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        steam_id, name = parts
                        expiration = None
                    else:
                        logging.error(f"⛔ | ERROR    | 📂 Load File        | Wrong file format in {file_path} | Line: {line}")
                        continue
                else:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        steam_id = parts[0]
                        expiration = parts[-1]
                        name = ' '.join(parts[1:-1])
                    else:
                        logging.error(f"⛔ | ERROR    | 📂 Load File        | Wrong file format in {file_path} | Line: {line}")
                        continue
                players.append({
                    "steam_id": steam_id,
                    "name": name,
                    "expiration": expiration
                })
        if len(players) > 0 and any(player["expiration"] for player in players):
            logging.info(f"✅ | SUCCESS  | 📂 Load CRcon File  | {len(players)} Players from {file_path}.")
        else:
            logging.info(f"✅ | SUCCESS  | 📂 Load Bulk File   | {len(players)} Players from {file_path}.")
        
        return players
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 📂 Load File        | {file_path} | {e}")
        raise SystemExit

def create_or_get_blacklist():
    blacklist_data = {
        "name": blacklist_name,
        "servers": None
    }
    try:
        logging.debug(f"Creating blacklist with data: {blacklist_data}")
        response = requests.post(create_blacklist_url, headers=headers, json=blacklist_data, timeout=10)
        if response.status_code == 200:
             logging.info("✅ | SUCCESS  | 📓 Create Blacklist")
        else:
            logging.error(f"⛔ | ERROR    | 📓 Create Blacklist | Response: {response.status_code}")
            logging.error(f"Response: {response.text}")
            raise SystemExit
    except Exception as e:
        logging.critical(f"⛔ | CRITICAL | 📓 Create Blacklist | {e}")
        raise SystemExit
    try:
        response = requests.get(get_blacklists_url, headers=headers, timeout=10)
        if response.status_code == 200:
            blacklists = response.json().get('result', [])
            logging.info(f"✅ | SUCCESS  | 🔎 Find Blacklist   | {len(blacklists)} Blacklists found.")
            for bl in blacklists:
                if bl.get('name') == blacklist_name:
                    logging.info(f"✅ | SUCCESS  | 🔎 Find Blacklist   | ID = {bl.get('id')}, Name = {blacklist_name}")
                    return bl.get('id')

            logging.error(f"⛔ | ERROR    | 🔎 Find Blacklist   | No blacklist found with name {blacklist_name}")
            raise SystemExit
        else:
            logging.error(f"⛔ | ERROR    | 🔎 Find Blacklist   | Response: {response.status_code}")
            logging.error(f"Response: {response.text}")
            raise SystemExit
    except Exception as e:
        logging.critical(f"⛔ | CRITICAL | 🔎 Find Blacklist   | {e}")
        raise SystemExit

def main():
    try:
        blacklist_id = create_or_get_blacklist()
        players = read_players_from_file(blacklist_file_path)
        vip_players = read_players_from_file(vip_players_file_path)
        non_vip_players = read_players_from_file(non_vip_players_file_path)
        threads = []
        
        thread_add_players_to_blacklist = threading.Thread(target=add_players_to_blacklist, args=(players, blacklist_id), daemon=True)
        threads.append(thread_add_players_to_blacklist)
        thread_add_vip_players = threading.Thread(target=add_vip_status, args=(vip_players, add_vip_url), daemon=True)
        threads.append(thread_add_vip_players)
        thread_add_non_vip_players = threading.Thread(target=add_vip_status, args=(non_vip_players, add_vip_url), daemon=True)
        threads.append(thread_add_non_vip_players)
        thread_add_vip_flags = threading.Thread(target=flag_players, args=(vip_players, vip_first_flag, vip_second_flag), daemon=True)
        threads.append(thread_add_vip_flags)
        thread_add_non_vip_flags = threading.Thread(target=flag_players, args=(non_vip_players, non_vip_flag), daemon=True)
        threads.append(thread_add_non_vip_flags)

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        logging.info("Program exited by user by pressing CTRL+C")
        sys.exit(0)

if __name__ == "__main__":
    main()
