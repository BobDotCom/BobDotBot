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

# import stuff
import discord
import aiosqlite
import aiohttp
from discord.ext import commands
from bs4 import BeautifulSoup
import datetime

class LogCog(commands.Cog, name = "Logging"):
    """Server logs"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        create_guilds_table = """
        CREATE TABLE IF NOT EXISTS guilds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guildid INTEGER,
            enabled INTEGER,
            modlog INTEGER,
            messagelog INTEGER,
            memberlog INTEGER,
            serverlog INTEGER
        );
        """
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(create_guilds_table)
             
    @commands.Cog.listener()
    async def on_member_ban(self,guild,user):
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM guilds WHERE guildid = ?", (guild.id,))
                rows = await cursor.fetchone()

        if rows:
            if rows[2] == 1 and rows[3] != 0:
                try:
                    channel = guild.get_channel(rows[3])
                except:
                    return
                try:
                    entry = (await guild.audit_logs(limit=1,action=discord.AuditLogAction.ban).flatten())[0]
                    embed = discord.Embed(title="Member banned",color=discord.Color.red(),timestamp=entry.created_at)
                    embed.add_field(name="Member",value=user.mention)
                    embed.add_field(name="Moderator",value=entry.user.mention)
                    embed.add_field(name="Reason",value=entry.reason or "None specified")
                except:
                    embed = discord.Embed(title="Member banned",color=discord.Color.red())
                    embed.add_field(name="Member",value=str(user))
                await channel.send(embed=embed)




    @commands.Cog.listener()
    async def on_member_unban(self,guild,user):
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM guilds WHERE guildid = ?", (guild.id,))
                rows = await cursor.fetchone()
        if rows:
            if rows[2] == 1 and rows[3] != 0:
                try:
                    channel = guild.get_channel(rows[3])
                except:
                    return
                try:
                    entry = (await guild.audit_logs(limit=1,action=discord.AuditLogAction.unban).flatten())[0]
                    embed = discord.Embed(title="Member unbanned",color=discord.Color.red(),timestamp=entry.created_at)
                    embed.add_field(name="Member",value=user.mention)
                    embed.add_field(name="Moderator",value=entry.user.mention)
                    embed.add_field(name="Reason",value=entry.reason or "None specified")
                except:
                    embed = discord.Embed(title="Member Unbanned",color=discord.Color.red())
                    embed.add_field(name="Member",value=str(user))
                await channel.send(embed=embed)
    @commands.Cog.listener()
    async def on_member_join(self,member):
        return

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        return

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        return

    @commands.Cog.listener()
    async def on_user_update(self,before,after):
        return

    @commands.Cog.listener()
    async def on_raw_message_delete(self,payload):
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM guilds WHERE guildid = ?". (payload.guild_id,))
                rows = await cursor.fetchone()
        if rows:
            if rows[2] == 1 and rows[3] != 0:
                try:
                    channel = self.client.get_guild(payload.guild_id).get_channel(rows[3])
                    if channel == payload.channel:
                        return
                    embed = discord.Embed(title="Message Deleted",description=payload.cached_message.content,timestamp=datetime.datetime.utcnow())
                    embed.add_field(name="Author",value=payload.cached_message.author.mention)
                    embed.add_field(name="Channel",value=self.client.get_guild(payload.guild_id).get_channel(payload.channel_id))
                    embed.set_footer(text="Deleted")
                    await channel.send(embed=embed)
                except:
                    return


    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self,payload):
        return

    @commands.Cog.listener()
    async def on_raw_message_edit(self,payload):
        return

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def enablelogs(self,ctx):
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM guilds WHERE guildid = ?", (ctx.guild.id,))
                rows = await cursor.fetchone()
        if rows:
            if rows[2] == 0:
                async with aiosqlite.connect("log.sql") as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("UPDATE guilds SET enabled = ? WHERE guildid = ?", (1, ctx.guild.id,))
                        await connection.commit()
                await ctx.send("Successfully enabled logs. Now use my other commands to set the log channels")
            elif rows[2] == 1:
                await ctx.send("You already have logs enabled! Use my other commands to set log channels.")
            else:
                await ctx.send("It appears something went wrong. If this continues, please notify my developer. I will try to fix it now.")
                async with aiosqlite.connect("log.sql") as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("UPDATE guilds SET enabled = ? WHERE guildid = ?", (1, ctx.guild.id,))
                        await connection.commit()
                await ctx.send("It appears that the bug has been resolved. Logs are now enabled. You may use my other commands to set the log channels")
        else:
            await ctx.send("It appears you havent used my logs before. Give me a moment while I add your guild to my database...")
            async with aiosqlite.connect("log.sql") as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("""
            INSERT INTO
            guilds (guildid, enabled, modlog, messagelog, memberlog, serverlog)
            VALUES
            (?, ?, ?, ?, ?, ?);
            """, (ctx.guild.id,1,0,0,0,0,))
                    await connection.commit()
            await ctx.send("Sucess! Now use my other commands to set the log channels")
        
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def disablelogs(self,ctx):
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM guilds WHERE guildid = ?", (ctx.guild.id,))
                rows = await cursor.fetchone()
        if rows:
            if rows[2] == 1:
                async with aiosqlite.connect("log.sql") as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("UPDATE guilds SET enabled = ? WHERE guildid = ?", (0, ctx.guild.id,))
                        await connection.commit()
                await ctx.send("Successfully disabled logs.")
            elif rows[2] == 0:
                await ctx.send("You already have logs disabled! To use logs, please enable them instead.")
            else:
                await ctx.send("It appears something went wrong. If this continues, please notify my developer. I will try to fix it now.")
                async with aiosqlite.connect("log.sql") as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("UPDATE guilds SET enabled = ? WHERE guildid = ?", (0, ctx.guild.id,))
                        await connection.commit()
                await ctx.send("It appears that the bug has been resolved. Logs are now disabled.")
        else:
            await ctx.send("It appears you havent used my logs before. Please enable them first.")
    
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def modlog(self,ctx):
        async with aiosqlite.connect("log.sql") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM guilds WHERE guildid = ?", (ctx.guild.id,))
                rows = await cursor.fetchone()
        if rows:
            async with aiosqlite.connect("log.sql") as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("UPDATE guilds SET modlog = ? WHERE guildid = ?", (ctx.channel.id, ctx.guild.id,))
                    await connection.commit()
            await ctx.send("Success!")


def setup(client):
    client.add_cog(LogCog(client))
