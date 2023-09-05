import pathlib

import discord
import json
import random
import os
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
from datetime import datetime, timedelta
from discord.ext.commands import bot
import Email.db as db
import Email.fetchmail as fetch
import Cogs.Json.jshelper as jshelper
from discord.ext.commands.cooldowns import BucketType
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')
log_file_handler = logging.FileHandler(filename=f'{__name__}.log',mode='a')
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)


t = BucketType.user
rate = 1
per = 2

async def checkmail(money, codeid):
    endTime = datetime.now() + timedelta(minutes=30)
    while True:
        if datetime.now() >= endTime:
            return False
        all = db.read_useremail()
        for codes in all:
            try:
                code = int(codes[1])
            except:
                continue
            try:
                cash = float(codes[2])
            except:
                continue
            if cash == money and code == codeid:
                return True
        await asyncio.sleep(30)

def gencode():
    number = random.randint(1000, 9999)
    all = db.read_useremail()
    if len(all) == 0:
        return number
    for code in all:
        if number == code:
            return gencode()
        else:
            return number
    

class app(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        data = jshelper.openf("/config/config.json")
        self.price = data["Price"]
        self.ca = f'Cashapp: ${data["cashapp"]}'
        self.vm = f'Venmo: @{data["venmo"]}'
        self.note = data["note"]
        self.role = data["role"] 
        self.fetch_email.start()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listprice(self, ctx):
        embed1 = discord.Embed(title="Pay using Cashapp or Venmo",
                               description=f"Cost: ${self.price}.", color=0xf50000)
        await ctx.channel.send(embed=embed1)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprice(self, ctx, price):
        if price.isnumeric():
            data = jshelper.openf("/config/config.json")
            data["Price"] = int(price)
            self.price = int(price)
            jshelper.savef("/config/config.json", data)
            embed = discord.Embed(title=f"${price} has been set as the price.", color=0xf50000)
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrole(self, ctx, role: discord.Role):
        data = jshelper.openf("/config/config.json")
        data["role"] = str(role.name)
        self.role = str(role.name)
        jshelper.savef("/config/config.json", data)
        embed = discord.Embed(title=f"{role} has been set as the role.", color=0xf50000)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setpayment(self, ctx, type, addy):
        type = str.lower(type)
        if type == "cashapp":
            data = jshelper.openf("/config/config.json")
            data["cashapp"] = str(addy)
            self.ca = f'Cashapp: ${str(addy)}'
            jshelper.savef("/config/config.json", data)
            embed = discord.Embed(title=f"${addy} has been set as the cashapp address.", color=0xf50000)
            await ctx.send(embed=embed)
        elif type == "venmo":
            data = jshelper.openf("/config/config.json")
            data["venmo"] = str(addy)
            self.vm = f'Venmo: ${str(addy)}'
            jshelper.savef("/config/config.json", data)
            embed = discord.Embed(title=f"@{addy} has been set as the Venmo address.", color=0xf50000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'Error, Please use ".setpayment (cashapp/venmo) address"', color=0xf50000)
            await ctx.send(embed=embed)

    async def assignrole(self, ctx, role):
        role = get(ctx.guild.roles, name=role)
        await ctx.message.author.add_roles(role, reason="Donated.")

    @commands.command()
    async def cancel(self, ctx):
        if jshelper.checkopen(int(ctx.author.id)):
            await ctx.author.send("Your Previous order has been canceled.")
            jshelper.makeclose(ctx.author.id)
        else:
            await ctx.author.send("Your don't have any orders open.")
    
    @commands.cooldown(rate, per, t)
    @commands.command(ignore_extra=False)
    async def donate(self, ctx):
        await ctx.channel.send(f'{ctx.author.mention} Please check dms!')
        one  = '1️⃣'
        two = '2️⃣'
        nay = '❌'
        tick = '✅'
        recs = [one,two,nay,tick]
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in recs
        price = self.price
        if jshelper.checkopen(int(ctx.author.id)):
            embed = discord.Embed(color=0xf50000)
            embed.add_field(name=f"ERROR",
                            value=f"Please Finish your existing order before opening a new one. \nOr press {nay} button to cancel your previous order.")
            msg = await ctx.author.send(embed=embed)
            await msg.add_reaction(nay)
            try:
                reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await ctx.author.send("Timed out.")
            else:
                await self.cancel(ctx)
        embed = discord.Embed(title="Choose Payment Method",description=f'Click {one} to donate with Cashapp.\nClick {two} to donate with Venmo.\nThis menu will time out in 2 minutes.',color=0x800080)
        msg = await ctx.author.send(embed=embed)
        await msg.add_reaction(one)
        await msg.add_reaction(two)
        try:
            reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send("Timed out.")
        else:
            if str(reaction.emoji) == one:
                payment = self.ca
            elif str(reaction.emoji) == two: 
                payment = self.vm
            else:
                ctx.author.send("Incorrect reaction please start over again.")
                return
            number = gencode()
            note = self.note + str(number)
            jshelper.userexsist(ctx.author.id)  
            jshelper.makeopen(ctx.author.id)
            
            embed = discord.Embed(title=f'Payment via {payment}',color=0xf50000)
            embed.add_field(name=f"Price: ${price} \n{payment}\nNote: {note}\nMake sure you send the exact amount with the NOTE.",
                            value=f"This page will timeout in 30 mins.\nClick {tick} once you have sent the payment.")
            msg = await ctx.author.send(embed=embed)
            await ctx.author.send("Here is an example of how to fill out the cashapp form.", file=discord.File('Screenshots/example_cashapp.jpg'))
            await ctx.author.send("Below is the note so you can copy and paste:")
            await ctx.author.send(note)
            await msg.add_reaction(tick)
            try:
                reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=1800.0, check=check)
            except asyncio.TimeoutError:
                await ctx.author.send("Timed out.")
            else:
                embed = discord.Embed(color=0xf50000)
                embed.add_field(name=f"Please wait while we process your payment!",
                                value=f"Usually takes upto 5 mins.")
                msg = await ctx.author.send(embed=embed)
                checkifright = await checkmail(price, number)
                if checkifright:
                    await msg.delete()
                    embed = discord.Embed(title= "Payment recieved. Thank you!", color=0x00ff00)
                    await ctx.author.send(embed=embed)
                    await self.assignrole(ctx,self.role)
                else:
                    await ctx.author.send(
                        f"Timed out. Payment not Received. Contact server admin if you have paid.")
                jshelper.makeclose(ctx.author.id)
            
    @tasks.loop(seconds=60)
    async def fetch_email(self):
        fetch.fetchmail()


async def setup(bot):
    await bot.add_cog(app(bot))
