# Blacklist and VIP- and User-Management Script

This Python script automates the process of managing a blacklist and VIP list for a game server. It reads player data from text files, adds them to the blacklist or VIP list via API requests, and flags them with specific tags. The script is customizable via environment variables defined in a `.env` file.

## Features

- **Create and manage blacklists**: Automatically create and retrieve blacklists from the API, and add players to the blacklist based on a text file.
- **Manage VIP status**: Add VIP status to players based on active and passive seeder files.
- **Flag players**: Assign custom flags (e.g., seeding, grinning) to players from the VIP and non-VIP files.
- **Logging**: Detailed logs of each action, stored in a log file.
- **Multi-format support**: The script can process both bulk and CRcon file formats for player data.

## Prerequisites

- Python 3.x
- `requests` library: Install with `pip install requests`
- `python-dotenv` library: Install with `pip install python-dotenv`
- `threading` is part of the standard Python library.

## Environment Variables

Create a `.env` file in the root directory to configure the script. The following environment variables are required:

- `LOGFILE`: Path to the log file where logs will be stored.
- `BLACKLIST_FILE_PATH`: Path to the text file containing players to be blacklisted.
- `VIP_PLAYERS_FILE_PATH`: Path to the text file containing players to be added as VIPs.
- `NON_VIP_PLAYERS_FILE_PATH`: Path to the text file containing players to be added as non-VIPs.
- `BLACKLIST_NAME`: Name of the blacklist to create or retrieve.
- `REASON`: Reason for blacklisting a player.
- `ADMIN_NAME`: Name of the admin performing the blacklist operation.
- `API_URL`: Base URL of the API.
- `API_KEY`: Authorization key to access the API.

## Text File Format

The script supports two formats for player data files:

### Bulk Format

Each line contains a Steam ID and player name, separated by a comma:
`steam_id,player_name`

### CRcon Format

Each line contains a Steam ID, player name, and expiration date, separated by spaces:
`steam_id player_name expiration_date`

## Usage

1. Configure the `.env` file with the necessary environment variables.
2. Prepare the blacklist, VIP, and non-VIP files in the correct format.
3. Run the script:

```bash
python player_importer.py
```

The script will:

- Create a blacklist using the specified `BLACKLIST_NAME`.
- Add players from the blacklist file to the newly created blacklist.
- Add infinite VIP status to players from the VIP file.
- Add expired VIP status to players from the non-VIP file.
- Flag players from the VIP file with the flags 😀🌱.
- Flag players from the non-VIP file with the flag 🌱.

```env
LOGFILE=logfile.log
BLACKLIST_FILE_PATH=./data/blacklist.txt
VIP_PLAYERS_FILE_PATH=./data/vip_players.txt
NON_VIP_PLAYERS_FILE_PATH=./data/non_vip_players.txt
BLACKLIST_NAME=my_blacklist
REASON=Violation of server rules
ADMIN_NAME=admin123
API_URL=https://api.example.com
API_KEY=your_api_key_here
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
