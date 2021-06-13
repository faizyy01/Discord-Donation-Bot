import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
import asyncio

with open("token.txt", "r") as f:
    TOKEN = f.readline()

bot = commands.Bot(command_prefix=".")
bot.remove_command('help')


@bot.event
async def on_ready():
    print("bot is online.")


@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, name):
    bot.load_extension(f'Cogs.{name}')
    print(f"The {name} cog has been loaded successfully.")


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, name):
    bot.unload_extension(f'Cogs.{name}')
    print(f"The {name} cog has been unloaded successfully.")


@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, name):
    bot.unload_extension(f'Cogs.{name}')
    bot.load_extension(f'Cogs.{name}')
    print(f"The {name} cog has been reloaded successfully.")


@bot.command()
@commands.has_permissions(administrator=True)
async def openstore(ctx):
    global status
    status = 1
    await ctx.channel.send("store is open")


@bot.command()
@commands.has_permissions(administrator=True)
async def closestore(ctx):
    global status
    status = 0
    await ctx.channel.send("store is closed")


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return
    if not message.guild:
        return
    if status == 0:
        return
    await bot.process_commands(message)

@bot.event
async def on_guild_channel_create(channel):
    await asyncio.sleep(1)
    embed = discord.Embed(title="Help", description="These are the commands for the bot.", color=0xf50000)
    embed.add_field(name='.buy <amount> <cashapp or Venmo>',
                    value='This command is used to buy Example: `.buy cashapp`',
                    inline=False)
    embed.add_field(name='.help', value='This command is used to display this message.', inline=False)
    await channel.send(embed=embed)
    await asyncio.sleep(1)



@bot.command()
@commands.has_permissions(administrator=True)
async def all(ctx):
    for filename in os.listdir("Cogs"):
        if filename.endswith('.py'):
            bot.unload_extension(f'Cogs.{filename[:-3]}')
    for filename in os.listdir("Cogs"):
        if filename.endswith('.py'):
            bot.load_extension(f'Cogs.{filename[:-3]}')
    print("All cogs has been reloaded.")


for filename in os.listdir("Cogs"):
    if filename.endswith('.py'):
        bot.load_extension(f'Cogs.{filename[:-3]}')

bot.run(TOKEN)

