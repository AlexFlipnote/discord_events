# discord_events
Custom bot I've made to host events on my personal Discord server.<br>
You can try the bot out in my personal server here: https://discord.gg/DpxkY3x (if I run an event at that time that is, lol)

# Requirements
Python 3.8 or above

# Setup
Everything is controlled by the `index.py` and `config.json` file (check example on how it should look). You create new events by simply making a new `.py` file inside the path `./events` that are structured to be like a discord.py Cogs file.

# How to use
You can run `python index.py` to view all commands, but if you just want to go right on, you simply do `python index.py --events <filename>` (without the .py at the end) and the bot will automatically load it in. If the bot detects a database class, it will automatically generate one that it takes usage of, you can also add the `--reset` argument to drop the entire database and start from scratch. The database is located inside the `./database` folder, name scheme is `database_<filename>.db`.

# Running 24/7
There are multiple ways to run the bot forever, preferably on a Linux server (that isn't your own PC).
A few examples of what you can use to run the bot:
- Linux screen: `screen -dmS Events python index.py --event filename`
- NodeJS PM2: `pm2 start pm2.json`

# License
Please give me credits if you choose to take usage of this, thank you ❤️
