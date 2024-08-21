import os
import telebot
import requests
import json
import configparser

def main():
    global config, BOT_TOKEN, IP, TelegramUID

    def get_config_file_path():
        # Define the default path for config.ini in the user's home directory
        home_dir = os.path.expanduser("~")
        config_file_path = os.path.join(home_dir, 'BitaxeBot', 'config.ini')

        # Create the directory if it doesn't exist
        if not os.path.exists(os.path.dirname(config_file_path)):
            os.makedirs(os.path.dirname(config_file_path))

        return config_file_path

    def read_config():
        configu = configparser.ConfigParser()
        config_file_path = get_config_file_path()
        configu.read(config_file_path)
        return configu

    config = read_config()
    try:
        BOT_TOKEN = config['config']['BOT_TOKEN']
        IP = config['config']['IP']
        TelegramUID = int(config['config']['TelegramUID'])
    except KeyError as e:
        print(f"Missing configuration option: {e}")
        return

    commands = [
        {"command": "info", "description": "Show Bitaxe info"},
        {"command": "preset", "description": "/preset <num> - Over/Underclock your Bitaxe"},
        {"command": "restart", "description": "Restart your Bitaxe"},
    ]
    bot = telebot.TeleBot(BOT_TOKEN)

    # Set bot commands
    apiurl = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    apiresponse = requests.post(apiurl, json={"commands": commands})
    if apiresponse.status_code == 200:
        print("Commands updated successfully!")
    else:
        print(f"Failed to update commands: {apiresponse.status_code}, {apiresponse.text}")

    # Define handlers
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

    # Start polling
    bot.infinity_polling()

def BitaxePreset(PresetNum):
    json_data_str = config['presets'].get(PresetNum, '{}')
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
            return "Settings Changed! Restart required (/restart)"
        else:
            return f"Error: Unable to update resource. Status code: {response.status_code}, Response: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def time(seconds):
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
    url = f"http://{IP}/api/system/info"
    response = requests.get(url)
    json_data = response.json()

    T = json_data.get("temp")
    HR = json_data.get("hashRate")
    BD = json_data.get("bestDiff")
    SD = json_data.get("bestSessionDiff")
    CV = json_data.get("coreVoltage")
    F = json_data.get("frequency")
    UT = int(json_data.get("uptimeSeconds"))

    text_string = f"Temp: {T} C\nHashrate: {round(HR)} GH/s\nSession Best Difficulty: {SD}\nAll-Time Best Difficulty: {BD}\nCorevoltage: {CV}\nFrequency: {F}\nUptime: {time(UT)}"
    return text_string

def BitaxeRestart():
    response = requests.post(
        f"http://{IP}/api/system/restart",
        headers={"Content-Type": "application/json"}
    )
    return response.text

if __name__ == "__main__":
    main()
