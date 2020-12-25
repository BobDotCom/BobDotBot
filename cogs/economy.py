import discord, aiosqlite, random, json, asyncio, datetime
from discord.ext import commands,tasks,menus
from extensions.crimecheck import check # idk why but my linter thinks this is an error. its not

async def use_item(ctx,item_id,amount):
    async with aiosqlite.connect('economy.db') as connection:
        async with connection.cursor() as cursor:
            if True:
                await cursor.execute(f'SELECT item{item_id} FROM users WHERE userid = ?',(ctx.author.id,))
                prev = await cursor.fetchone()
                await connection.commit()
                if prev:
                    if not prev[0]:
                        await ctx.send("You don't have any of those...")
                        return False
                    await cursor.execute("SELECT name FROM shop WHERE id = ?",(item_id,))
                    name = (await cursor.fetchone())[0]
                    prev = prev[0]
                    await connection.commit()
                    if amount <= prev:
                        await cursor.execute(f'UPDATE users SET item{item_id} = ? WHERE userid = ?',((prev - amount),ctx.author.id,))
                        await connection.commit()
                        return name
                    else:
                        await ctx.send("You don't have that many!")
                        return False
                else:
                    await ctx.send("You don't have any of those...")
                    return False
            else:
                await ctx.send("That item doesnt exist!")
                return False

class LeaderboardMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=5)

    async def format_page(self, menu, entries):
        embed = discord.Embed(title='🏆 Top 10 users 🏆',description='Sorted by the total of wallet and bank balance combined')
        place = 0

        for row in entries:
            place += 1
            user = row[0]
            embed.add_field(name=f'{user}',value=f"**Bank:** {row[1]}\n**Wallet:** {row[2]}\n**Total:** {row[1] + row[2]}",inline=False)
        return embed
    
class InventoryMenu(menus.ListPageSource):
    def __init__(self, data, user):
        self.user = user
        super().__init__(data, per_page=6)

    async def format_page(self, menu, entries):
        embed = discord.Embed(title=f"{self.user.name}'s Inventory")

        for row in entries:
            if row[2] and row[2] != 0:
                embed.add_field(name=row[1],value=f"**Amount:** {row[2]}\n**ID:** {row[0]}")
        return embed

class Economy(commands.Cog, name = "Economy"):
    """Economy Commands"""

    def __init__(self, client):
        self.client = client
        self.currency_name = "blob"
        self.work_payment = [500,900]
        self.crime_payment = [1000,5000]
        self.beg_amount = [50,200]

    @commands.Cog.listener()
    async def on_ready(self):
        # Use the below line to debug if the cog stops working
        #print('Economy Cog is active on startup')
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS users (userid INTEGER, bank INTEGER, wallet INTEGER);")
                await cursor.execute("CREATE TABLE IF NOT EXISTS shop (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price INTEGER, available BOOL);")
                await connection.commit()

    @commands.check
    async def pre_crime_check(self):
        return await check(self) # formatted as such to get rid of linter errors
        
    @commands.command(aliases=['bal'])
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def balance(self,ctx,member:discord.Member=None):
        member = member or ctx.author
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE userid = ?",(member.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(member.id,0,0))
                    await cursor.execute("SELECT * FROM users WHERE userid = ?",(member.id,))
                    rows = await cursor.fetchone()
                await connection.commit()
                embed = discord.Embed(title=f"{member.name}'s Balance",description=f"**Wallet**: {rows[2]}\n**Bank**: {rows[1]}")
                await ctx.send(embed=embed)
        
    @commands.command()
    @commands.is_owner()
    async def edituser(self,ctx,area,member: discord.Member,amount):
        amount = int(amount)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT {area} FROM users WHERE userid = ?",(member.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(member.id,0,0,))
                    await cursor.execute(f"UPDATE users SET {area} = ? WHERE userid = ?",(amount,member.id,))
                    await ctx.send(f"previous: 0\nnew: {amount}")
                else:
                    await cursor.execute(f"UPDATE users SET {area} = ? WHERE userid = ?",(amount,member.id,))
                    await ctx.send(f"previous: {rows[0]}\nnew: {amount}")
                await connection.commit()

    @commands.command()
    @commands.is_owner()
    async def workquote(self,ctx,what,*,quote):
        with open("work.json",'r') as f:
            data = json.load(f)
        if what == 'add':
            data['quotes'].append(quote)
        elif what == 'remove':
            data['quotes'].remove(quote)
        else:
            await ctx.send("remember to specify add or remove")
        with open("work.json",'w') as f:
            json.dump(data,f,indent=4)
        await ctx.send("Success")

    @commands.command()
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,3600,commands.BucketType.user)
    async def work(self,ctx):
        currency = self.currency_name
        with open("work.json",'r') as f:
            data = json.load(f)
        message = random.choice(data['quotes'])
        amount = random.randint(self.work_payment[0],self.work_payment[1])
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,amount,))
                else:
                    await cursor.execute("UPDATE users SET wallet = ? WHERE userid = ?",(amount + rows[0],ctx.author.id,))
                await connection.commit()
        money = str(amount) + ' ' + currency
        embed = discord.Embed(title="Work",description=message.replace('%',money),color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(aliases=['dep'])
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def deposit(self,ctx,amount):
        if not amount == 'all':
            amount = int(amount)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0,''))
                else:
                    if not amount == 'all':
                        if amount > rows[1]:
                            await ctx.send("You dont have that much")
                        elif amount <= 0:
                            await ctx.send("That is too low")
                        else:
                            await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] - amount,rows[0] + amount,ctx.author.id,))
                            await ctx.send(f"Successfully deposited {amount} into your bank")
                    else:
                        await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(0,rows[0] + rows[1],ctx.author.id,))
                        await ctx.send(f"Successfully deposited {rows[1]} into your bank")
                    await connection.commit()
        
    @commands.command(aliases=['with'])
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def withdraw(self,ctx,amount):
        if not amount == 'all':
            amount = int(amount)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0,))
                else:
                    if not amount == 'all':
                        if amount > rows[0]:
                            await ctx.send("You dont have that much")
                        elif amount <= 0:
                            await ctx.send("That is too low")
                        else:
                            await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + amount,rows[0] - amount,ctx.author.id,))
                            await ctx.send(f"Successfully withdrew {amount} from your bank")
                    else:
                        await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + rows[0],0,ctx.author.id,))
                        await ctx.send(f"Successfully withdrew {rows[0]} from your bank")
                await connection.commit()
        
    @commands.command()
    @commands.max_concurrency(1,commands.BucketType.default)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def bet(self,ctx,amount,*,member:discord.Member):
        amount = int(amount)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                row1 = await cursor.fetchone()
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(member.id,))
                row2 = await cursor.fetchone()
                await connection.commit()
        if not (row1 and row2):
            return await ctx.send("Either you or your opponent doesnt have an account!")
        else:
            if not (row1[0] >= amount and row2[0] >= amount):
                return await ctx.send("Either you or your opponent doesn't have that much money")
        await ctx.send(f"Hey, {member.mention}. `{ctx.author}` invited you to bet {amount}. To accept, type `yes` within 1 minute.")
        def check(m):
            return m.content == 'yes' and m.channel == ctx.channel and m.author == member
        try:
            await self.client.wait_for('message', check=check,timeout=60)
        except:
            return await ctx.send("Time is up!")
        await ctx.send(f"Ok, the rules are simple. I will take {amount} from each of you, and the winner will get {amount * 2}. The loser will get nothing.")
        await asyncio.sleep(3)
        msg = await ctx.send("3")
        await asyncio.sleep(1)
        await msg.edit(content="2")
        await asyncio.sleep(1)
        await msg.edit(content="1")
        await asyncio.sleep(1)
        both = random.sample([ctx.author,member],k=2)
        winner = both[0]
        loser = both[1]
        await msg.delete()
        await ctx.send(f'{winner.mention} Won!')
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(winner.id,))
                row1 = await cursor.fetchone()
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(loser.id,))
                row2 = await cursor.fetchone()
                await cursor.execute("UPDATE users SET wallet = ? WHERE userid = ?",(row1[0] + amount,winner.id,))
                await cursor.execute("UPDATE users SET wallet = ? WHERE userid = ?",(row2[0] - amount,loser.id,))
                await connection.commit()

    @commands.group(invoke_without_command=True)
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def shop(self, ctx):
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM shop WHERE available = ?",(True,))
                rows = await cursor.fetchall()
        embed = discord.Embed(title="Shop",description="Use the buy command to buy an item by its id")
        for row in rows:
            embed.add_field(name=row[1],value=f"**Cost**: {row[2]} \n**ID**: {row[0]}")
        await ctx.send(embed=embed)

    @shop.command()
    @commands.is_owner()
    async def add(self,ctx,name,price):
        price = int(price)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO shop (name, price, available) VALUES (?,?,?)",(name,price,True,))
                await cursor.execute('SELECT id FROM shop')
                rows = await cursor.fetchall()
                number = rows[-1][0]
                await cursor.execute(f'ALTER TABLE users ADD COLUMN item{number} INTEGER;')
                await connection.commit()
        await ctx.send(f"Successfully added `{name}` to the shop at the price of `{price}`")

    @shop.command()
    @commands.is_owner()
    async def remove(self,ctx,item_id):
        item_id = int(item_id)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM shop WHERE id = ? AND available = ?",(item_id,True,))
                rows = await cursor.fetchone()
                if rows:
                    await ctx.send(f"Successfully removed item `{item_id}` from the shop")
                else:
                    await ctx.send("That item doesnt exist")
                await cursor.execute("UPDATE shop SET available = ? WHERE id = ?",(False,item_id,))
                await connection.commit()

    @shop.command()
    @commands.is_owner()
    async def enable(self,ctx,item_id):
        item_id = int(item_id)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM shop WHERE id = ? AND available = ?",(item_id,False,))
                rows = await cursor.fetchone()
                if rows:
                    await ctx.send(f"Successfully enabled item `{item_id}` in the shop")
                else:
                    await ctx.send("That item doesnt exist or is enabled")
                await cursor.execute("UPDATE shop SET available = ? WHERE id = ?",(True,item_id,))
                await connection.commit()

    @shop.command()
    @commands.is_owner()
    async def edit(self,ctx,item_id,price):
        item_id = int(item_id)
        price = int(price)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE shop SET price = ? WHERE id = ?",(price,item_id,))
                await connection.commit()
        await ctx.send(f"Successfully changed price of item `{item_id}` to `{price}`")

    @shop.command()
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def buy(self,ctx,item_id,amount = 1):
        item_id,amount = int(item_id),int(amount)
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT name, price FROM shop WHERE id = ? AND available = ?",(item_id,True,))
                row = await cursor.fetchone()
                await cursor.execute(f'SELECT item{item_id} FROM users WHERE userid = {ctx.author.id}')
                row1 = await cursor.fetchone()
                await connection.commit()
        price,name = row[1] * amount,row[0]
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                row = await cursor.fetchone()
                if row[0] >= price:
                    if row1[0]:
                        await cursor.execute(f"UPDATE users SET wallet = ?,item{item_id} = ? WHERE userid = ?",(row[0] - price,row1[0] + amount, ctx.author.id,))
                        await connection.commit()
                        await ctx.send(f"Successfully purchased {amount} {name}")
                    else:
                        await cursor.execute(f"UPDATE users SET wallet = ?,item{item_id} = ? WHERE userid = ?",(row[0] - price,amount, ctx.author.id,))
                        await connection.commit()
                        await ctx.send(f"Successfully purchased {amount} {name}")
                else:
                    await ctx.send("You don't have that much money")
        
    @commands.command()
    @pre_crime_check
    @commands.cooldown(1,7200,commands.BucketType.user)
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    async def crime(self,ctx):
        both = random.choice([['succeed',random.randint(self.crime_payment[0],self.crime_payment[1])],['fail',0 - random.randint(self.crime_payment[0],self.crime_payment[1])]])
        amount = both[1]
        outcome = both[0]
        if outcome == 'fail':
            color = discord.Color.red()
        else:
            color = discord.Color.green()
        currency = self.currency_name
        with open("crime.json",'r') as f:
            data = json.load(f)
        message = random.choice(data[outcome])
        async with aiosqlite.connect("economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,amount,))
                else:
                    await cursor.execute("UPDATE users SET wallet = ? WHERE userid = ?",(amount + rows[0],ctx.author.id,))
                await connection.commit()
        money = str(abs(amount)) + ' ' + currency
        embed = discord.Embed(title="Crime",description=message.replace('%',money),color=color)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def crimefail(self,ctx,what,*,quote):
        with open("crime.json",'r') as f:
            data = json.load(f)
        if what == 'add':
            data['fail'].append(quote)
        elif what == 'remove':
            data['fail'].remove(quote)
        else:
            await ctx.send("remember to specify add or remove")
        with open("crime.json",'w') as f:
            json.dump(data,f,indent=4)
        await ctx.send("Success")

    @commands.command()
    @commands.is_owner()
    async def crimesucceed(self,ctx,what,*,quote):
        with open("crime.json",'r') as f:
            data = json.load(f)
        if what == 'add':
            data['succeed'].append(quote)
        elif what == 'remove':
            data['succeed'].remove(quote)
        else:
            await ctx.send("remember to specify add or remove")
        with open("crime.json",'w') as f:
            json.dump(data,f,indent=4)
        await ctx.send("Success")

    @commands.command(aliases=['lb'])
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def leaderboard(self,ctx):
        async with aiosqlite.connect('economy.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT * FROM users')
                rows = await cursor.fetchall()
                await connection.commit()

        top = sorted(rows,reverse=True, key=lambda x: x[1] + x[2])[:10]
        top = [list(x) for x in top]
        place = 0

        for row in top:
            if place == 0:
                pl = f"🥇 "
            elif place == 1:
                pl = f"🥈 "
            elif place == 2:
                pl = f"🥉 "
            else:
                pl = ''
            top[place][0] = f'{pl}{place+1}. {await self.client.fetch_user(row[0])}' or "User not found"
            place += 1

        pages = menus.MenuPages(source=LeaderboardMenu(top), delete_message_after=True)
        await pages.start(ctx)

    @commands.command(aliases=['inv'])
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def inventory(self,ctx,user: discord.Member = None):
        user = user or ctx.author
        async with aiosqlite.connect('economy.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT id,name FROM shop')
                rows1 = await cursor.fetchall()
                amount = rows1[-1][0]
                rows = ','.join([f'item{x + 1}' for x in range(amount)])
                await cursor.execute(f'SELECT {rows} FROM users WHERE userid = ?',(user.id,))
                row = await cursor.fetchone()
                await connection.commit()
            new_row = []
            for item in rows1:
                new = list(item)
                new.append(row[item[0] - 1])
                new_row.append(tuple(new))
            pages = menus.MenuPages(source=InventoryMenu(new_row,user), delete_message_after=True)
            await pages.start(ctx)

    @commands.command()
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,60,commands.BucketType.user)
    async def use(self,ctx,item_id,amount=1):
        try:
            item_id, amount = int(item_id), int(amount)
        except:
            return await ctx.send("Both the item id and amount have to be numbers!")
        name = await use_item(ctx,item_id,amount)
        if name:
            if item_id == 1:
                earned = random.randint((amount * 100) / 2,(amount * 100) * 1.5)
                await ctx.send(f"You used {amount} {name}. You got really high but somehow managed to get {earned}")
                async with aiosqlite.connect('economy.db') as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                        prev = (await cursor.fetchone())[0]
                        await cursor.execute('UPDATE users SET wallet = ? WHERE userid = ?',((prev + earned),ctx.author.id,))
                        await connection.commit()
            elif item_id == 2:
                await ctx.send(f"Ok {ctx.author.mention}, who do you want to shoot? You have 10 seconds to reply")
                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author
                try:
                    msg = await self.client.wait_for('message', check=check,timeout=10)
                except asyncio.TimeoutError:
                    return await ctx.send("Time is up! You missed and hit a tree.")
                try:
                    member = await commands.MemberConverter().convert(ctx,msg.content)
                except discord.ext.commands.errors.MemberNotFound as e:
                    await ctx.send(e + " You missed and hit a tree.")
                succeed = random.choice([True,False,False,False])
                if succeed:
                    await member.send(f"You were shot by {ctx.author}! They took all the money in your wallet")
                    await ctx.send('You shot them dead and took all the money in their wallet')
                    async with aiosqlite.connect('economy.db') as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                            prev = (await cursor.fetchone())[0]
                            await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(member.id,))
                            new = (await cursor.fetchone())[0]
                            await cursor.execute('UPDATE users SET wallet = ? WHERE userid = ?',((prev + new),ctx.author.id,))
                            await cursor.execute('UPDATE users SET wallet = ? WHERE userid = ?',(0,member.id,))
                            await connection.commit()
                else:
                    await ctx.send("You missed and hit your mom")
            else:
                await ctx.send(f"You used {amount} {name}. It doesn't really do anything yet though so rip you lmao.")

    @commands.command()
    @commands.max_concurrency(1,commands.BucketType.default,wait=True)
    @commands.cooldown(1,900,commands.BucketType.user)
    async def beg(self,ctx):
        chance = random.choice([True,False])
        with open("beg.json",'r') as f:
            data = json.load(f)

        if chance:
            title = "Success!"
            amount = random.randint(self.beg_amount[0],self.beg_amount[1])
            money = str(amount) + ' ' + self.currency_name
            message = random.choice(data['succeed']).replace('%',money)
            color = discord.Color.green()
            async with aiosqlite.connect('economy.db') as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
                    prev = (await cursor.fetchone())[0]
                    await cursor.execute('UPDATE users SET wallet = ? WHERE userid = ?',((prev + amount),ctx.author.id,))
                    await connection.commit()
        else:
            title = "Dammit!"
            message = random.choice(data['fail'])
            color = discord.Color.red()
        embed = discord.Embed(title=title,description=message,color=color)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def begfail(self,ctx,what,*,quote):
        with open("beg.json",'r') as f:
            data = json.load(f)
        if what == 'add':
            data['fail'].append(quote)
        elif what == 'remove':
            data['fail'].remove(quote)
        else:
            await ctx.send("remember to specify add or remove")
        with open("beg.json",'w') as f:
            json.dump(data,f,indent=4)
        await ctx.send("Success")

    @commands.command()
    @commands.is_owner()
    async def begsucceed(self,ctx,what,*,quote):
        with open("beg.json",'r') as f:
            data = json.load(f)
        if what == 'add':
            data['succeed'].append(quote)
        elif what == 'remove':
            data['succeed'].remove(quote)
        else:
            await ctx.send("remember to specify add or remove")
        with open("beg.json",'w') as f:
            json.dump(data,f,indent=4)
        await ctx.send("Success")
                
    async def cog_check(self, ctx):
        return True # await self.client.is_owner(ctx.author)
        # if you want every single command to be checked

def setup(client):
    client.add_cog(Economy(client))