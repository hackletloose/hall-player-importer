import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import ui
import os
import aiohttp
import asyncio
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename='import.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S"
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
blacklist_name = os.getenv("BLACKLIST_NAME")
reason = os.getenv("REASON")
admin_name = os.getenv("ADMIN_NAME")
blacklist_file_path = os.getenv("BLACKLIST_FILE_PATH")
vip_players_file_path = os.getenv("VIP_PLAYERS_FILE_PATH")
non_vip_players_file_path = os.getenv("NON_VIP_PLAYERS_FILE_PATH")
vip_first_flag = os.getenv("VIP_FIRST_FLAG")
vip_second_flag = os.getenv("VIP_SECOND_FLAG")
non_vip_flag = os.getenv("NON_VIP_FLAG")

class ImportModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Input your CRCON Data")
        self.add_item(ui.TextInput(
            label="CRCON URL", 
            placeholder="https://rcon.example.com",
            custom_id="api_base_url"
        ))
        self.add_item(ui.TextInput(
            label="API Token", 
            placeholder="paste your Admin API-Token here",
            custom_id="api_token",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        open('import.log', 'w').close()
        headers = {
            "Authorization": f"Bearer {self.children[1].value}"
        }
        api_base_url = self.children[0].value
        await interaction.response.send_message("**Import in progress...** Please relax. You will be informed by direct message with a log file attached!", ephemeral=True)
        try:
            await perform_import(api_base_url, self.children[1].value, interaction)
            with open('import.log', 'rb') as log_file:
                await interaction.user.send("**Import successfull** | Here is the log file for your information:", file=discord.File(log_file, 'import.log'))
        except Exception as e:
            await interaction.followup.send(f"An error occured: {e}", ephemeral=True)

class ImportView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.api_url = None
        self.api_key = None

    @discord.ui.button(label="Import Accounts", style=discord.ButtonStyle.primary, custom_id="import_button")
    async def import_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ImportModal())

    async def wait_for_input(self, interaction):
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
            await msg.delete()
            return msg.content.strip()
        except asyncio.TimeoutError:
            await interaction.followup.send("Timeout on input.", ephemeral=True)
            return None

async def send_progress(interaction, total, completed):
    progress = (completed / total) * 100
    await interaction.followup.send(f"**Progress:** {progress:.2f}% complete", ephemeral=True)

async def perform_import(api_url, api_key, interaction):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    remove_perma_ban_url = f"{api_url}/api/remove_perma_ban"
    remove_temp_ban_url = f"{api_url}/api/remove_temp_ban"
    remove_vip_url = f"{api_url}/api/remove_vip"
    create_blacklist_url = f"{api_url}/api/create_blacklist"
    get_blacklists_url = f"{api_url}/api/get_blacklists"
    add_blacklist_record_url = f"{api_url}/api/add_blacklist_record"
    add_vip_url = f"{api_url}/api/add_vip"
    flag_player_url = f"{api_url}/api/flag_player"
    players = read_players_from_file(blacklist_file_path)
    vip_players = read_players_from_file(vip_players_file_path)
    non_vip_players = read_players_from_file(non_vip_players_file_path)
    all_players = players + vip_players + non_vip_players
    total_players = len(all_players)
    completed_players = 0

    await interaction.response.send_message("**Import in progress...** Please relax. You will be informed by direct message with a log file attached!", ephemeral=True)

    async with aiohttp.ClientSession() as session:
        removal_tasks = []
        for player in all_players:
            player_id = player["steam_id"]
            removal_tasks.extend([
                remove_perma_ban(session, remove_perma_ban_url, headers, {"player_id": player_id}, player_id),
                remove_temp_ban(session, remove_temp_ban_url, headers, {"player_id": player_id}, player_id),
                remove_vip_status(session, remove_vip_url, headers, {"player_id": player_id}, player_id)
            ])
            completed_players += 1
            if completed_players % 10 == 0:
                await send_progress(interaction, total_players, completed_players)
                await asyncio.sleep(10)

        await asyncio.gather(*removal_tasks)
        
        try:
            blacklist_id = await create_or_get_blacklist(session, headers, create_blacklist_url, get_blacklists_url, blacklist_name)
            tasks = [
                add_players_to_blacklist(session, players, blacklist_id, headers, add_blacklist_record_url, reason, admin_name),
                add_vip_status(session, vip_players, headers, add_vip_url),
                add_vip_status(session, non_vip_players, headers, add_vip_url),
                flag_players(session, vip_players, headers, flag_player_url, vip_first_flag, vip_second_flag),
                flag_players(session, non_vip_players, headers, flag_player_url, non_vip_flag, None)
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"⛔ | ERROR    | {e}")

    await interaction.followup.send("Import complete! You will receive a direct message with the log file.")

async def remove_perma_ban(session, url, headers, json_data, player_id):
    try:
        async with session.post(url, headers=headers, json=json_data) as response:
            if response.status == 200:
                logging.info(f"✅ | SUCCESS  | ✔️ Remove Perma-Ban | ID: {player_id}")
            else:
                text = await response.text()
                logging.error(f"⛔ | ERROR    | ✔️ Remove Perma-Ban | ID: {player_id} | Status: {response.status} | Response: {text}")
    except Exception as e:
        logging.error(f"⛔ | ERROR    | ✔️ Remove Perma-Ban | ID: {player_id} | {e}")

async def remove_temp_ban(session, url, headers, json_data, player_id):
    try:
        async with session.post(url, headers=headers, json=json_data) as response:
            if response.status == 200:
                logging.info(f"✅ | SUCCESS  | 🕔 Remove Temp-Ban  | ID: {player_id}")
            else:
                text = await response.text()
                logging.error(f"⛔ | ERROR    | 🕔 Remove Temp-Ban  | ID: {player_id} | Status: {response.status} | Response: {text}")
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 🕔 Remove Temp-Ban  | ID: {player_id} | {e}")            

async def remove_vip_status(session, url, headers, json_data, player_id):
    try:
        async with session.post(url, headers=headers, json=json_data) as response:
            if response.status == 200:
                logging.info(f"✅ | SUCCESS  | 👑 Remove VIP       | ID: {player_id}")
            else:
                text = await response.text()
                logging.error(f"⛔ | ERROR    | 👑 Remove VIP       | ID: {player_id} | Status: {response.status} | Response: {text}")
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 👑 Remove VIP       | ID: {player_id} | {e}")     

def read_players_from_file(file_path):
    try:
        players = []
        with open(file_path, 'r', encoding='utf-8') as file:
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
                    "steam_id": steam_id.strip(),
                    "name": name.strip(),
                    "expiration": expiration
                })
        if len(players) > 0 and any(player["expiration"] for player in players):
            logging.info(f"✅ | SUCCESS  | 📂 Load CRcon File  | {len(players)} Players in {file_path}.")
        else:
            logging.info(f"✅ | SUCCESS  | 📂 Load Bulk File   | {len(players)} Players in {file_path}.")

        return players
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 📂 Load File        | {file_path} | {e}")
        raise SystemExit

async def create_or_get_blacklist(session, headers, create_url, get_url, blacklist_name):
    blacklist_data = {
        "name": blacklist_name,
        "servers": None
    }
    try:
        async with session.post(create_url, headers=headers, json=blacklist_data) as response:
            if response.status == 200:
                logging.info("✅ | SUCCESS  | 📓 Create Blacklist")
            else:
                text = await response.text()
                logging.error(f"⛔ | ERROR    | 📓 Create Blacklist | Status: {response.status} | Response: {text}")
                raise Exception(f"Error on creation of blacklist: {text}")
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 📓 Create Blacklist | {e}")
        raise e
    try:
        async with session.get(get_url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                blacklists = result.get('result', [])
                logging.info(f"✅ | SUCCESS  | 🔎 Find Blacklist   | {len(blacklists)} Blacklists found.")
                for bl in blacklists:
                    if bl.get('name') == blacklist_name:
                        logging.info(f"✅ | SUCCESS  | 🔎 Find Blacklist   | ID = {bl.get('id')}, Name = {blacklist_name}")
                        return bl.get('id')

                logging.error(f"⛔ | ERROR    | 🔎 Find Blacklist   | No blacklist found with the name {blacklist_name}")
                raise Exception(f"No blacklist found with the name {blacklist_name}")
            else:
                text = await response.text()
                logging.error(f"⛔ | ERROR    | 🔎 Find Blacklist   | Status: {response.status} | Response: {text}")
                raise Exception(f"Error on fetching the blacklists: {text}")
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 🔎 Find Blacklist   | {e}")
        raise e

async def add_players_to_blacklist(session, players, blacklist_id, headers, url, reason, admin_name):
    for player in players:
        blacklist_record_data = {
            "player_id": player["steam_id"],
            "blacklist_id": blacklist_id,
            "reason": reason,
            "expires_at": None,
            "admin_name": admin_name
        }
        try:
            async with session.post(url, headers=headers, json=blacklist_record_data) as response:
                if response.status == 200:
                    logging.info(f"✅ | SUCCESS  | 🚷 Add to Blacklist | ID: {player['steam_id']} | Name: {player['name']}")
                else:
                    text = await response.text()
                    logging.error(f"⛔ | ERROR    | 🚷 Add to Blacklist | ID: {player['steam_id']} | Name: {player['name']} | Status: {response.status}")
                    logging.error(f"Response: {text}")
        except Exception as e:
            logging.error(f"⛔ | ERROR    | 🚷 Add to Blacklist | ID: {player['steam_id']} | Name: {player['name']} | {e}")

async def add_vip_status(session, players, headers, url):
    for player in players:
        vip_data = {
            "player_id": player["steam_id"],
            "description": player.get("description", ""),
            "expiration": None
        }
        try:
            async with session.post(url, headers=headers, json=vip_data) as response:
                if response.status == 200:
                    logging.info(f"✅ | SUCCESS  | 💎 Add VIP          | ID: {player['steam_id']} | Name: {player['name']}")
                else:
                    text = await response.text()
                    logging.error(f"⛔ | ERROR    | 💎 Add VIP          | ID: {player['steam_id']} | Name: {player['name']} | Status: {response.status}")
                    logging.error(f"Response: {text}")
        except Exception as e:
            logging.error(f"⛔ | ERROR    | 💎 Add VIP          | ID: {player['steam_id']} | Name: {player['name']} | {e}")

async def flag_players(session, players, headers, url, first_flag, second_flag=None):
    for player in players:
        await flag_player(session, player['steam_id'], player['name'], headers, url, first_flag)
        if second_flag:
            await flag_player(session, player['steam_id'], player['name'], headers, url, second_flag)

async def flag_player(session, player_id, player_name, headers, url, flag, comment=None):
    flag_data = {
        "player_id": player_id,
        "flag": flag,
        "player_name": player_name,
        "comment": comment
    }
    try:
        async with session.post(url, headers=headers, json=flag_data) as response:
            if response.status == 200:
                logging.info(f"✅ | SUCCESS  | 🚩 Add Flag {flag}      | ID: {player_id} | Name: {player_name}")
            else:
                text = await response.text()
                logging.error(f"⛔ | ERROR    | 🚩 Add Flag {flag}      | ID: {player_id} | Name: {player_name} | Status: {response.status}")
                logging.error(f"Response: {text}")
    except Exception as e:
        logging.error(f"⛔ | ERROR    | 🚩 Add Flag {flag}      | ID: {player_id} | Name: {player_name} | {e}")

async def discord_request_with_retry(interaction, message, view=None):
    while True:
        try:
            if view:
                await interaction.channel.send(message, view=view)
            else:
                await interaction.channel.send(message)
            break  # Anfrage erfolgreich, Schleife verlassen
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print("Headers:", response.headers)
                retry_after = int(e.response.headers.get("Retry-After", 1))
                await asyncio.sleep(retry_after)
            else:
                raise e

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

    if channel:
        await discord_request_with_retry(channel, "To import Player Data, please go ahead!", view=ImportView())
    else:
        print(f"Channel ID {channel_id} not found.")

bot.run(TOKEN)
