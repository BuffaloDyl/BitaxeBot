To enable nostr functionality i have included all of the work from callebtc/python-nostr in the source. Thanks dr. calle.
This is meant to be run on a machine on the same local network as your Bitaxe. I chose to run it on my Umbrel node. 
Install the whl package found in dist/ with pip3. You will likely get an error and need to install pkg-config with apt. 
After install, edit the config file found at ~/BitaxeBot/config.ini.
For telegram, set enable to 1, enter your Telegram bot token and telegram userid
for nostr, set enable to 1, and enter the npub at which you want to receive updates. 'generatednsec' will auto-fill if you leave it blank.
You can add as many presets as you would like. 
There are no guardrails on the settings you provide, so please dont fry your machine!

I set mine up as a systemd service.

If you would like a notification that youve hit a block, set EnableMempool=1 and enter the address of your mempool instance in mempool=
on Umbrel the mempool app is on port 3006, so I enter 192.168.86.21:3006
If you use mempool.space you are blowing the privacy of that address by tying your IP to it. 

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