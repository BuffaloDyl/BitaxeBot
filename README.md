This is meant to be run on a machine on the same network as your Bitaxe. I chose to run it on my Umbrel node.
Install the whl package found in dist/ with pip3.
Edit the config file found at ~/BitaxeBot/config.ini, enter your Bitaxe IP, Telegram User ID, and your telegram bot token.
You can add as many presets as you would like, call them from the bot with /preset (num or string).
There are no gaurdrails on the settings you provide!
Please dont fry your machine!

I set mine up as a systemd service.
