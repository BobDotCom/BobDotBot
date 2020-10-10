import discord
from discord.ext import commands

from otherscripts.data import Data
# import stuff
import os
import json
# import stuff
import typing
import asyncio
import datetime
# import stuff
from dotenv import load_dotenv
from datetime import datetime

class Serversettings(commands.Cog, name = "Settings"):
    """Special commands that only administrators/moderators in the server can use"""
    def __init__(self, client):
        self.bot = client
        self.theme_color = discord.Color.blurple()
    @commands.Cog.listener()
    async def on_ready(self):
        print('SettingsCog is active')
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    @commands.has_permissions(manage_guild = True)
    async def prefix(self, ctx, *args):
        """Set one or multiple prefixes for BobDotBot in your server"""
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        with open('prefixes.json', 'r') as f:
            notprefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = args
        notprefixes[str(ctx.guild.id)] = ['B.', 'b.']
        args = None if not args else args
        if args:
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Prefix(s) changed to {args}')
        else:
            await ctx.send('To use the prefixes command, type B.prefix prefix1 prefix2(optional) etc. Since you did not specify any prefixes this time, I reset your server prefixes to the default B. or b.')
            with open('prefixes.json', 'w') as f:
                json.dump(notprefixes, f, indent=4)
    @commands.command(name="welcomemessage")
    @commands.has_guild_permissions(administrator=True)
    async def welcome_message(self, ctx, *, msg: str = ""):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["welcome_msg"] = msg
        if len(msg.strip()) == 0:
            await ctx.send("This server's welcome message has been disabled")
        else:
            await ctx.send(f"This server's welcome message has been set to ```{msg}```")
    @commands.command(name="leavemessage")
    @commands.has_guild_permissions(administrator=True)
    async def leave_message(self, ctx, *, msg: str = ""):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["leave_message"] = msg
        if len(msg.strip()) == 0:
            await ctx.send("This server's leave message has been disabled")
        else:
            await ctx.send(f"This server's leave message has been set to ```{msg}```")

    @commands.command(name="joinrole")
    @commands.has_guild_permissions(administrator=True)
    async def join_role(self, ctx, *, role: discord.Role):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["join_role"] = role.id
        await ctx.send(f"This server's join role has been set to **{role}**")
def setup(client):
    client.add_cog(Serversettings(client))
