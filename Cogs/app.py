import discord
import json
import random
import os
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import Email.db as db
import Email.fetchmail as fetch
from discord.ext.commands.cooldowns import BucketType

t = BucketType.user
cashappaddy = "Cashapp: $"
paypaladdy = "Venmo: @"
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

    def openf(self, name):
        path = os.getcwd() + f"/Cogs/Json/{name}"
        with open(path, "r") as f:
            data = json.load(f)
        return data

    def savef(self, name, data):
        path = os.getcwd() + f"/Cogs/Json/{name}"
        with open(path, "w") as f:
            json.dump(data, f, indent=4, default=str)

    def save_user(self, id, creds):
        data = self.openf("cdb.json")
        data["members"][str(id)] = {
            "open": 0,
            "date": datetime.now(),
            "id": id,
        }
        self.savef("cdb.json", data)

    def makeopen(self, id):
        data = self.openf("cdb.json")
        check = 0
        for member in data["members"]:
            if data["members"][member]["id"] == id:
                check = 1
                data["members"][member]["open"] = 1
                self.savef("cdb.json", data)

    def makeclose(self, id):
        data = self.openf("cdb.json")
        check = 0
        for member in data["members"]:
            if data["members"][member]["id"] == id:
                check = 1
                data["members"][member]["open"] = 0
                self.savef("cdb.json", data)

    def checkopen(self, id):
        check = 0
        data = self.openf("cdb.json")
        for member in data["members"]:
            if data["members"][member]["id"] == id:
                if data["members"][member]["open"] == 1:
                    check = 1

        if check == 1:
            return True
        else:
            return False

    def userexsist(self, id):
        data = self.openf("cdb.json")
        check = 0
        for member in data["members"]:
            if data["members"][member]["id"] == id:
                check = 1

        if check != 1:
            self.save_user(id, 0)

    @commands.Cog.listener()
    async def on_ready(self):
        data = self.openf("info.json")
        self.price = data["Price"]
        self.ca = cashappaddy + data["cashapp"]
        self.vm = paypaladdy + data["venmo"]
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
    async def uc(self, ctx, member: discord.Member, amount):
        amount = int(amount)
        user_creds = self.get_creds(member.id)
        newbalance = user_creds + amount
        self.change_creds(member.id, newbalance)
        await ctx.channel.send("Updated users credits.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprice(self, ctx, price, tier):
        if price.isnumeric():
            data = self.openf("price.json")
            if tier is '1':
                data["Price"] = int(price)
                embed = discord.Embed(title=f"${price} has been set as the price.", color=0xf50000)
                await ctx.send(embed=embed)

    @commands.command()
    async def cancel(self, ctx):
        if self.checkopen(int(ctx.author.id)):
            await ctx.channel.send("Your Previous order has been canceled.")
            self.makeclose(ctx.author.id)
        else:
            await ctx.channel.send("Your don't have any orders open.")

    @commands.cooldown(rate, per, t)
    @commands.command(ignore_extra=False)
    async def buy(self, ctx, payment):
        price = self.price
        if self.checkopen(int(ctx.author.id)):
            await ctx.channel.send(
                "Please Finish your existing order before opening a new one. Or type '.cancel' to cancel your previous order.")
            return
        payment = payment.lower()
        if payment == "cashapp" or payment == "venmo" or payment == "cash app":
            number = random.randint(1000, 9999)
            note = self.note + str(number)
            if payment == "cashapp":
                payment = self.ca
            else:
                payment = self.vm   

            self.userexsist(ctx.author.id)  
            self.makeopen(ctx.author.id)

            embed = discord.Embed(title="{}".format(ctx.channel.name))
            embed.add_field(name=f"Price: ${price} \n{payment}\nNote: {note}",
                            value=f"Make sure you send the exact amount with the note.\nThis Order will auto-cancel in 30 mins.\nType .cancel to cancel order.\nBot takes upto 5 mins to process after payment.")
            await ctx.channel.send(embed=embed)
            await ctx.channel.send(note)

            checkifright = await checkmail(price, number)

            if checkifright:
                await ctx.author.send(f"{ctx.author.mention} Thank You! Payment recieved.")
            else:
                await ctx.channel.send(
                    f"30 mins over. Payment not Received.")
            self.makeclose(ctx.author.id)
        else:
            await ctx.channel.send("Incorrect command please recheck what you typed.")

    @tasks.loop(seconds=30)
    async def fetch_email(self):
        fetch.fetchmail()


def setup(bot):
    bot.add_cog(app(bot))