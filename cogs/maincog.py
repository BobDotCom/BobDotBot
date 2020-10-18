# All 25 of the gay imports
import discord
import os
import random
import typing
import asyncio
import datetime
import functools
import operator
import json
import pprint
import aiohttp
from googleapiclient.discovery import build
import binascii
import sys
import requests
import sqlite3
from dotenv import load_dotenv
from sqlite3 import Error
from termcolor import colored, cprint
from humanize import precisedelta as nd
from discord.ext.commands import Bot, BucketType
from discord.ext import commands
#from .otherscripts import cheks, formats, time
from otherscripts.paginator import RoboPages
from collections import OrderedDict, deque, Counter
import copy
import unicodedata
import inspect
import itertools
from typing import Union
from datetime import datetime
from discord.ext.commands import MissingPermissions
from discord.ext import menus
load_dotenv()
MONITOR_TOKEN = os.getenv("MONITOR_TOKEN")

# Create an instance of a class
# Create an instance of a class
class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        #entries will be each element of your passed list.
        embed = discord.Embed(title=entries["title"], url=entries["link"], description=entries["snippet"])
        try:
            x = entries["pagemap"]["metatags"][0]["og:image"]
            if x[:6] == https:
                embed.set_thumbnail(url="https:" + entries["pagemap"]["metatags"][0]["og:image"])
            else:
                embed.set_thumbnail(url=entries["pagemap"]["metatags"][0]["og:image"])
        except:
            pass
        embed.set_footer(text=f"Result {menu.current_page + 1}/{menu._source.get_max_pages()}")
        return embed
class BotHelpPageSource(menus.ListPageSource):
    def __init__(self, help_command, commands):
        # entries = [(cog, len(sub)) for cog, sub in commands.items()]
        # entries.sort(key=lambda t: (t[0].qualified_name, t[1]), reverse=True)
        super().__init__(entries=sorted(commands.keys(), key=lambda c: c.qualified_name), per_page=6)
        self.commands = commands
        self.help_command = help_command
        self.prefix = help_command.clean_prefix

    def format_commands(self, cog, commands):
        # A field can only have 1024 characters so we need to paginate a bit
        # just in case it doesn't fit perfectly
        # However, we have 6 per page so I'll try cutting it off at around 800 instead
        # Since there's a 6000 character limit overall in the embed
        if cog.description:
            short_doc = cog.description.split('\n', 1)[0] + '\n'
        else:
            short_doc = 'No help found...\n'

        current_count = len(short_doc)
        ending_note = '+%d not shown'
        ending_length = len(ending_note)

        page = []
        formyaddidion = False
        for command in commands:
            if formyaddidion == False:
                value = f'`{command.name}`'
                formyaddidion = True
            else:
                value = f'| `{command.name}`'
            count = len(value) + 1 # The space
            if count + current_count < 800:
                current_count += count
                page.append(value)
            else:
                # If we're maxed out then see if we can add the ending note
                if current_count + ending_length + 1 > 800:
                    # If we are, pop out the last element to make room
                    page.pop()

                # Done paginating so just exit
                break

        if len(page) == len(commands):
            # We're not hiding anything so just return it as-is
            return short_doc + ' '.join(page)

        hidden = len(commands) - len(page)
        return short_doc + ' '.join(page) + '\n' + (ending_note % hidden)


    async def format_page(self, menu, cogs):
        prefix = menu.ctx.prefix
        description = f'Use "{prefix}help command" for more info on a command.\n' \
                      f'Use "{prefix}help category" for more info on a category.\n' \
                       'For more help, join the official bot support server: [BobDotBot Support](https://discord.gg/3seAXGr)'

        embed = discord.Embed(title='Categories', description=description, colour=discord.Colour.blurple())

        for cog in cogs:
            commands = self.commands.get(cog)
            if commands:
                value = self.format_commands(cog, commands)
                embed.add_field(name=cog.qualified_name, value=value, inline=True)

        maximum = self.get_max_pages()
        embed.set_footer(text=f'Page {menu.current_page + 1}/{maximum}')
        return embed

class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self, group, commands, *, prefix):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f'{self.group.qualified_name} Commands'
        self.description = self.group.description

    async def format_page(self, menu, commands):
        embed = discord.Embed(title=self.title, description=self.description, colour=discord.Colour.blurple())

        for command in commands:
            signature = f'{command.qualified_name} {command.signature}'
            embed.add_field(name=signature, value=command.short_doc or 'No help given...', inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed


class HelpMenu(RoboPages):
    def __init__(self, source):
        super().__init__(source)

    @menus.button('\N{WHITE QUESTION MARK ORNAMENT}', position=menus.Last(5))
    async def show_bot_help(self, payload):
        """shows how to use the bot"""

        embed = discord.Embed(title='How to use the help command', colour=discord.Colour.blurple())
        embed.title = 'How to use the help command'
        embed.description = 'This is help for the help'

        entries = (
            ('<argument>', 'This means the argument is __**required**__.'),
            ('[argument]', 'This means the argument is __**optional**__.'),
            ('[A|B]', 'This means that it can be __**either A or B**__.'),
            ('[argument...]', 'This means you can have multiple arguments.\n' \
                              'Now that you know the basics, it should be noted that...\n' \
                              '__**You do not type in the brackets!**__')
        )

        embed.add_field(name='How do I use this bot?', value='Reading the bot signature is pretty simple.')

        for name, value in entries:
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=f'Previous page: {self.current_page + 1}')
        await self.message.edit(embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member),
            'help': 'Shows help about the bot, a command, or a category'
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True)

        all_commands = {}
        for command in entries:
            if command.cog is None:
                continue
            try:
                all_commands[command.cog].append(command)
            except KeyError:
                all_commands[command.cog] = [command]


        menu = HelpMenu(BotHelpPageSource(self, all_commands))
        await menu.start(self.context)

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        menu = HelpMenu(GroupHelpPageSource(cog, entries, prefix=self.clean_prefix))
        await menu.start(self.context)

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.help or 'No help found...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.blurple())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group, entries, prefix=self.clean_prefix)
        self.common_command_formatting(source, group)
        menu = HelpMenu(source)
        await menu.start(self.context)
class MemberRoles(commands.MemberConverter):
    async def convert(self, ctx, argument):
        member = ctx.author if not argument else await super().convert(ctx, argument)
        return [role.mention for role in member.roles[1:]] # Remove everyone role!

class MainCog(commands.Cog, name = "General"):
    """General commands that anyone can use"""

    def __init__(self, client):
        self.client = client
        self.bot = client
        self.client.uptime1 = datetime.utcnow()
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221
        self.client.helper1_id = 716503311402008577
        self.client.helper2_id = 280667989370732545
        self.client.helper3_id = 706898741499789364
        global onreadyblocker
        onreadyblocker = False
        self.api = "https://some-random-api.ml"
        client.help_command = PaginatedHelpCommand()
        client.help_command.cog = self

    async def save_users(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
                with open("users.json", 'r') as f1:
                        self.users = json.load(f1)


                await asyncio.sleep(60)
    @commands.Cog.listener()
    async def on_ready(self):
      print('MainCog is active')
      await asyncio.sleep(5)
      global onreadyblocker
      if onreadyblocker == False:
        onreadyblocker = True
        if True:
          def create_connection(path):
            connection = None
            try:
              connection = sqlite3.connect(path)
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
            return connection
          connection = create_connection("reports.db")
          def execute_query(connection, query):
            cursor = connection.cursor()
            try:
                cursor.execute(query)
                connection.commit()
            except Error as e:
                cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
          def execute_read_query(connection, query):
            cursor = connection.cursor()
            result = None
            try:
              cursor.execute(query)
              result = cursor.fetchall()
              return result
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
          create_users_table = """
          CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            report TEXT NOT NULL,
            reportcontent TEXT NOT NULL,
            logreport TEXT,
            status TEXT NOT NULL
          );
          """
          execute_query(connection, create_users_table)
          def getDeveloperInfo(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from reports where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[2]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
          def getTheInfo(info1):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select id from reports where report = ?"""
              cursor.execute(sql_select_query, (info1,))
              records = cursor.fetchall()

              for id in records:
                return int(''.join(map(str, id)))
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
          execute_query(connection, create_users_table)
          def getDeveloperInfo1(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from reports where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[1]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
          def getDeveloperInfo2(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from reports where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[3]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
          def getDeveloperInfo3(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from reports where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[4]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
          def getDeveloperInfo4(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from reports where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[5]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def check(reaction, user):
          guild = self.client.get_guild(727739470731935765)
          nsfw = self.client.get_emoji(762060771680583710)
          if str(reaction.emoji) == '✅':
            if user == owner:
              message_id = str(reaction.message.id)
              info1 = getTheInfo(message_id)
              info = getDeveloperInfo(info1)
              if str(reaction.message.id) == info:
                return str(reaction.emoji) == '✅' and user == owner

          elif str(reaction.emoji) == '❎':
            if user == owner:
              message_id = str(reaction.message.id)
              info1 = getTheInfo(message_id)
              info = getDeveloperInfo(info1)
              if str(reaction.message.id) == info:
                return str(reaction.emoji) == '❎' and user == owner
        c2 = self.client.get_guild(727739470731935765).get_channel(755258858242441308)
        owner = self.client.get_user(self.client.owner_id)
        while True:
          reaction, user = await self.client.wait_for('reaction_add', check=check)
          if str(reaction) == '✅' and user == owner:
            await reaction.remove(user)
            message_id = str(reaction.message.id)
            infos = getTheInfo(message_id)
            info5 = getDeveloperInfo4(infos)
            othermessage = getDeveloperInfo(infos)
            info2 = getDeveloperInfo1(infos)
            send_to = self.client.get_user(int(info2))
            info3 = getDeveloperInfo2(infos)
            the_content = info3
            if info5 == 'Approved':
              info4 = getDeveloperInfo3(infos)
              second_message = await c2.fetch_message(int(info4))
              delete_account = f"DELETE FROM reports WHERE report = {othermessage}"
              execute_query(connection, delete_account)
              await second_message.edit(content=f"COMPLETED: {the_content}")
              await reaction.message.edit(content=f"COMPLETED: {the_content}")
            elif info5 == 'Submitted':
              msg2 = await c2.send(f"APPROVED: {the_content}")
              update_post_description = f"""
                UPDATE
                  reports
                SET
                  logreport = "{msg2.id}",
                  status = 'Approved'
                WHERE
                  report = {othermessage}
                """
              execute_query(connection, update_post_description)
              await send_to.send(f"Hey, {user.name} approved your suggestion")
              await reaction.message.edit(content=f"APPROVED: {the_content}")
            else:
              return
          elif str(reaction) == '✅' and user == owner:
            send_to = self.client.get_user(int(info2))
            await send_to.send("Your suggestion did not get approved")
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.message_id == 762754787602595840 and not payload.member.bot:
            guild = self.client.get_guild(payload.guild_id)
            nsfw = "<:nsfw:762060771680583710>"
            dev = "<:computer:762783497315811358>"
            channel = guild.get_channel(762721025912733696)
            message = await channel.fetch_message(payload.message_id)
            role = guild.get_role(745834936992399410)
            announce = "<:megaphone:762345707272667227>"
            role2 = guild.get_role(762065259166957588)
            role3 = guild.get_role(762487691061231617)
            remove = "<:redx:762347633925947392>"
            member = payload.member
            if str(payload.emoji) == nsfw:
                await member.add_roles(role)
                await message.remove_reaction(nsfw, member)
                await member.send(f"Added role: **{role.name}**")
            elif str(payload.emoji) == announce:
                await member.add_roles(role2)
                await message.remove_reaction(announce, member)
                await member.send(f"Added role: **{role2.name}**")
            elif str(payload.emoji) == dev:
                await member.add_roles(role3)
                await message.remove_reaction(dev, member)
                await member.send(f"Added role: **{role3.name}**")
            elif str(payload.emoji) == remove:
                await message.remove_reaction(remove, member)
                await member.remove_roles(role)
                await member.remove_roles(role2)
                await member.remove_roles(role3)
                await member.send("Removed roles")
        elif payload.message_id == 762773798419169310 and not payload.member.bot:
            guild = self.client.get_guild(payload.guild_id)
            red = "<:red:762759166627676201>"
            orange = "<:orange:762759545642549278>"
            yellow = "<:yellow:762759756514721852>"
            green = "<:green:762759873984462918>"
            blue = "<:blue:762760282354352168>"
            purple = "<:purple:762760629462761534>"
            channel = guild.get_channel(762721025912733696)
            message = await channel.fetch_message(payload.message_id)
            red1 = guild.get_role(762717092418945084)
            orange1 = guild.get_role(762717096529887282)
            yellow1 = guild.get_role(762717099633803326)
            green1 = guild.get_role(762717102091141137)
            blue1 = guild.get_role(762717103982903336)
            purple1 = guild.get_role(762717105938104391)
            remove = "<:redx:762347633925947392>"
            member = payload.member
            if str(payload.emoji) == red:
                await member.add_roles(red1)
                await member.remove_roles(orange1)
                await member.remove_roles(yellow1)
                await member.remove_roles(green1)
                await member.remove_roles(blue1)
                await member.remove_roles(purple1)
                await message.remove_reaction(red, member)
                await member.send(f"Added role: **{red1.name}**")
            elif str(payload.emoji) == orange:
                await member.add_roles(orange1)
                await member.remove_roles(red1)
                await member.remove_roles(yellow1)
                await member.remove_roles(green1)
                await member.remove_roles(blue1)
                await member.remove_roles(purple1)
                await message.remove_reaction(orange, member)
                await member.send(f"Added role: **{orange1.name}**")
            elif str(payload.emoji) == yellow:
                await member.add_roles(yellow1)
                await member.remove_roles(red1)
                await member.remove_roles(orange1)
                await member.remove_roles(green1)
                await member.remove_roles(blue1)
                await member.remove_roles(purple1)
                await message.remove_reaction(yellow, member)
                await member.send(f"Added role: **{yellow1.name}**")
            elif str(payload.emoji) == green:
                await member.add_roles(green1)
                await member.remove_roles(red1)
                await member.remove_roles(orange1)
                await member.remove_roles(yellow1)
                await member.remove_roles(blue1)
                await member.remove_roles(purple1)
                await message.remove_reaction(green, member)
                await member.send(f"Added role: **{green1.name}**")
            elif str(payload.emoji) == blue:
                await member.add_roles(blue1)
                await member.remove_roles(red1)
                await member.remove_roles(orange1)
                await member.remove_roles(yellow1)
                await member.remove_roles(green1)
                await member.remove_roles(purple1)
                await message.remove_reaction(blue, member)
                await member.send(f"Added role: **{blue1.name}**")
            elif str(payload.emoji) == purple:
                await member.add_roles(purple1)
                await member.remove_roles(red1)
                await member.remove_roles(orange1)
                await member.remove_roles(yellow1)
                await member.remove_roles(green1)
                await member.remove_roles(blue1)
                await message.remove_reaction(purple, member)
                await member.send(f"Added role: **{purple1.name}**")
            elif str(payload.emoji) == remove:
                await message.remove_reaction(remove, member)
                await member.remove_roles(red1)
                await member.remove_roles(orange1)
                await member.remove_roles(yellow1)
                await member.remove_roles(green1)
                await member.remove_roles(blue1)
                await member.remove_roles(purple1)
                await member.send("Removed roles")
                
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def uptime(self, ctx):
            """See how long the bot has been online
            Uses: `B.uptime`"""
            owner = self.client.get_user(self.client.owner_id)
            url = "https://api.uptimerobot.com/v2/getMonitors"
            payload = f"api_key={MONITOR_TOKEN}&format=json&logs=1&response_times=1&custom_uptime_ratios=1-7-30"
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
                }
            async with aiohttp.ClientSession() as sess:
                async with sess.post(url, data=payload, headers=headers) as resp:
                    loaded_json = await resp.json()
                await sess.close()
            second = 0
            uptime = 0
            second1 = 0
            time = datetime.utcnow()
            time -= self.client.uptime
            time1 = datetime.utcnow()
            time1 -= self.client.uptime1
            second = list(str(time.seconds)).copy()
            second = int("".join(second))
            second1 = list(str(time1.seconds)).copy()
            second1 = int("".join(second1))
            uptime = loaded_json["monitors"][0]["logs"][0]["duration"]
            ping = loaded_json["monitors"][0]["average_response_time"]
            ratios1 = loaded_json["monitors"][0]["custom_uptime_ratio"]
            ratios = ratios1.split("-")
            perday = ratios[0]
            perweek = ratios[1]
            permonth = ratios[2]
            embedVar = discord.Embed(title="Bot Uptime", timestamp=ctx.message.created_at, description=f"Bot has been online for `{nd(second)}`, and was last reloaded `{nd(second1)}` ago")
            embedVar.add_field(name="BobDotBot Server Uptime", value=f"Server has been up for `{nd(uptime)}`, with an average response time of `{ping}ms`")
            embedVar.add_field(name="BobDotBot Server Uptime History", value=f"BobDotBot has logged:\n`{perday}%` uptime today\n`{perweek}%` uptime this week\n`{permonth}%` uptime this month")
            embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
            await ctx.send(embed=embedVar)

    @commands.command(aliases=["nub"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def noob(self, ctx):
        """Ur nub
        Uses: `B.noob`"""
        await ctx.send("NOOOOOB")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def invite(self, ctx):
        """Invite me to your own server!
        Uses: `B.invite`"""
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Wow! I'm really that special?", timestamp=ctx.message.created_at, description="I have 2 different versions, here they are:")
        embedvar.add_field(name="BobDotBot(Reccomended)", value="This bot is online almost 24/7, and the code works a lot better than alpha, though it still has lots of new features. [Click Here](https://discord.com/api/oauth2/authorize?client_id=746045299125911562&permissions=8&scope=bot)", inline=False)
        embedvar.add_field(name="BobDotBot Alpha(Unstable)", value="This bot has code that updates as I write it, so it may be buggy. Only online part of the day.(You will have to request permission from the owner to invite this bot) [Click Here](https://discord.com/api/oauth2/authorize?client_id=745044803732897802&permissions=8&scope=bot)", inline=False)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def add(self, ctx, a: int, b: int):
        """I'm a baby bot, so I only do baby math
        Uses: `B.add <number> <number>`"""
        answer = (a + b)
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Math", timestamp=ctx.message.created_at, description="I think the answer to that is **" + str(answer) + "**") 
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def slap(self, ctx, members: commands.Greedy[discord.Member], *, reason='no reason'):
        """Use this to slap someone
        Uses: `B.slap [user] [reason]`
        Note: Arguments in brackets[] are not required
        Note: If the user has a multi word name, put it in "quotes", or mention it"""
        slapped = ", ".join(x.name for x in members)
        slapself = f"{ctx.author.name}"
        owner = self.client.get_user(self.client.owner_id)
        if slapped:
            embedvar = discord.Embed(title="***SLAP***", timestamp=ctx.message.created_at, description='*{}* just got **slapped** for {}'.format(slapped, reason)) 
            embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        else:
            embedvar = discord.Embed(title="***OOPS***", timestamp=ctx.message.created_at, description=f"{slapself} just **slapped** themselves because they didn't mention someone valid to slap!")
        await ctx.send(embed=embedvar)
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def say(self, ctx, *, arg):
        """Use the bot to say something
        Uses: `B.say <text>`"""
        quote = arg
        author = ctx.author.name
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title=f"{author} says:", timestamp=ctx.message.created_at, description=f'{quote}')
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedVar)

    @commands.command(aliases=['pong'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def ping(self, ctx):
        """Checks the latency of the bot(lower is better)
        Uses: `B.ping`"""
        ping = int(self.client.latency * 1000)
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title="***PONG!***  :ping_pong:", timestamp=ctx.message.created_at, description="My ping is *" + str(ping) + "ms*")
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedVar)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def porn(self, ctx):
        """Use if you are really horny
        Uses: `B.porn`"""
        await ctx.send("Shut up, horny kid.")


    @commands.command(aliases=["credit", "owner"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def credits(self, ctx):
        """Shows the credits for the bot
        Uses: `B.credits`"""
        owner = self.client.get_user(self.client.owner_id)
        routergtx = self.client.get_user(self.client.helper1_id)
        gamin = self.client.get_user(self.client.helper2_id)
        yo56789 = self.client.get_user(self.client.helper3_id)
        tcc = "[The Coding Community](https://discord.gg/a84amZ4)"
        dpy = "[Discord.py](https://discord.gg/dpy)"
        embed = discord.Embed(timestamp=ctx.message.created_at, inline=False)
        embed.set_author(name=f"Bot created by {owner}", icon_url=owner.avatar_url)
        embed.add_field(name=f"Others", value=f"Special thanks to everyone who helped me with learning how to create this bot, especially the following people and servers", inline=False)
        embed.add_field(name=f'{routergtx}', value=f"RouterGTX was a really big help with learning how the code worked, and giving me examples, but still letting me figure out most of it on my own", inline=False)
        embed.add_field(name=f'{gamin}', value=f'Okct was one of the first people to help me, and was able to help me solve problems that I was having trouble with at the beginning', inline=False)
        embed.add_field(name=f'{yo56789}', value=f'Yo56789 helped me learn that if you give someone admin, they will grief your server :/', inline=False)
        embed.add_field(name=f'Servers', value=f'{tcc} -- This was the first server that I got help from, and they are quite active and able to help.\n{dpy} -- This is the official discord.py server, and it has an extremely active help chat, where you can get help with almost anything about discord.py.', inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['xp', 'rank', 'levels'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def level(self, ctx, member: discord.Member = None):
        """Lists a user's level. You can level up by talking in any channel/server that the bot is in
        Uses: `B.level [member]`
        Note: Arguments in brackets[] are optional"""
        if True:
          def create_connection(path):
            connection = None
            try:
              connection = sqlite3.connect(path)
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
            return connection
          connection = create_connection("Users.db")
          def execute_query(connection, query):
            cursor = connection.cursor()
            try:
                cursor.execute(query)
                connection.commit()
            except Error as e:
                cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
          def execute_read_query(connection, query):
            cursor = connection.cursor()
            result = None
            try:
              cursor.execute(query)
              result = cursor.fetchall()
              return result
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
          create_users_table = """
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT NOT NULL,
            level INTEGER NOT NULL,
            xp INTEGER NOT NULL
          );
          """
          execute_query(connection, create_users_table)
        def get_userid(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from users where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[1]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def get_id(info1):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select id from users where userid = ?"""
              cursor.execute(sql_select_query, (info1,))
              records = cursor.fetchall()

              for id in records:
                return int(''.join(map(str, id)))
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def get_xp(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from users where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[3]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def get_level(username):
            try:
              cursor = connection.cursor()

              sql_select_query = f"""select * from users where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()

              for row in records:
                return row[2]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        member = ctx.author if not member else member
        member_id = str(member.id)
        owner = self.client.get_user(self.client.owner_id)
        the_id = get_id(member_id)
        userid = get_userid(the_id)
        if userid == None:
            await ctx.send("Member doesn't have a level. This could be because they have not talked yet, or due to a glitch.")
        else:
            xp = get_xp(the_id)
            level = get_level(the_id)
            embed = discord.Embed(timestamp=ctx.message.created_at)
            embed.set_author(name=f"Level - {member}", icon_url=member.avatar_url)
            embed.add_field(name="Level", value=level)
            embed.add_field(name="XP", value=xp)
            embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
            await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def ligma(self, ctx):
        """Ligmabols
        Uses: `B.ligma`"""
        await ctx.send("slurp")

    @commands.command(aliases=['suggestion'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def suggest(self, ctx, *, arg):
      """Make a suggestion about the bot, it can be a new command that you would like to see, or anything else that you want to suggest. NOTE: do not use this command for bugs. To report a bug, use the bug command.
        Uses: `B.suggest <suggestion>`"""
      def create_connection(path):
        connection = None
        try:
          connection = sqlite3.connect(path)
        except Error as e:
          cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')

        return connection
      connection = create_connection("reports.db")
      def execute_query(connection, query,params:tuple=()):
        cursor = connection.cursor()
        try:
            cursor.execute(query,params)
            connection.commit()
        except Error as e:
            cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
        def execute_read_query(connection, query):
            cursor = connection.cursor()
            result = None
            try:
              cursor.execute(query)
              result = cursor.fetchall()
              return result
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')

      report = arg
      owner = self.client.get_user(self.client.owner_id)
      reporter = ctx.author.name
      embed = discord.Embed(timestamp=ctx.message.created_at, title='Success!',description='Also, consider joining the support server: [Click here](https://discord.gg/3seAXGr)')
      embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
      c = self.client.get_guild(727739470731935765).get_channel(751834280929525791)
      msg = await c.send(f"{reporter} suggested {report}")
      create_users = f"""
        INSERT INTO
          reports (username, report, reportcontent, logreport, status)
        VALUES
          (?,?,?,?,?);
        """
      execute_query(connection, create_users,(ctx.author.id,msg.id,msg.content,'None','Submitted',))
      await msg.add_reaction(emoji='✅')
      await msg.add_reaction(emoji='❎')
      await ctx.send(embed=embed)

    @commands.command(aliases=['bugs'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def bug(self, ctx, *, arg):
        """Let the owner know about a bug in the bot. NOTE: do not use this command for suggestions. To make a suggestion, use the suggestion command.
        Uses: `B.bug <report>`"""
        #load the database, collapseable
        suggestion = arg
        owner = self.client.get_user(self.client.owner_id)
        embed = discord.Embed(timestamp=ctx.message.created_at, title='Success!',description='Also, consider joining the support server: [Click here](https://discord.gg/3seAXGr)')
        embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        suggestor = ctx.author.name
        c = self.client.get_guild(727739470731935765).get_channel(751971356865986731)
        msg = await c.send(f"{suggestor} reported {suggestion}")
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❎')
        await ctx.send(embed=embed)
    @commands.command(aliases=["emoji"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def emoji_id(self,ctx,emoji: discord.Emoji):
        """Get the ID of any custom emoji that the bot can see
        Uses: `B.emoji_id <emoji>`
        Example: B.emoji_id <:computer:762783497315811358>"""
        owner = self.client.get_user(self.client.owner_id)
        emoji = self.client.get_emoji(emoji.id)
        embed = discord.Embed(timestamp=ctx.message.created_at, title=f'{emoji} Emoji id for :{emoji.name}: {emoji}',description=f'ID: {emoji.id}')
        embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        await ctx.send(embed=embed)
    #@commands.command()
    #async def menu_example(self,ctx):
        #m = MyMenu()
        #await m.start(ctx)
        # Python3 code to demonstrate working of 
    @commands.command(aliases=["ttb", "text_to_binary", "binary"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def encode(self,ctx,*,arg):
        """Take a string of ASCII text and translate it to binary
        Uses: `B.encode <text>`"""
        binary = ' '.join(format(ord(i), 'b') for i in arg)
        embed = discord.Embed(timestamp=ctx.message.created_at, title="Text to binary", description=binary)
        await ctx.send(embed=embed)
    @commands.command(aliases=["btt", "binary_to_text", "text"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def decode(self,ctx,*,arg):
        """Take a string of binary and translate it back to ASCII text
        Uses: `B.decode <binary>`"""
        lists = ""
        newarg = arg.split(" ")
        for x in newarg:
            asdf = chr(int(x, 2))
            thevar = (lists,asdf)
            lists = "".join(thevar)
        embed = discord.Embed(timestamp=ctx.message.created_at, title="Binary to text", description=lists)
        await ctx.send(embed=embed)
    @commands.command(name="serverinfo", aliases=["si"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def serverinfo(self, ctx):
        """Get the info of the server that you are in
        Uses `B.serverinfo`"""
        name = ctx.guild.name
        description = ctx.guild.description
        owner = ctx.guild.owner
        guild_id = ctx.guild.id
        region = ctx.guild.region
        member_count = ctx.guild.member_count
        icon = ctx.guild.icon_url

        embed = discord.Embed(
            title=f"{name} Server Information",
            description=description
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=guild_id, inline=True)
        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Member Count", value=member_count, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="userinfo", aliases=["ui"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def userinfo(self, ctx, member: discord.Member = None):
        """Tells you some info about the member.
        Uses: `B.userinfo [member]`
        Note: Arguments in brackets[] are optional
        Note: If the user has a multi word name, put it in "quotes", or mention it"""
        member = ctx.author if not member else member

        embed = discord.Embed(
            timestamp=ctx.message.created_at,
            description=member.mention
        )

        embed.set_author(name=f"{member} Info")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Nickname", value=member.nick)
        embed.add_field(
            name="Registered At:",
            value=member.created_at.strftime("%a, %d %b %Y %I:%M %p")
        )
        embed.add_field(
            name="Joined Server At:",
            value=member.joined_at.strftime("%a, %d %b %Y %I:%M %p")
        )
        badges = ""
        for i in list(iter(member.public_flags)):
            if i[1] and i[0] == "staff":
                badges += str(self.bot.get_emoji(764456791215046667))+" Discord Staff"
            if  i[1] and i[0] == "partner":
                badges += str(self.bot.get_emoji(764456791345201173))+" Discord Partner"
            if  i[1] and i[0] == "early_supporter":
                badges += str(self.bot.get_emoji(764456791453990933))+" Early Supporter"
            if  i[1] and i[0] == "bug_hunter":
                badges += str(self.bot.get_emoji(764456789440725012))+" Bug Hunter"
            if  i[1] and i[0] == "bug_hunter_level_2":
                badges += str(self.bot.get_emoji(764456791509041152))+" Bug Hunter 2"
            if  i[1] and i[0] == "early_verified_bot_developer":
                badges += str(self.bot.get_emoji(764456791601315860))+" Early Verified Bot Developer"
            if  i[1] and i[0] == "verified_bot":
                badges += str(self.bot.get_emoji(764507982347763712))+str(self.bot.get_emoji(764507981907755018))+" Verified Bot"
            if  i[1] and i[0] == "hypesquad":
                badges += str(self.bot.get_emoji(764456789256830976))+" Hypesquad"
            if  i[1] and i[0] == "hypesquad_bravery":
                badges += str(self.bot.get_emoji(764456791294869506))+" Hypesquad Bravery"
            if  i[1] and i[0] == "hypesquad_brilliance":
                badges += str(self.bot.get_emoji(764456789734588426))+" Hypesquad Brilliance"
            if  i[1] and i[0] == "hypesquad_balance":
                badges += str(self.bot.get_emoji(764456791521361930))+" Hypesquad Balance"
            else:
                badges += ""
        if badges == "":
            badges = "None"
        embed.add_field(name="Badges", value=badges)

        embed.add_field(name="Bot?", value=member.bot)
        roles = " ".join([role.mention for role in member.roles if role != ctx.guild.default_role])
        roles = "Nothing to display here, this user looks boring" if not roles else roles
        embed.add_field(
            name=f"{len(member.roles)-1} Roles",
            value=roles,
            inline = False
        )

        await ctx.send(embed=embed)
    @commands.command(name="avatar")
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def avatar(self, ctx, member: discord.Member = None):
        """Get the avatar of a user
        Uses `B.avatar [user]`
        Note: Arguments in brackets [] are optional"""
        member = ctx.author if not member else member

        aembed = discord.Embed(
            title=f"{member}"
        )

        aembed.set_image(url=f"{member.avatar_url}")
        await ctx.send(embed=aembed)
    @commands.command(name="mystbin",aliases=["mb"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def mystbin(self,ctx,*,code):
      """Send your code to [Mystb.in](https://mystb.in). You may use codeblocks(by putting your code inside \`\`\`, followed by the language you want to use) Currently, this bot recognizes python and javascript codeblocks, but will support more in the future.
      Uses `B.mystbin [\`\`\`][language]
      <code>[\`\`\`]`
      Note: Arguments in brackets [] are optional"""
      code = code.strip("```py")
      code = code.strip("```python")
      code = code.strip("```js")
      code = code.strip("```")
      code = code.encode('utf-8')
      async with aiohttp.ClientSession() as cs:
        async with cs.post('https://mystb.in/documents', data = code) as r:
          res = await r.json()
          key = res["key"]
          embed = discord.Embed(timestamp=ctx.message.created_at, title="Mystb.in", description=f"https://mystb.in/{key}")
          msg = await ctx.send(embed=embed)
      try:
        await ctx.message.delete()
      except:
        embed = discord.Embed(timestamp=ctx.message.created_at, title="Mystb.in", description=f"[Mystb.in Link](https://mystb.in/{key})")
        embed.add_field(name="Error in deleting message",value="I was unable to delete your message, this could be because I don't have permissions to. You can still use the Mystb.in link")
        await msg.edit(embed=embed)
    @commands.command(name="google",aliases=["g"])
    @commands.cooldown(5, 600, commands.BucketType.channel)
    async def google(self,ctx,*,query):
        my_api_key = "AIzaSyA5vrTzd9OHvXc09q7oK26wjLVA3K5Y3Xo"
        my_cse_id = "8ffe6dda337341c4b"
        def google_search(search_term, api_key, cse_id, **kwargs):
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
            return res['items']

        results = google_search(
            query, my_api_key, my_cse_id, num=10)
        thisasdf = []
        for result in results:
            thisasdf += [result, ]
        #await ctx.send(thisasdf[0]["title"])
        #await ctx.send(thisasdf[0]["link"])
        #await ctx.send(thisasdf[0]["snippet"])
        #MySource() will take any Iterable argument into it, you can also put in list of embeds
        pages = menus.MenuPages(source=MySource(thisasdf), clear_reactions_after=30)
        await pages.start(ctx)

def setup(client):
    client.add_cog(MainCog(client))
