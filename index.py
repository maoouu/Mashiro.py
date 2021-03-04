import os
import discord
import keep_alive

from utils import default
from utils.data import Bot, HelpFormat

config = default.config()
print("Logging in...")

bot = Bot(
    command_prefix=config["prefix"], prefix=config["prefix"],
    owner_ids=os.environ.get("OWNER"), command_attrs=dict(hidden=True), help_command=HelpFormat(),
    intents=discord.Intents(
        # kwargs found at https://discordpy.readthedocs.io/en/latest/api.html?highlight=intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True
    )
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    # run the server
    keep_alive.keep_alive()
    #run the bot
    bot.run(os.environ.get("BOT_TOKEN"))
except Exception as e:
    print(f'Error when logging in: {e}')
