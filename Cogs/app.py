import discord
import json
import random
import os
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta

from discord.ext.commands import bot
import Email.db as db
import Email.fetchmail as fetch
import Cogs.Json.jshelper as jshelper
from discord.ext.commands.cooldowns import BucketType

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


class app(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        data = jshelper.openf("/settings.json")
        self.price = data["Price"]
        self.ca = f'Cashapp: ${data["cashapp"]}'
        self.vm = f'Venmo: @{data["venmo"]}'
        self.note = data["note"]
        # self.change_status.start()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listprices(self, ctx):
        embed1 = discord.Embed(title="Pay using Cashapp or Venmo",
                               description=f"Cost: ${self.price}.", color=0xf50000)
        await ctx.channel.send(embed=embed1)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprice(self, ctx, price):
        if price.isnumeric():
            data = jshelper.openf("/settings.json")
            data["Price"] = int(price)
            jshelper.savef("/settings.json", data)
            embed = discord.Embed(title=f"${price} has been set as the price.", color=0xf50000)
            await ctx.send(embed=embed)
                
    @commands.command()
    async def cancel(self, ctx):
        if jshelper.checkopen(int(ctx.author.id)):
            await ctx.author.send("Your Previous order has been canceled.")
            jshelper.makeclose(ctx.author.id)
        else:
            await ctx.author.send("Your don't have any orders open.")
    
    @commands.cooldown(rate, per, t)
    @commands.command(ignore_extra=False)
    async def buy(self, ctx):
        recs = ['❌','1️⃣','2️⃣']
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in recs
    
        price = self.price
        if jshelper.checkopen(int(ctx.author.id)):
            nay = '❌'
            embed = discord.Embed(color=0xf50000)
            embed.add_field(name=f"ERROR",
                            value=f"Please Finish your existing order before opening a new one. \nOr press {nay} button to cancel your previous order.")
            msg = await ctx.author.send(embed=embed)
            await msg.add_reaction(nay)
            try:
                reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.author.send("Timed out.")
            else:
                await self.cancel(ctx)

        one  = '1️⃣'
        two = '2️⃣'
        embed = discord.Embed(title="Choose Payment Method",description=f'Click {one} to pay with Cashapp.\nClick {two} to pay with Venmo.\nThis menu will time out in 1 minute.',color=0x800080)
        msg = await ctx.author.send(embed=embed)
        await msg.add_reaction(one)
        await msg.add_reaction(two)
        try:
            reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
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
            
            number = random.randint(1000, 9999)
            note = self.note + str(number)
            jshelper.userexsist(ctx.author.id)  
            jshelper.makeopen(ctx.author.id)
            
            embed = discord.Embed(title=f'Payment via {payment}',color=0xf50000)
            embed.add_field(name=f"Price: ${price} \n{payment}\nNote: {note}",
                            value=f"Make sure you send the exact amount with the note.\nThis Order will auto-cancel in 30 mins.\nBot takes upto 5 mins to process after payment.")
            await ctx.author.send(embed=embed)
            await ctx.author.send(note)
            checkifright = await checkmail(price, number)
            if checkifright:
                await ctx.author.send(f"{ctx.author.mention} Thank You! Payment recieved.")
            else:
                await ctx.author.send(
                    f"Timed out. Payment not Received.")
            jshelper.makeclose(ctx.author.id)
            
    @tasks.loop(seconds=30)
    async def fetch_email(self):
        fetch.fetchmail()


def setup(bot):
    bot.add_cog(app(bot))
