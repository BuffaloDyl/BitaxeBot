import os
import requests
import json
import telebot
import configparser
import threading
import time
from nostr.key import PrivateKey
from nostr.event import EncryptedDirectMessage
import ssl
from nostr.relay_manager import RelayManager
from nostr.key import PublicKey
import importlib.resources as resources
import shutil
import BitaxeBot
import argparse

def check_for_config():
    config_dir = os.path.expanduser('~/BitaxeBot')
    config_path = os.path.join(config_dir, 'config.ini')
    config_bak_path = os.path.join(config_dir, 'config.ini.bak')
    os.makedirs(config_dir, exist_ok=True)

    try:
        config_in_package = resources.files(BitaxeBot).joinpath('config.ini')
        shipped_config = configparser.ConfigParser()
        shipped_config.read(config_in_package)

        if not os.path.isfile(config_path):
            print(f"Users config.ini not found. Copying from package...")
            shutil.copy(config_in_package, config_path)
            print(f"Running Editor...")
            edit_config()
        else:
            user_config = configparser.ConfigParser()
            user_config.read(config_path)

            if 'version' in shipped_config and 'version' in user_config:
                shipped_version = shipped_config['version'].get('v', '0')
                user_version = user_config['version'].get('v', '0')

                if shipped_version > user_version:
                    print(f"config.ini already exists. Creating backup and merging missing keys/values...")
                    shutil.copy(config_path, config_bak_path)
                    for section in shipped_config.sections():
                        if not user_config.has_section(section):
                            user_config.add_section(section)
                        for key, value in shipped_config.items(section):
                            if not user_config.has_option(section, key):
                                user_config.set(section, key, value)

                    with open(config_path, 'w') as config_file:
                        user_config.write(config_file)
                    print(f"Running Editor...")
                    edit_config()
                else:
                    print(f"User's config.ini is up to date.")
            else:
                print(f"Newer version detected in shipped config. Merging missing keys/values...")
                shutil.copy(config_path, config_bak_path)
                print(f"Backup created at config.ini.bak")
                for section in shipped_config.sections():
                        print(section)
                        if not user_config.has_section(section):
                            user_config.add_section(section)
                        for key, value in shipped_config.items(section):
                            if not user_config.has_option(section, key):
                                user_config.set(section, key, value)
                with open(config_path, 'w') as config_file:
                    user_config.write(config_file)
                print(f"Running Editor...")
                edit_config()
    except Exception as e:
        print(f"Failed to process config.ini: {e}")


def main():
    parser = argparse.ArgumentParser(description="BitaxeBot CLI")
    parser.add_argument('-config', action='store_true', help="Launch config editor")
    
    args = parser.parse_args()

    if args.config:
        edit_config()
    else:
        check_for_config()
    global config, bot, BOT_TOKEN, IP, EnableTelegram, Enablenostr, TelegramUID, Mempool, EnableMempool, n_pub, HEXnpub, private_key, public_key, boottime
    def get_config_file_path():
        home_dir = os.path.expanduser("~")
        config_file_path = os.path.join(home_dir, 'BitaxeBot', 'config.ini')

        if not os.path.exists(os.path.dirname(config_file_path)):
            os.makedirs(os.path.dirname(config_file_path))

        return config_file_path

    def read_config():
        configu = configparser.ConfigParser()
        config_file_path = get_config_file_path()
        configu.read(config_file_path)
        return configu
    def write_config():
        config_file_path = get_config_file_path()
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    config = read_config()
    try:
        n_pub = str(config['nostr']['npub'])
        BOT_TOKEN = config['telegram']['BOT_TOKEN']
        IP = config['bitaxe']['IP']
        TelegramUID = int(config['telegram']['TelegramUID']) if config['telegram']['TelegramUID'] else 0
        EnableMempool = int(config['mempool']['enable']) if config['mempool']['enable'] else 0
        EnableTelegram = int(config['telegram']['enable']) if config['telegram']['enable'] else 0
        Enablenostr = int(config['nostr']['enable']) if config['nostr']['enable'] else 0
        HEXnpub = PublicKey.from_npub(n_pub).hex()
        boottime = time.time() 

        if config['nostr']['Generatednsec'] == "":
            private_key = PrivateKey()
            public_key = private_key.public_key
            config['nostr']['Generatednsec'] = private_key.hex()
            write_config()
        else: 
            private_key = PrivateKey(bytes.fromhex(config['nostr']['Generatednsec']))
            public_key = private_key.public_key
    except (ValueError, KeyError) as e:
        print(f"Missing configuration option: {e}")
        return
    if (Enablenostr == 1 or EnableTelegram == 1) and EnableMempool == 1:
        Mempool = config['mempool']['mempool']
        threading.Thread(target=did_i_win, daemon=True).start()
    if Enablenostr == 1:
        if EnableTelegram == 1:
            threading.Thread(target=ReadDMS, daemon=True).start()
        else:
            ReadDMS()
###TELEGRAM
    if EnableTelegram == 1:
        commands = [
            {"command": "info", "description": "Show Bitaxe info"},
            {"command": "presets", "description": "List presets"},
            {"command": "preset", "description": "/preset <num> - Over/Underclock your Bitaxe. Edit presets in ~/BitaxeBot/config.ini"},
            {"command": "restart", "description": "Restart your Bitaxe"},
        ]
        bot = telebot.TeleBot(BOT_TOKEN)
        apiurl = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
        apiresponse = requests.post(apiurl, json={"commands": commands})
        if apiresponse.status_code == 200:
            print("Commands updated successfully!")
        else:
            print(f"Failed to update commands: {apiresponse.status_code}, {apiresponse.text}")

        @bot.message_handler(commands=['info'])
        def handle_info(message):
            if TelegramUID == message.from_user.id:
                bot.send_message(message.from_user.id, BitaxeInfo())
            else:
                bot.reply_to(message, f"Not Authorized, add your TelegramUID ({message.from_user.id}) to config.ini")

        @bot.message_handler(commands=['preset'])
        def handle_preset(message):
            command_text = message.text[len('/preset '):]
            if TelegramUID == message.from_user.id:
                bot.reply_to(message, BitaxePreset(command_text))
            else:
                bot.reply_to(message, f"Not Authorized, add your TelegramUID ({message.from_user.id}) to config.ini")

        @bot.message_handler(commands=['restart'])
        def handle_restart(message):
            if TelegramUID == message.from_user.id:
                bot.reply_to(message, BitaxeRestart())
            else:
                bot.reply_to(message, f"Not Authorized, add your TelegramUID ({message.from_user.id}) to config.ini")

        @bot.message_handler(commands=['presets'])
        def handle_presets(message):
            if TelegramUID == message.from_user.id:
                presets = dict(config['presets'])
                presets_string = '\n'.join(f"{key} - {value}" for key, value in presets.items())
                bot.reply_to(message, presets_string)
            else:
                bot.reply_to(message, f"Not Authorized, add your TelegramUID ({message.from_user.id}) to config.ini")

        try: bot.send_message(TelegramUID, "BitaxeBot Online!")
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Missing configuration option: {e}")
        bot.infinity_polling()
###NOSTR
    
    

def nostDM(SecretMessage):
    global n_pub, HEXnpub
    dm = EncryptedDirectMessage(
    recipient_pubkey=HEXnpub,
    cleartext_content=SecretMessage,
    tags=[["expiration", f"{round(time.time() + (24*60*60))}"]]
    )
    private_key.sign_event(dm)
    relay_manager.publish_event(dm)
    return

from nostr.filter import Filter, Filters
from nostr.event import Event
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType

def ReadDMS():
    global relay_manager, HEXnpub
    relaystart() #establish and open relay connection
    threading.Thread(target=nostdmsubscribe, daemon=True).start() #ask relays for relevant DMs

    while True:
        while relay_manager.message_pool.has_events():
            event_msg = relay_manager.message_pool.get_event()
            try:
                if boottime < event_msg.event.created_at:
                    decrypted_message = private_key.decrypt_message(event_msg.event.content, HEXnpub)
                    print(f"New Event found {formattime(round(time.time() - boottime))}: {decrypted_message}")
                    procNostDM(decrypted_message)
            except Exception as e:
                print(f"Failed to decrypt message: {e}")
        time.sleep(1)

def relaystart():
    global relay_manager, HEXnpub
    relay_manager = RelayManager()
    relays = dict(config['nostrrelays']) #add relays
    for key, url in relays.items():
        if url != "":
            print(f"Adding relay: {url}")
            relay_manager.add_relay(url)
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
    time.sleep(1.25) # allow the connections to open

    #send connected DM
    nostDM("BitaxeBot Connected!")

    #update bot username
    botname = f"{{\"display_name\":\"{config['nostr']['botname']}\",\"name\":\"{config['nostr']['botname']}\",\"picture\":\"https://github.com/skot/bitaxe/raw/master/doc/bitaxe_204.jpg\"}}"
    event = Event(botname, public_key.hex(), kind=0)
    private_key.sign_event(event)
    event_json = event.to_message()
    relay_manager.publish_message(event_json)

def nostdmsubscribe():
    global relay_manager, HEXnpub
    while True:
        print("Updating Subscription...")
        filters = Filters([Filter(authors=[HEXnpub], kinds=[4])])
        subscription_id = f"Bitaxebot{time.time()}"
        request = [ClientMessageType.REQUEST, subscription_id]
        request.extend(filters.to_json_array())
        relay_manager.add_subscription(subscription_id, filters)

        message = json.dumps(request)
        relay_manager.publish_message(message)
        time.sleep(10*60)
        relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
        time.sleep(1.25) # allow the connections to open

def procNostDM(plaintextmsg):
    plaintext = str(plaintextmsg).lower()
    if plaintext == "info":
        nostDM(BitaxeInfo())
    elif plaintext == "restart":
        nostDM(BitaxeRestart())
    elif plaintext == "presets":
        presets = dict(config['presets'])
        presets_string = '\n'.join(f"{key} - {value}" for key, value in presets.items())
        nostDM(presets_string)
    elif plaintext.split()[0] == "preset":
        command_text = plaintext[len('preset '):]
        nostDM(BitaxePreset(command_text))
    else: nostDM(f"\"{plaintext}\" is not a recognized command")

###/NOSTR

def BitaxePreset(PresetNum):
    json_data_str = config['presets'].get(PresetNum, '{}')
    if json_data_str == "{}":
        return "Invalid preset number"
    try:
        data = json.loads(json_data_str)
    except json.JSONDecodeError:
        return "Error: Failed to parse JSON data from config."

    try:
        response = requests.patch(
            f"http://{IP}/api/system",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            time.sleep(4)
            BitaxeRestart()
            return "Settings Changed! Restarting...."
        else:
            return f"Error: Unable to update resource. Status code: {response.status_code}, Response: {response.text}"
    except requests.exceptions.Timeout:
        return f"Request timed out. Can't connect to Bitaxe."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def formattime(seconds):
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    result = []
    if days > 0:
        result.append(f"{days}d")
    if hours > 0:
        result.append(f"{hours}h")
    if minutes > 0:
        result.append(f"{minutes}m")
    if seconds > 0 or not result:
        result.append(f"{seconds}s")
    
    return ' '.join(result)

def BitaxeInfo():
    global addr
    try:
        url = f"http://{IP}/api/system/info"
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()

            T = json_data.get("temp")
            HR = json_data.get("hashRate")
            BD = json_data.get("bestDiff")
            SD = json_data.get("bestSessionDiff")
            CV = json_data.get("coreVoltage")
            F = json_data.get("frequency")
            UT = int(json_data.get("uptimeSeconds"))
            OH = int(json_data.get("overheat_mode"))
            SA = int(json_data.get("sharesAccepted"))
            SR = int(json_data.get("sharesRejected"))
            usr = json_data.get("stratumUser")
            addr = usr.split('.')[0]
            if OH != 0:
                overheatwarning = f"Bitaxe in Overheat mode\nThrottled for safety\nVisit AxeOS dashboard\n"
            else: overheatwarning = ""
            text_string = f"{overheatwarning}Temp: {T} C\nHashrate: {round(HR)} GH/s\nSession Best Difficulty: {SD}\nAll Time Best Difficulty: {BD}\nCorevoltage: {CV}\nFrequency: {F}\nUptime: {formattime(UT)}\nShares A/R: {SA}/{SR}"
            return text_string
        else:
            return f"Error: Unable to update resource. Status code: {response.status_code}, Response: {response.text}"
    except requests.exceptions.Timeout:
        return f"Request timed out. Can't connect to Bitaxe."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def BitaxeRestart():
    try:
        response = requests.post(
            f"http://{IP}/api/system/restart",
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: Unable to update resource. Status code: {response.status_code}, Response: {response.text}"
    except requests.exceptions.Timeout:
        return f"Request timed out. Can't connect to Bitaxe."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    
def Mempoolapi(memcalltype):
        try:
            response = requests.get(
            f"http://{Mempool}/api/address/{memcalltype}",
            headers={"Content-Type": "application/json"}
        )
            if response.status_code == 200:
                json_data = response.json()
                bal = json_data.get("chain_stats",{}).get("funded_txo_sum")
                return bal
            else:
                return f"Error: Unable to update resource. Status code: {response.status_code}, Response: {response.text}"
        except requests.exceptions.Timeout:
            return f"Request timed out. Can't connect to Bitaxe."
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

def did_i_win():
    BitaxeInfo()
    while True:
        time.sleep(60)
        try:
            response = requests.get(
            f"http://{Mempool}/api/address/{addr}",
            headers={"Content-Type": "application/json"}
        )
            if response.status_code == 200:
                json_data = response.json()
                bal = int(json_data.get("chain_stats",{}).get("funded_txo_sum"))
                if bal > 0:
                    if EnableTelegram == 1:
                        telebot.TeleBot(BOT_TOKEN).send_message(TelegramUID, f"Block Found\!\?\!\nAddress: ||{addr}||\nBalance: ||{bal/100000000:.3f} BTC||\nUse a new address \(with zero balance\) to stop this message".replace('.', '\\.'),parse_mode='MarkdownV2')
                    if Enablenostr == 1:
                        nostDM(f"Block Found!?!\nAddress: {addr}\nBalance: {bal/100000000:.3f} BTC\nUse a new address (with zero balance) to stop this message")
            else:
                return f"Error: Unable to update resource. Status code: {response.status_code}, Response: {response.text}"
        except requests.exceptions.Timeout:
            return f"Request timed out. Can't connect to Bitaxe."
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"\

def edit_config():
    import subprocess
    config_path = os.path.expanduser('~/BitaxeBot/config.ini')
    editor = os.environ.get('EDITOR', 'nano')
    try:
        subprocess.run([editor, config_path], check=True)
        print(f"Configuration file {config_path} opened in {editor}.")
    except subprocess.CalledProcessError as e:
        print(f"Error opening file in {editor}: {e}")
    except FileNotFoundError:
        print(f"Editor {editor} not found. Please install {editor} or set the EDITOR environment variable.")


if __name__ == "__main__":
    main()