# BitaxeBot

BitaxeBot is designed to interact with the AxeOS API, Telegram API, and nostr protocol. This document provides incomplete instructions for installation, configuration, and usage of BitaxeBot.

To enable nostr functionality i have included all of the work from callebtc/python-nostr in the source. Thanks dr. calle.

**TL/DR**

This is meant to be run on a machine on the same local network as your Bitaxe. I chose to run it on my Umbrel node.  

```
Commands:
    Telegram:
        '/info' - shows bitaxe info
        '/presets' - lists presets you have set in config.ini
        '/restart' - restarts your bitaxe
        '/preset number/string' - changes settings
    nostr:
        'info' - shows bitaxe info
        'presets' - lists presets you have set in config.ini
        'restart' - restarts your bitaxe
        'preset number/string' - changes settings
```

## Installation

### Prerequisites

Ensure you have Python 3.11 or later installed on your system. You will also need `pip3` for installing Python packages.

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/BuffaloDyl/BitaxeBot.git
   cd BitaxeBot
   ```

2. **Install the Package:**

   You can install BitaxeBot from the source using `pip3`:

   ```bash
   pip3 install .
   ```

   Alternatively, install from the whl file in dist/:

   ```bash
   pip3 install dist/BitaxeBot-0.4-py3-none-any.whl
   ```

## Configuration

### Configuration File

The `config.ini` file is used to configure BitaxeBot. It should be in `~/BitaxeBot/`. If the file does not exist, BitaxeBot will create it.

You can edit the file using
```
BitaxeBot -config
```

### Default Configuration

Here is a copy of the default `config.ini`:

```ini
[bitaxe]
# IP of your Bitaxe
ip = 192.168.86.34

[telegram]
# Set to 0 to disable, 1 to enable
enable = 0
bot_token = 6740000000:Axxxxxxxxxxxxxxxxxx
telegramuid = 00001234

[mempool]
# Set to 0 to disable, 1 to enable. Will monitor your BTC address for a non-zero balance.
# Using mempool.space or any other public instance will destroy your privacy
enable = 0
mempool = umbrel.local:3006

[nostr]
botname = Bitaxebot-nostr
# Set to 0 to disable, 1 to enable
enable = 0
# Your npub where you want to receive bot update DMs
npub =
# This will auto-generate. DO NOT use for any other purpose, this nsec is in plain text and therefore not secure
generatednsec =

[nostrrelays]
1 = wss://nostr-pub.wellorder.net
2 = wss://relay.damus.io
3 =
4 =

[presets]
# There are no guardrails for these settings, don't fry your miner
low = {"corevoltage":1166, "frequency":490}
mid = {"corevoltage":1200, "frequency":500}
high = {"corevoltage":1250, "frequency":525}
1 = {"corevoltage":1250, "frequency":550}
2 = {"corevoltage":1300, "frequency":525}
3 = {"corevoltage":1300, "frequency":550}
4 =
5 =

[version]
v = 0.4
```

## Usage

### Running BitaxeBot

To run BitaxeBot, simply run:

```bash
BitaxeBot
```

### Setting Up a Systemd Service

To run BitaxeBot as a system service, you can create a systemd service file. Here’s a sample service file configuration:

1. **Create the Service File:**

   ```bash
   sudo nano /etc/systemd/system/bitaxebot.service
   ```

2. **Add the Following Content:**

   ```ini
   [Unit]
   Description=BitaxeBot Service
   After=network.target

   [Service]
   User=yourusername
   ExecStart=/usr/bin/python3 -m BitaxeBot
   Restart=on-failure
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start the Service:**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable bitaxebot
   sudo systemctl start bitaxebot
   ```

4. **Check the Status:**

   ```bash
   sudo systemctl status bitaxebot
   ```

This setup will ensure BitaxeBot runs as a background service and restarts automatically if it fails.


## License

[MIT](https://choosealicense.com/licenses/mit/)