import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import json
import Cogs.Json.jshelper as jshelper
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
log_formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')
log_file_handler = logging.FileHandler(filename=f'{__name__}.log',mode='a')
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)

jshelper.prestart()
data = jshelper.openf("/config/config.json")
if data["token"] == "":
    logger.critical('Missing Config')
    sys.exit()
        
data = jshelper.openf("/config/config.json")
TOKEN = data["token"]
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=".", intents = intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    logger.debug('Bot Online')


@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, name):
    bot.load_extension(f'Cogs.{name}')
    logger.debug(f"The {name} cog has been loaded successfully.")


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, name):
    bot.unload_extension(f'Cogs.{name}')
    logger.debug(f"The {name} cog has been unloaded successfully.")


@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, name):
    bot.unload_extension(f'Cogs.{name}')
    bot.load_extension(f'Cogs.{name}')
    logger.debug(f"The {name} cog has been reloaded successfully.")


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if not message.guild:
        return
    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def all(ctx):
    for filename in os.listdir("Cogs"):
        if filename.endswith('.py'):
            bot.unload_extension(f'Cogs.{filename[:-3]}')
    for filename in os.listdir("Cogs"):
        if filename.endswith('.py'):
            bot.load_extension(f'Cogs.{filename[:-3]}')
    logger.debug("All cogs has been reloaded.")


async def load_cogs():
    try:
        logger.debug('Loading cogs')
        await bot.load_extension('Cogs.app')
        logger.debug('App Cog loaded')
    except Exception as e:
        logger.critical(f'There was an error loading the cogs. Below is the exception: \n\n {e} \n\n________________________')

if __name__ == "__main__":
    asyncio.run(load_cogs())
    bot.run(TOKEN)