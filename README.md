# Blacklist and VIP Management Script

This Python script automates the process of managing a blacklist and VIP list for a game server. It reads player data from text files, adds them to the blacklist or VIP list via API requests, and flags them with specific tags. The script is customizable via environment variables defined in a `.env` file.

## Features

- **Create and manage blacklists**: Automatically create and retrieve blacklists from the API, and add players to the blacklist based on a text file.
- **Manage VIP status**: Add VIP status to players based on active and passive seeder files.
- **Flag players**: Assign custom flags (e.g., seeding, grinning) to players from the active seeder file.
- **Logging**: Detailed logs of each action, stored in a log file.

## Prerequisites

- Python 3.x
- `requests` library: Install with `pip install requests`
- `python-dotenv` library: Install with `pip install python-dotenv`
- API access with an API key and valid URLs.

## Environment Variables

Create a `.env` file in the root directory to configure the script. The following environment variables are required:

- `LOGFILE`: Path to the log file where logs will be stored.
- `BLACKLIST_FILE_PATH`: Path to the text file containing players to be blacklisted.
- `ACTIVE_SEEDER_FILE_PATH`: Path to the text file containing players to be added as active seeders (VIPs).
- `PASSIVE_SEEDER_FILE_PATH`: Path to the text file containing passive seeders (VIPs).
- `BLACKLIST_NAME`: Name of the blacklist to create or retrieve.
- `REASON`: Reason for blacklisting a player.
- `ADMIN_NAME`: Name of the admin performing the blacklist operation.
- `API_URL`: Base URL of the API.
- `API_KEY`: Authorization key to access the API.

## Text File Format

Both the blacklist and seeder text files should have the following format:
`steam_id,player_name`

## Usage

1. Configure the `.env` file with the necessary environment variables.
2. Prepare the blacklist and seeder files in the correct format.
3. Run the script:

```bash
python script.py
