
# Hall Player Importer

The **Hall Player Importer** bot is designed to manage player lists (banned players, VIPs, and non-VIPs) using an importer script. This README will guide you through the setup and usage of the bot.

## Project Structure

- **.env**: Stores environment variables and sensitive configuration settings.
- **ban_players.txt**: A list of banned players.
- **non_vip_players.txt**: A list of non-VIP players.
- **player-importer.py**: The main script that runs the player import functionalities.
- **vip_players.txt**: A list of VIP players.

## Requirements

To run this bot, ensure you have the following installed:
- Python 3.x
- Required Python libraries (can be installed via `pip`)

## Installation

1. Clone the repository or download the project files.
2. Install the necessary dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your environment variables by configuring the `.env` file.

## Environment Variables

In the `.env` file, configure the following:

- `API_URL`: The endpoint for the API to manage players.
- `API_KEY`: Your API key for authentication.
- `ADMIN_NAME`: The administrator name to log actions.
- `REASON`: The reason to be used when banning or flagging players.

Example `.env`:

```bash
API_URL="http://your-api-url.com"
API_KEY="your-api-key"
ADMIN_NAME="your-admin-name"
REASON="violated terms"
```

## Usage

To run the bot, execute the `player-importer.py` script:

```bash
python player-importer.py
```

### Features:

1. **Ban Players**: The bot can ban players listed in `ban_players.txt`.
2. **VIP Players**: Assign VIP status to players listed in `vip_players.txt`.
3. **Non-VIP Players**: Manage non-VIP players listed in `non_vip_players.txt`.

## Contributing

Feel free to fork the repository and create a pull request if you would like to contribute to the development of this project.

## License

This project is licensed under the MIT License.
