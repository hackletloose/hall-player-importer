
# Blacklist and VIP- and User-Management Bot

This Discord bot automates the management of a blacklist and VIP list for a game server. It reads player data from text files, adds them to the blacklist or VIP list via API requests, and flags them with specific tags. The bot is configurable via environment variables defined in a `.env` file and is designed to operate directly within Discord.

## Features

- **Discord UI Integration**: Modals, buttons, and commands provide a streamlined user interface within Discord.
- **Create and Manage Blacklists**: Automatically create and retrieve blacklists from the API, adding players based on data from text files.
- **VIP Status Management**: Assign VIP status to players based on active and passive seeder files.
- **Player Flagging**: Assign custom flags (e.g., seeding, grinning) to players from the VIP and non-VIP files.
- **Asynchronous API Handling**: Improved performance and responsiveness by using asynchronous API calls.
- **Comprehensive Logging**: Logs all actions, such as imports, blacklist additions, and VIP status updates.

## Prerequisites

- Python 3.8 or later
- Libraries: Install requirements with
  ```bash
  pip install discord.py aiohttp python-dotenv
  ```

## Environment Variables

The bot requires environment variables for configuration, which should be set in a `.env` file.

### Required Variables

| Variable Name            | Description                                                    |
|--------------------------|----------------------------------------------------------------|
| DISCORD_BOT_TOKEN        | Token for Discord Bot authentication                           |
| DISCORD_CHANNEL_ID       | Channel ID where bot posts its messages                        |
| BLACKLIST_NAME           | Name of the blacklist to create or retrieve                    |
| REASON                   | Reason for blacklisting a player                               |
| ADMIN_NAME               | Name of the admin performing blacklist operations              |
| BLACKLIST_FILE_PATH      | Path to the text file containing players to be blacklisted     |
| VIP_PLAYERS_FILE_PATH    | Path to the text file containing players to be added as VIPs   |
| NON_VIP_PLAYERS_FILE_PATH| Path to the text file containing players to be added as non-VIPs |
| VIP_FIRST_FLAG           | First flag for VIP players                                    |
| VIP_SECOND_FLAG          | Second flag for VIP players                                   |
| NON_VIP_FLAG             | Flag for non-VIP players                                      |

## Text File Format

The bot supports two formats for player data files:

### Bulk Format

Each line contains a Steam ID and player name, separated by a comma:
`steam_id,player_name`

### CRcon Format

Each line contains a Steam ID, player name, and expiration date, separated by spaces:
`steam_id player_name expiration_date`

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file based on `.env.dist`.

4. Run the bot:
   ```bash
   python player-importer.py
   ```

## Usage

When the bot is running, it listens to commands and interacts through Discord modals and buttons for streamlined player data management.

- **Import Player Data**: Click the provided button in Discord to open a modal, input your API credentials, and let the bot handle the rest.
- **Automatic Blacklist and VIP Addition**: Upon execution, the bot will create or retrieve a blacklist, add players from the blacklist file, and apply flags as specified.

```env
# Example of .env file
DISCORD_BOT_TOKEN=your_discord_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
BLACKLIST_NAME=my_blacklist
REASON=Violation of server rules
ADMIN_NAME=admin123
BLACKLIST_FILE_PATH=./data/blacklist.txt
VIP_PLAYERS_FILE_PATH=./data/vip_players.txt
NON_VIP_PLAYERS_FILE_PATH=./data/non_vip_players.txt
VIP_FIRST_FLAG=:seed:
VIP_SECOND_FLAG=:grin:
NON_VIP_FLAG=:seed:
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
