import discord
import os
import argparse
import sys
import shlex
import json
import importlib

from utils import default
from utils import sqlite as db
from utils.bot_runner import Bot, HelpFormat

with open("./config.json", "r", encoding="utf8") as f:
    config = json.load(f)


def main():
    parser = argparse.ArgumentParser(description="AlexFlipnote's Discord Event Manager")
    parser.add_argument("-e", "--event", help="Event filename you want to run (without .py at end)", required=True)
    parser.add_argument("-r", "--reset", help="Reset the database", action="store_true")

    try:
        args = parser.parse_args(
            shlex.split(" ".join(sys.argv[1:]) or "--help")
        )
    except Exception as e:
        print(f"[!] There was an error parsing your command...\n{e}")
        sys.exit(1)

    event_file = args.event
    if not os.path.isfile(f"./events/{event_file}.py"):
        print(f"[!] File {event_file}.py does not exist, stopping...")
        sys.exit(1)

    print("[+] Creating bot instance...")
    bot = Bot(
        command_prefix=config["prefix"], prefix=config["prefix"],
        command_attrs=dict(hidden=True), help_command=HelpFormat(),
        allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
        intents=discord.Intents(guilds=True, members=True, messages=True, reactions=True, presences=True)
    )

    print("[+] Loading custom config values to discord.Bot() class...")
    bot.custom_extension_name = event_file
    bot.custom_presence = {
        "status": config.get("status_type", "online"),
        "message": config.get("status_msg", None)
    }

    bot.event_config = {
        "category_id": config.get("event_category_id", None),
        "guild_id": config.get("event_guild_id", None)
    }

    print("[+] Checking for database structure...")
    importlib.import_module(f"events.{event_file}")
    bot.pool = None

    def create_drop_tables(method: str):
        all_tables = [g for g in db.Table.all_tables()]
        for table in all_tables:
            try:
                getattr(table, method)(filename=event_file)
            except Exception as e:
                print(f'Could not {method} {table.__tablename__}.\n\nError: {e}')
            else:
                print(f'[{table.__module__}] {method}ed {table.__tablename__}.')
        return all_tables

    print(f"[+] Connecting to storage_{event_file}.db file...")

    if args.reset:
        try:
            os.remove(f"./database/storage_{event_file}.db")
            print("[-] Successfully deleted previous database (DROPPED)")
        except FileNotFoundError:
            pass

    print("[+] Creating database structure...")
    bot.pool = db.Database(filename=event_file)
    if not create_drop_tables("create"):
        print("[?] False alarm, deleting database...")
        os.remove(f"./database/storage_{event_file}.db")

    print("[+] Logging in to Discord...")
    bot.run(config["token"])


try:
    main()
except KeyboardInterrupt:
    print("[x] Stopping event manager...")
except Exception as e:
    print(
        f"\n[!] Unexpected error appeared:"
        f"\n{default.traceback_maker(e)}"
    )
