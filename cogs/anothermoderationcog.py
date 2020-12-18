"""
MIT License

Copyright (c) 2020 BobDotCom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import aiosqlite
import discord
import datetime
import asyncio
from discord.ext import tasks, commands
from humanize import precisedelta as pd
from otherscripts.helpers import create_mute_role
cog_name = "Moderation" # change this if u want


async def mute_member(self,ctx,member,time):
    user = member
    try:
        asdf = ctx.author
        f = user.top_role
        h = asdf.top_role
        if h > f or ctx.guild.owner == ctx.author and not user == ctx.author:
          if user.guild_permissions.ban_members and not ctx.guild.owner == ctx.author:
            await ctx.send("This person has to not have the ban members permission.")
            return False
        else:
          if user == ctx.author:
            await ctx.send("You can't mute yourself. -_-")
            return False
          else:
            await ctx.send("Error, this person has a higher or equal role to you")
            return False
    except:
        await ctx.send("error, please report this to the developer")
        return False
    guild = ctx.guild
    mute_role = None

    for role in guild.roles:
        if "muted" in role.name.lower():
            mute_role = role
            break
    if mute_role in user.roles:
        await ctx.send("This user is already muted.")
        return False
    else:
        if not mute_role:
            await ctx.send("This server does not have a `Muted` Role. Creating one right now.")
            await ctx.send("This may take some time.")
            mute_role = await create_mute_role(guild)

        if time is None:
            await user.add_roles(mute_role)
            await ctx.send(f"User {user} has been muted! They cannot speak.")
        else:
            await user.add_roles(mute_role)
        return True

async def unmute_member(self,guild,user):
        """Unmute a member. This will remove all roles named muted from the member
        Uses: `B.unmute <member>`"""
        if user is None:
            return print("error")
        else:
            mute_role = None

            for role in guild.roles:
                if role.name.lower() == "muted":
                    mute_role = role
                    break

            if mute_role in user.roles:
                if not mute_role:
                    mute_role = await create_mute_role(guild)

                await user.remove_roles(mute_role)

            else:
              return

async def make_user(self,ctx,member):
    guild = ctx.guild
    async with aiosqlite.connect("punishments.sql") as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("""
    INSERT INTO
      users (userid, guildid, bantime, mutetime, warncount)
    VALUES
      (?, ?, ?, ?, ?);
    """, (member.id,guild.id,0,0,0))
            await connection.commit()
           

async def mutes(self,ctx,member,time,reason):
      if not time:
          guild = ctx.guild
          async with aiosqlite.connect("punishments.sql") as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT * FROM users WHERE userid = ? AND guildid = ?", (member.id,ctx.guild.id))
                    rows = await cursor.fetchone()
          if not rows:
            await make_user(self,ctx,member)
          async with aiosqlite.conncet("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE users SET mutetime = ? WHERE userid = ? AND guildid = ?", (-1, member.id, guildid,))
                await connection.commit()
          await mute_member(self,ctx,member,time)
          if reason:
            await ctx.send(f"Reason: {reason}")

          # MUTE HERE

      else:
          guild = ctx.guild
          timelist = time.split(" ")
          oldtime = datetime.datetime.utcnow()
          week,day,hour,minute = 0,0,0,0
          if len(timelist) > 4:
            return await ctx.send("Err")
          for i in range(len(timelist)):
            test_str = timelist[i].lower()
            if "w" in test_str:
              new_str = test_str.replace('w', '')
              week += int(new_str)
            elif "d" in test_str:
              new_str = test_str.replace('d', '')
              day += int(new_str)
            elif "h" in test_str:
              new_str = test_str.replace('h', '')
              hour += int(new_str)
            elif "m" in test_str:
              new_str = test_str.replace('m', '')
              minute += int(new_str)
          NextDay_Date = oldtime + datetime.timedelta(weeks=week,days=day,hours=hour,minutes=minute)
          async with aiosqlite.connect("punishments.sql") as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT * FROM users WHERE userid = ? AND guildid = ?", (member.id,ctx.guild.id))
                    rows = await cursor.fetchone()      
          if not rows:
            await make_user(self,ctx,member)
          async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE users SET mutetime = ? WHERE userid = ? AND guildid = ?", (NextDay_Date.timestamp(), member.id, guild.id,))
                await connection.commit()
          y = await mute_member(self,ctx,member,time)
          if y:
            await ctx.send(f"Successfully muted {member} for {time}. Reason: {reason}")

class Moderation(commands.Cog, name = cog_name):
    """Mod commands testing"""

    def __init__(self, client):
        self.client = client
        self.unmute_members.start()

    @commands.Cog.listener()
    async def on_ready(self):
      create_users_table = """
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userid INTEGER,
        guildid INTEGER,
        bantime INTEGER,
        mutetime INTEGER,
        warncount INTEGER
      );
      """
      async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(create_users_table)
                await connection.commit()

    @commands.command(aliases=["strikes"])
    @commands.is_owner()
    async def warns(self,ctx,member: discord.Member,*,amount: int = 1):
      guild = ctx.guild
      async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE userid = ? AND guildid = ?", (member.id,ctx.guild.id,))
                rows = await cursor.fetchone()
      if not rows:
        await make_user(self,ctx,member)
        return await ctx.send("That would give this user less than 0 warnings")
      else:
        warncount = rows[5] + amount
      if warncount > 100:
        return await ctx.send("That would give this user less than 0 warnings")
      async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE users SET warncount = ? WHERE userid = ? AND guildid = ?", (warncount, member.id, guild.id,))
                await connection.commit()   
      await ctx.send(f"Successfully added {amount} warns to {member}, they now have {warncount} warnings in this server")

    @commands.command(aliases=["clearstrike"])
    @commands.is_owner()
    async def clearwarns(self,ctx,member: discord.Member,*,amount: int = 1):
      guild = ctx.guild
      async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE userid = ? AND guildid = ?", (member.id,ctx.guild.id,))
                rows = await cursor.fetchone()
      if not rows:
        await make_user(self,ctx,member)
        return await ctx.send("That would give this user less than 0 warnings")
      else:
        warncount = rows[5] - amount
      if warncount < 0:
        return await ctx.send("That would give this user less than 0 warnings")
      async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE users SET warncount = ? WHERE userid = ? AND guildid = ?", (warncount, member.id, guild.id,))
                await connection.commit()   
      await ctx.send(f"Successfully removed {amount} warns from {member}, they now have {warncount} warnings in this server")

    @tasks.loop(seconds=55)
    async def unmute_members(self):
        await asyncio.sleep(5)
        async with aiosqlite.connect("punishments.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE mutetime > 0")
                rows = await cursor.fetchall()
        for row in rows:
          if datetime.datetime.utcfromtimestamp(row[4]) <= datetime.datetime.utcnow():
            try:
              guild = self.client.get_guild(row[2])
              user = guild.get_member(row[1])
              await unmute_member(self,guild,user)
              async with aiosqlite.connect("punishments.sql") as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("UPDATE users SET mutetime = ? WHERE userid = ? AND guildid = ?", (0, row[1], row[2],))
                        await connection.commit()
            except:
              print("fail")

def setup(client):
    client.add_cog(Moderation(client))
