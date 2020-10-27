import aiosqlite
import discord
import pytz
from datetime import datetime
from discord.ext import commands

class Timezone(commands.Cog, name = "Time"):
    """Time commands so ppl can stalk you"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready():
      print("TimeZoneCog is active")
      create_users_table = """
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        userid INTEGER,
        timezone TEXT
      );
      """
      db = await aiosqlite.connect("timezone.sql")

      cursor = await db.execute(create_users_table)
      await cursor.close()
      await db.close()

    @commands.command()
    async def settime(self,ctx,timezone):
      member = ctx.author
      timezone1 = timezone
      timezone5 = timezone1.lower()
      splitter = timezone5[3]
      contents = timezone5.split(splitter)
      splitter = "+" if splitter == "-" else "-"
      timezone5 = contents[0] + splitter + contents[1]
      if timezone5[:3] in ["gmt","utc"] and timezone5[3] in ["-", "+"] and contents[1].isdigit():
        timezone5 = "GMT" + timezone5[3:]
        timezone1 = "Etc/" + timezone5
      db = await aiosqlite.connect("timezone.sql")
      cursor = await db.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
      rows = await cursor.fetchone()
      await cursor.close()
      await db.close()
      try:
        timezone2 = pytz.timezone(rows[3])
      except:
        timezone2 = None
      if not timezone2:
        try:
          timezone2 = pytz.timezone(timezone1)
          timezone2 = datetime.now(timezone2)
          timezone2 = timezone2.strftime('%Y-%m-%d %H:%M:%S %Z %z')
          embed1 = discord.Embed(title="Setting time to " + timezone2,timestamp=ctx.message.created_at)
          msg = await ctx.send(embed=embed1)
          db = await aiosqlite.connect("timezone.sql")

          cursor = await db.execute("""
          INSERT INTO
            users (name, userid, timezone)
          VALUES
            (?, ?, ?);
          """, (member.name,member.id,timezone1,))
          await db.commit()
          await cursor.close()
          await db.close()
          embed1 = discord.Embed(title="Successfully set time to " + timezone2,timestamp=ctx.message.created_at,color=discord.Color.green())
          await msg.edit(embed=embed1)
        except:
          embed = discord.Embed(title="Error",description="Invalid time zone. See [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for valid time zones. You can also use GMT/UTC offset by typing `gmt+0`, replaced with your GMT offset",color=discord.Color.red(),timestamp=ctx.message.created_at)
          try:
                await msg.edit(embed=embed)
          except:
            await ctx.send(embed=embed)
      else:
        try:
          timezone2 = pytz.timezone(timezone1)
          timezone2 = datetime.now(timezone2)
          timezone2 = timezone2.strftime('%Y-%m-%d %H:%M:%S %Z %z')
          embed1 = discord.Embed(title="Setting time to " + timezone2,timestamp=ctx.message.created_at)
          msg = await ctx.send(embed=embed1)
          db = await aiosqlite.connect("timezone.sql")
          member = ctx.author if not member else member
          cursor = await db.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
          rows = await cursor.fetchone()
          await cursor.close()
          cursor = await db.execute("UPDATE users SET timezone = ? WHERE userid = ?", (timezone1, member.id,))
          await db.commit()
          await cursor.close()
          await db.close()
          embed1 = discord.Embed(title="Successfully set time to " + timezone2,timestamp=ctx.message.created_at,color=discord.Color.green())
          await msg.edit(embed=embed1)
        except:
          embed = discord.Embed(title="Error",description="Invalid time zone. See [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for valid time zones. You can also use GMT/UTC offset by typing `gmt+0`, replaced with your GMT offset",color=discord.Color.red(),timestamp=ctx.message.created_at)
          try:
                await msg.edit(embed=embed)
          except:
            await ctx.send(embed=embed)
    @commands.command()
    @commands.is_owner()
    async def settimefor(self,ctx,member: discord.Member,timezone1):
      timezone5 = timezone1.lower()
      splitter = timezone5[3]
      contents = timezone5.split(splitter)
      splitter = "+" if splitter == "-" else "-"
      timezone5 = contents[0] + splitter + contents[1]
      if timezone5[:3] in ["gmt","utc"] and timezone5[3] in ["-", "+"] and contents[1].isdigit():
        timezone5 = "GMT" + timezone5[3:]
        timezone1 = "Etc/" + timezone5
      else:
        timezone1 = "fuck"
      db = await aiosqlite.connect("timezone.sql")
      cursor = await db.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
      rows = await cursor.fetchone()
      await cursor.close()
      await db.close()
      try:
        timezone2 = pytz.timezone(rows[3])
      except:
        timezone2 = None
      if not timezone2:
        try:
          timezone2 = pytz.timezone(timezone1)
          timezone2 = datetime.now(timezone2)
          timezone2 = timezone2.strftime('%Y-%m-%d %H:%M:%S %Z %z')
          embed1 = discord.Embed(title="Setting time to " + timezone2,timestamp=ctx.message.created_at)
          msg = await ctx.send(embed=embed1)
          db = await aiosqlite.connect("timezone.sql")

          cursor = await db.execute("""
          INSERT INTO
            users (name, userid, timezone)
          VALUES
            (?, ?, ?);
          """, (member.name,member.id,timezone1,))
          await db.commit()
          await cursor.close()
          await db.close()
          embed1 = discord.Embed(title="Successfully set time to " + timezone2,timestamp=ctx.message.created_at,color=discord.Color.green())
          await msg.edit(embed=embed1)
        except:
          embed = discord.Embed(title="Error",description="Invalid time zone. See [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for valid time zones. You can also use GMT/UTC offset by typing `gmt+0`, replaced with your GMT offset",color=discord.Color.red(),timestamp=ctx.message.created_at)
          try:
                await msg.edit(embed=embed)
          except:
            await ctx.send(embed=embed)
      else:
        try:
          timezone2 = pytz.timezone(timezone1)
          timezone2 = datetime.now(timezone2)
          timezone2 = timezone2.strftime('%Y-%m-%d %H:%M:%S %Z %z')
          embed1 = discord.Embed(title="Setting time to " + timezone2,timestamp=ctx.message.created_at)
          msg = await ctx.send(embed=embed1)
          db = await aiosqlite.connect("timezone.sql")
          member = ctx.author if not member else member
          cursor = await db.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
          rows = await cursor.fetchone()
          await cursor.close()
          cursor = await db.execute("UPDATE users SET timezone = ? WHERE userid = ?", (timezone1, member.id,))
          await db.commit()
          await cursor.close()
          await db.close()
          embed1 = discord.Embed(title="Successfully set time to " + timezone2,timestamp=ctx.message.created_at,color=discord.Color.green())
          await msg.edit(embed=embed1)
        except:
          embed = discord.Embed(title="Error",description="Invalid time zone. See [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for valid time zones. You can also use GMT/UTC offset by typing `gmt+0`, replaced with your GMT offset",color=discord.Color.red(),timestamp=ctx.message.created_at)
          try:
                await msg.edit(embed=embed)
          except:
            await ctx.send(embed=embed)
    @commands.command()
    @commands.is_owner()
    async def newjob(self,ctx,member: discord.Member,job,amt = 1):
      jobs = None
      if job == "wc":
        jobs = "wcdone"
      elif job == "df":
        jobs = "dfdone"
      elif job == "fb":
        jobs = "fbdone"
      if not jobs:
        return await ctx.send("Not a job!")
      db = await aiosqlite.connect("blockcorp.sql")
      member = ctx.author if not member else member
      select_users = f"SELECT {jobs} FROM workers WHERE userid = {member.id}"
      cursor = await db.execute(select_users)
      rows = await cursor.fetchone()
      await cursor.close()
      update_post_description = f"UPDATE workers SET {jobs} = {rows[0] + amt} WHERE userid = {member.id}"
      cursor = await db.execute(update_post_description)
      await db.commit()
      await cursor.close()
      await db.close()
      await ctx.send("success")
    @commands.command()
    async def gettime(self,ctx,member: discord.Member = None):
        try:
            member = ctx.author if not member else member
            db = await aiosqlite.connect("timezone.sql")
            cursor = await db.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
            rows = await cursor.fetchone()
            await cursor.close()
            await db.close()
            timezone2 = pytz.timezone(rows[3])
            timezone2 = datetime.now(timezone2)
            currentdate = timezone2.strftime('%Y-%m-%d %H:%M:%S %Z %z')
            currentdate = timezone2.strftime('%Y-%m-%d')
            currenttime = timezone2.strftime("%H:%M:%S")
            currentzone = timezone2.strftime("%Z(UTC%z)")
            tzvar = rows[3]
            try:
                splitter = tzvar[7]
                if tzvar[:7].lower() == "etc/gmt":
                    asdf = tzvar.split(splitter)
                    splitter = "+" if splitter == "-" else "-"
                    tzvar = asdf[0] + splitter + asdf[1]
            except:
                pass
            embed = discord.Embed(title=f"Timezone details for: {member}",timestamp=ctx.message.created_at)
            embed.add_field(name="Timezone",value=f'"{tzvar}" {currentzone}')
            embed.add_field(name="Their current date",value=currentdate)
            embed.add_field(name="Their current time",value=currenttime)
            await ctx.send(embed=embed)
        except:
          embed = discord.Embed(title="Error",description="That user has not set their time yet",color=discord.Color.red(),timestamp=ctx.message.created_at)
          await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Timezone(client))
