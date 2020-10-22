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
    """Special commands that only administrators in the server can use"""
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
        """Set one or multiple prefixes for BobDotBot in your server. If no prefix is specified, it will reset to defaults"""
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = args if args else ['B.', 'b.']
        if args:
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Prefix(s) changed to {args}')
        else:
            await ctx.send('Since you did not specify any prefixes this time, I reset your server prefixes to the default B. or b. If you need help, use my help command')
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
    @commands.command(name="welcomer")
    @commands.has_guild_permissions(administrator=True)
    async def welcome_message(self, ctx, *, msg: str = ""):
        """Set a message to send when a user joins your server. It will automatically send in any channnel with "welcome" in the name. To mention the joining user in the message, type [mention], and to mention a channel, just mention that channel in your message.
        Uses: `B.welcomer [message]`
        Note: Arguments in brackets[] are optional"""
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["welcome_msg"] = msg
        if len(msg.strip()) == 0:
            await ctx.send("This server's welcome message has been disabled")
        else:
            await ctx.send(f"This server's welcome message has been set to ```{msg}```")
    @commands.command(name="leaver")
    @commands.has_guild_permissions(administrator=True)
    async def leave_message(self, ctx, *, msg: str = ""):
        """Set a message to send when a user leaves your server. It will automatically send in any channnel with "leave" or "bye" in the name. To send the name of the leaving user in the message, type [member].
        Uses: `B.leaver [message]`
        Note: Arguments in brackets[] are optional"""
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
        """Set a role to give users when they join your server. Just typing the role name should work, but mentioning it will too.
        Uses: `B.joinrole <role>`"""
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["join_role"] = role.id
        await ctx.send(f"This server's join role has been set to **{role}**")
        
    @commands.command(name="activateautomod")
    @commands.has_guild_permissions(administrator=True)
    async def activateautomod(self, ctx):
        """Turn on AutoMod in your server.
        Uses: `B.activateautomod`"""
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["active"] = True
        await ctx.send("Automod is now active in your server...")


    @commands.command(name="stopautomod")
    @commands.has_guild_permissions(administrator=True)
    async def stopautomod(self, ctx):
        """Turn off AutoMod in your server.
        Uses: `B.stopautomod`"""
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["active"] = False
        await ctx.send("Automod is now inactive in your server...")


    @commands.command(name="whitelistuser")
    @commands.has_guild_permissions(administrator=True)
    async def whitelistuser(self, ctx, user: discord.User = None):
        """Whitelist a user from the AutoMod
        Uses: `B.whitelistuser <user>`"""
        if user is None:
            ctx.send("Insufficient Arguments")
        else:
            if str(ctx.guild.id) not in Data.server_data:
                Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

            Data.server_data[str(ctx.guild.id)]["users"].append(str(user.id))
            await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")
    

    @commands.command(name="whitelisturl")
    @commands.has_guild_permissions(administrator=True)
    async def whitelisturl(self, ctx, url: str = None):
        """Whitelist a URL from the AutoMod
        Uses: `B.whitelisturl <URL>`"""
        if url is None:
            ctx.send("Insufficient Arguments")
        else:
            if str(ctx.guild.id) not in Data.server_data:
                Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

            Data.server_data[str(ctx.guild.id)]["urls"].append(url)
            await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")


    @commands.command(name="whitelistchannel")
    @commands.has_guild_permissions(administrator=True)
    async def whitelistchannel(self, ctx, channel: discord.TextChannel = None):
        """Whitelist a channel from the AutoMod\
        Uses: `B.whitelistchannel <channel>`"""
        if channel is None:
            ctx.send("Insufficient Arguments")
        else:
            if str(ctx.guild.id) not in Data.server_data:
                Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

            Data.server_data[str(ctx.guild.id)]["channels"].append(
                str(channel.id))
            await ctx.send(f"Added {channel.mention} to AutoMod Channel whitelist.")

    @commands.command(name="data")
    async def data(self, ctx):
        """Owner Command"""
        is_owner = await self.bot.is_owner(ctx.author)
        if is_owner:  # for real sparta
            data_file = discord.File("data.json")
            await ctx.send(file=data_file)
    @commands.command(name="automodstatus")
    async def automodstatus(self, ctx):
        """Get the status of AutoMod in your server
        Uses: `B.automodstatus`"""
        status = Data.server_data[str(ctx.guild.id)]["active"]
        await ctx.send(f"AutoMod Active: **{status}**")

def setup(client):
    client.add_cog(Serversettings(client))
