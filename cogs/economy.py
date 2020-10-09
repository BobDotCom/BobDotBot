import ast
import os 
import discord
import asyncio
import json
import datetime
import jishaku
from datetime import datetime
from discord.ext.commands import cog
from discord.ext.commands import command
from discord.ext import commands
from discord.ext.commands import Bot
import time
import discord.utils
from discord.ext import tasks, commands
import random



class economy(commands.Cog, name = "Economy"):
    """Economy commands"""
    def __init__(self, client):
        self.client = client
    @commands.command(aliases=['bal'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def balance(self,ctx,*,member: discord.Member = None):
        """See how much money you, or someone else has
        Uses: `B.balance [member]`
        Note: Arguments in brackets[] are optional"""
        member = ctx.author if not member else member
        await self.open_account(member)
        user = member
        users = await self.get_bank_data()

        wallet_amt = users[str(user.id)]["wallet"]
        bank_amt = users[str(user.id)]["bank"]
 
        em = discord.Embed(title = f"{member.name}'s balance",color = discord.Color.dark_blue())
        em.add_field(name = "Wallet", value = wallet_amt)
        em.add_field(name = "Bank", value = bank_amt)
        await ctx.send(embed = em)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def allin(self,ctx):
      """Bet all of your money in a coin toss
      Uses: `B.allin`"""
      async with ctx.channel.typing():
        emoji = self.client.get_emoji(759047006290313237) 
        msg = await ctx.send(f"{emoji}")
        answer = random.randrange(2)
        await asyncio.sleep(2)
        await msg.delete()
        user = ctx.author
        users = await self.get_bank_data()
        wallet_amt = users[str(user.id)]["wallet"]

        if answer == 1:
            answer = 'heads'
        elif answer == 0:
            answer = 'tails'
        if answer is str("heads"):
              embedVar = discord.Embed(title=f"The coin landed on... {answer}", description=f"You won {wallet_amt}", color = discord.Color.dark_blue())
              await self.update_bank(ctx.author,1*wallet_amt)

        else:
              await self.update_bank(ctx.author,-1*wallet_amt)
              embedVar = discord.Embed(title=f"The coin landed on... {answer}", description=f"You lost {wallet_amt}", color = discord.Color.dark_blue())
        await ctx.send(embed = embedVar)
      

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def beg(self,ctx):
        """Beg peope for money
        Uses: `B.beg`"""
        await self.open_account(ctx.author)
        user = ctx.author
        users = await self.get_bank_data()

        earnings =  random.randrange(101)

        await ctx.send(f"Someone gave you {earnings} coins!!")

        users[str(user.id)]["wallet"] += earnings
    
        with open("mainbank.json","w") as f:
            json.dump(users,f)

    #@commands.command()
    #@commands.cooldown(1, 86400, commands.BucketType.user)
    #async def daily(self,ctx):
        #"""use this every 24 hours to get a bonus"""
        #await self.open_account(ctx.author)
        #user = ctx.author
        #users = await self.get_bank_data()

        #earnings = 1000

        #await ctx.send(f"you got {earnings} come back in 24 hours to get more")

        #users[str(user.id)]["wallet"] += earnings
    
        #with open("mainbank.json","w") as f:
            #json.dump(users,f)

    #@commands.command()
    #@commands.cooldown(1, 604800, commands.BucketType.user)
    #async def weekly(self,ctx):
        ##"""use this every week to get a bonus"""
        ##await self.open_account(ctx.author)
        ##user = ctx.author
        ##users = await self.get_bank_data()

        ##earnings = 10000

        ##await ctx.send(f"you got {earnings} come back in 1 week to get more")

        ##users[str(user.id)]["wallet"] += earnings
    
        ##with open("mainbank.json","w") as f:
            ##json.dump(users,f)


    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self,ctx):
        """Go to work. Get a job. Leave your parents basement. Yes, I mean you. Lazy.
        Uses: `B.work`"""
        await self.open_account(ctx.author)
        user = ctx.author
        users = await self.get_bank_data()

        earnings =  random.randrange(2001)

        await ctx.send(f"You worked for an hour and somehow managed to get {earnings} coins. bruh")

        users[str(user.id)]["wallet"] += earnings
    
        with open("mainbank.json","w") as f:
            json.dump(users,f)


    @commands.command(aliases=['with'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def withdraw(self,ctx,amount = None):
        """Withdraw money from your bank, putting it into your wallet to use
        Uses: `B.withdraw <amount>`"""
        await self.open_account(ctx.author)
        if amount == None:
            await ctx.send("Please enter the amount")
            return

        bal = await self.update_bank(ctx.author)
    
        amount = int(amount)
        if amount>bal[1]:
            await ctx.send("You dont have that much money")
            return
        if amount<0:
            await ctx.send("Bruh")
            return
    
        await self.update_bank(ctx.author,amount)
        await self.update_bank(ctx.author,-1*amount,"bank")
        await ctx.send(f"You withdrew {amount} coins")
    
    @commands.command(aliases=['dep','depo'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def deposit(self,ctx,amount = None):
        """Keep your money safe in the bank
        Uses: `B.deposit <amount>`"""
        await self.open_account(ctx.author)
        if amount == None:
            await ctx.send("Please enter an amount")
            return

        bal = await self.update_bank(ctx.author)
    
        amount = int(amount)
        if amount>bal[0]:
            await ctx.send("You dont have that much money")
            return
        if amount<0:
            await ctx.send("Bruh")
            return
    
        await self.update_bank(ctx.author,-1*amount)
        await self.update_bank(ctx.author,amount,"bank")
        await ctx.send(f"You deposited {amount} coins")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def give(self,ctx,member:discord.Member,amount = None):
        """Donate to the poor
        Uses: `B.donate <member> <amount>`"""
        await self.open_account(ctx.author)
        await self.open_account(member)
        if amount == None:
            await ctx.send("Please enter an amount")
            return

        bal = await self.update_bank(ctx.author)
    
        amount = int(amount)
        if amount>bal[1]:
            await ctx.send("You dont have that much money")
            return
        if amount<0:
            await ctx.send("Bruh")
            return
    
        await self.update_bank(ctx.author,-1*amount,"bank")
        await self.update_bank(member,amount,"bank")
        await ctx.send(f"You gave them {amount} coins. You *might* go to heaven now.")

    @commands.command(aliases = ["lb"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def leaderboard(self,ctx,x = 10):
        """Check the top players and their balance
        Uses: `B.leaderboard`"""
        #users = await self.get_bank_data()
        #leader_board = {}
        #total = []
        #asdf = []
        #for user in users:
            #total_amount = users[user]["wallet"] + users[user]["bank"]
            #leader_board[total_amount] = int(user)
            #total.append(total_amount)
            #asdf.append(int(user))
        #total = sorted(total,reverse=True)    

        #em = discord.Embed(title = f"Top {x} Richest People" , description = "Leaderboard takes both bank and wallet balance",color = discord.Color.dark_blue())
        #index = 1
        #for amt in total:
            #await _ctx.send
            #id_ = asdf[index]
            #member = self.client.get_user(id_)
            #name = member.name
            #em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
            #if index == x:
                #break
            #else:
                #index += 1

        await ctx.send("this command is currently disabled")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slots(self,ctx,amount = None):
        """Try your luck. Or dont.
        Uses: `B.slots <amount>`"""
        await self.open_account(ctx.author)
        if amount == None:
            await ctx.send("Please enter an amount")
            return

        bal = await self.update_bank(ctx.author)

        amount = int(amount)
        if amount>bal[0]:
            await ctx.send("You dont have that much money")
            return
        if amount<0:
            await ctx.send("Bruh")
            return
        final = []
        for I in range(3):
              a = random.choice(["X","0","Q"])
              chance = random.choice(["a","b"])
              final.append(a)
            
              
        
        if chance is str("a"):
              done = False
              if not final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
                while done is False:
                  final = []
                  for I in range(3):
                    a = random.choice(["X","0","Q"])
                    final.append(a)
                  if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
                    done = True
              else:
                win = final
              await self.update_bank(ctx.author,1*amount)
              await ctx.send(str(final))
              await ctx.send(f"You won")

        else:
              done = False
              if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
                while done is False:
                  final = []
                  for I in range(3):
                    a = random.choice(["X","0","Q"])
                    final.append(a)
                  if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
                    done = False
                  else:
                    done = True
              else:
                lose = final
              await self.update_bank(ctx.author,-1*amount)
              await ctx.send(str(final))
              await ctx.send("You lost")

    @commands.command()
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def rob(self,ctx,member:discord.Member):
        """Rob someone. You're a theif now
        Uses: `B.rob <member>`"""
        await self.open_account(ctx.author)
        await self.open_account(member)

        bal = await self.update_bank(member)
    
        if bal[0]<150:
            await ctx.send("No robing poor people :angry:")
            return
    
        earnings = random.randrange(0, bal[0])

        final = []
        for I in range(3):
            a = random.choice(["X","0","Q"])

            final.append(a)

        if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
            await self.update_bank(ctx.author,earnings)
            await self.update_bank(member,-1*earnings)
            await ctx.send(f"You robbed {earnings} coins how rude")
        else:
            await self.update_bank(ctx.author,-1*earnings)
            await self.update_bank(member,earnings)
            await ctx.send(f"You were caught and had to pay the person {earnings} coins")

    mainshop = [{"name":"Watch","price":4000,"description":"buy yourself a expensive watch *RIGHT NOW THIS ITEM HAS NO USE*"},
            {"name":"Laptop","price":20000,"description":"use this overpriced laptop *RIGHT NOW THIS ITEM HAS NO USE"},
            {"name":"PC","price":500000,"description":"use this to flex on people *RIGHT NOW THIS ITEM HAS NO USE"}]


    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def shop(self,ctx):
        """See whats in the shop
        Uses: `B.shop`"""
        em = discord.Embed(title = "Shop", color = discord.Color.dark_blue())

        for item in self.mainshop:
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            em.add_field(name = name, value = f"${price} | {desc}")

        await ctx.send(embed = em)



    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def buy(self,ctx,item,amount = 1):
        """Buy something from the shop
        Uses: `B.buy <item> [amount]`
        Note: Amount(in brackets[]) defaults to 1 if not set"""
        await self.open_account(ctx.author)

        res = await self.buy_this(ctx.author,item,amount)

        if not res[0]:
            if res[1]==1:
                await ctx.send("That Object isn't there!")
                return
            if res[1]==2:
                await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
                return


        await ctx.send(f"You just bought {amount} {item}")


    @commands.command(aliases=["inv"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def inventory(self,ctx):
        """Check your inventory
        Uses: `B.inventory`"""
        await self.open_account(ctx.author)
        user = ctx.author
        users = await self.get_bank_data()

        try:
            bag = users[str(user.id)]["bag"]
        except:
            bag = []


        em = discord.Embed(title = "Bag", color = discord.Color.dark_blue() )
        for item in bag:
            name = item["item"]
            amount = item["amount"]

            em.add_field(name = name, value = amount)    

        await ctx.send(embed = em)    
    async def buy_this(self,user,item_name,amount):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                price = item["price"]
                break

        if name_ == None:
            return [False,1]

        cost = price*amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        if bal[0]<cost:
            return [False,2]


        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt + amount
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index+=1 
            if t == None:
                obj = {"item":item_name , "amount" : amount}
                users[str(user.id)]["bag"].append(obj)
        except:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"] = [obj]        

        with open("mainbank.json","w") as f:
            json.dump(users,f)

        await self.update_bank(user,cost*-1,"wallet")

        return [True,"Worked"]


    
    async def open_account(self,user):
    
        users = await self.get_bank_data()
        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["wallet"] = 0
            users[str(user.id)]["bank"] = 0
            users[str(user.id)]["name"] = user.name
        with open("mainbank.json","w") as f:
            json.dump(users,f)
        return True

    async def get_bank_data(self):
        with open("mainbank.json","r+") as f:
            users = json.load(f)

        return users

    async def update_bank(self,user,change = 0, mode = "wallet"):
        users = await self.get_bank_data()

        users[str(user.id)][mode] +=change

        with open("mainbank.json","w") as f:
            json.dump(users,f)
        
        
        bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
        return bal

def setup(client):
    client.add_cog(economy(client))
