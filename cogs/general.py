# All 25 of the gay imports
import discord
import os
import asyncio
import datetime
import time
import sr_api
import json
from termcolor import cprint
import aiohttp
from googleapiclient.discovery import build
import sqlite3
import aiosqlite
from dotenv import load_dotenv
from datetime import datetime
from sqlite3 import Error
from humanize import precisedelta as nd
from discord.ext import commands
#from .otherscripts import cheks, formats, time
from otherscripts.paginator import RoboPages
from jishaku.codeblocks import codeblock_converter
from discord.ext import menus
load_dotenv()
MONITOR_TOKEN = os.getenv("MONITOR_TOKEN")
SR_API_TOKEN = os.getenv("SR_API_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
api = sr_api.Client(SR_API_TOKEN)
# Create an instance of a class
# Create an instance of a class
class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
      try:
        #entries will be each element of your passed list.
        embed = discord.Embed(title=entries["title"], url=entries["link"], description=entries["snippet"])
        #try:
            #embed.set_thumbnail(url=entries["pagemap"]["cse_thumbnail"][0]["src"])
        #except:
            #try:
                #embed.set_thumbnail(url=entries["pagemap"]["thumbnail"][0]["src"])
            #except:
                #pass
        try:
            x = entries["pagemap"]["metatags"][0]["og:image"]
            if x[:6] == "https:":
                embed.set_image(url=entries["pagemap"]["metatags"][0]["og:image"])
            elif x[:5] != "http:":
                embed.set_image(url="https:" + entries["pagemap"]["metatags"][0]["og:image"])
        except:
            pass
        embed.set_footer(text=f"Result {menu.current_page + 1}/{menu._source.get_max_pages()}")
      except:
        embed = discord.Embed(title="Error",description="Please press either the left or right button, I was unable to display this page")
      return embed
class BotHelpPageSource(menus.ListPageSource):
    def __init__(self, help_command, commands):
        # entries = [(cog, len(sub)) for cog, sub in commands.items()]
        # entries.sort(key=lambda t: (t[0].qualified_name, t[1]), reverse=True)
        super().__init__(entries=sorted(commands.keys(), key=lambda c: c.qualified_name), per_page=3)
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
async def apiPing():
    start = time.perf_counter()
    await api.get_joke()
    end = time.perf_counter()
    duration = int((end - start) * 1000)
    return duration 
class MemberRoles(commands.MemberConverter):
    async def convert(self, ctx, argument):
        member = ctx.author if not argument else await super().convert(ctx, argument)
        return [role.mention for role in member.roles[1:]] # Remove everyone role!

class MainCog(commands.Cog, name = "General"):
    """General commands that anyone can use"""

    def __init__(self, client):
        self.client = client
        self.bot = client
        self.client.sniper = {}
        self.client.uptime1 = datetime.utcnow()
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
      async with aiosqlite.connect("logs.db") as connection:
        async with connection.cursor() as cursor:
          await cursor.execute("CREATE TABLE IF NOT EXISTS suggestions (id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER, content TEXT, status TEXT, messageid INTEGER);")
          await cursor.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER, content TEXT, status TEXT, messageid INTEGER);")
          await connection.commit()
      async with aiosqlite.connect("emojis.db") as connection:
        async with connection.cursor() as cursor:
          await cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER, status INTEGER);")
          await connection.commit()
    @commands.Cog.listener()
    async def on_message_delete(self,message):
      channel = message.channel.id
      guild = message.guild.id
      try:
        self.client.sniper[guild][channel] = {"author": f"{message.author}", "content": message.content, "avatar": message.author.avatar_url}
      except:
        self.client.sniper[guild] = {}
        self.client.sniper[guild][channel] = {"author": f"{message.author}", "content": message.content, "avatar": message.author.avatar_url}
    @commands.command()
    async def snipe(self,ctx):
      """See the last message that someone deleted from chat"""
      try:
        x = self.client.sniper[ctx.guild.id][ctx.channel.id]
        title = x["author"]
        content = x["content"]
        avatar = x["avatar"]
      except:
        title = None
        content = "There is nothing to snipe!"
      embed = discord.Embed(title="Sniped message content:",description=content,timestamp=ctx.message.created_at)
      if title:
        embed.set_author(name=title,icon_url=avatar)
      await ctx.send(embed=embed)
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.channel_id == 751834280929525791 and payload.member.id == self.client.owner_id:
            if payload.emoji.name == "✅":
                async with aiosqlite.connect('logs.db') as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("SELECT * FROM suggestions WHERE messageid = ?",(payload.message_id,))
                        rows = await cursor.fetchone()
                        if rows[3] == "submitted":
                            what = "Approved"
                            color = discord.Color.yellow()
                        elif rows[3] == "approved":
                            what = "Completed"
                            color = discord.Color.green()
                        else:
                            return
                        try:
                            await payload.member.send(f"Your suggestion has been {what.lower()}: `{rows[2]}`")
                        except:
                            pass
                        message = await self.client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji,payload.member)
                        await message.edit(embed=discord.Embed(title="Suggestion",description=rows[2],color=color,timestamp=datetime.utcnow()).set_footer(text=what).set_author(name=payload.member,icon_url=payload.member.avatar_url))
                        await cursor.execute("UPDATE suggestions SET status = ? WHERE messageid = ?",(what.lower(),payload.message_id,))
                        await connection.commit()
            elif payload.emoji.name == "❎":
                async with aiosqlite.connect('logs.db') as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("SELECT * FROM suggestions WHERE messageid = ?",(payload.message_id,))
                        rows = await cursor.fetchone()
                        if rows[3] == "declined":
                            return
                        what = "Declined"
                        color = discord.Color.red()
                        try:
                            await payload.member.send(f"Your suggestion has been {what.lower()}: `{rows[2]}`")
                        except:
                            pass
                        message = await self.client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji,payload.member)
                        await message.edit(embed=discord.Embed(title="Suggestion",description=rows[2],color=color,timestamp=datetime.utcnow()).set_footer(text=what).set_author(name=payload.member,icon_url=payload.member.avatar_url))
                        await cursor.execute("UPDATE suggestions SET status = ? WHERE messageid = ?",(what.lower(),payload.message_id,))
                        await connection.commit()
                
        elif payload.channel_id == 751971356865986731 and payload.member.id == self.client.owner_id:
            if payload.emoji.name == "✅":
                async with aiosqlite.connect('logs.db') as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("SELECT * FROM reports WHERE messageid = ?",(payload.message_id,))
                        rows = await cursor.fetchone()
                        if rows[3] == "reported":
                            what = "Verified"
                            color = discord.Color.yellow()
                        elif rows[3] == "verified":
                            what = "Fixed"
                            color = discord.Color.green()
                        else:
                            return
                        try:
                            await payload.member.send(f"Your bug report has been {what.lower()}: `{rows[2]}`")
                        except:
                            pass
                        message = await self.client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji,payload.member)
                        await message.edit(embed=discord.Embed(title="Bug Report",description=rows[2],color=color,timestamp=datetime.utcnow()).set_footer(text=what).set_author(name=payload.member,icon_url=payload.member.avatar_url))
                        await cursor.execute("UPDATE reports SET status = ? WHERE messageid = ?",(what.lower(),payload.message_id,))
                        await connection.commit()
            elif payload.emoji.name == "❎":
                async with aiosqlite.connect('logs.db') as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("SELECT * FROM reports WHERE messageid = ?",(payload.message_id,))
                        rows = await cursor.fetchone()
                        if rows[3] == "declined":
                            return
                        what = "Declined"
                        color = discord.Color.red()
                        try:
                            await payload.member.send(f"Your bug report has been {what.lower()}: `{rows[2]}`")
                        except:
                            pass
                        message = await self.client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji,payload.member)
                        await message.edit(embed=discord.Embed(title="Bug Report",description=rows[2],color=color,timestamp=datetime.utcnow()).set_footer(text=what).set_author(name=payload.member,icon_url=payload.member.avatar_url))
                        await cursor.execute("UPDATE reports SET status = ? WHERE messageid = ?",(what.lower(),payload.message_id,))
                        await connection.commit()
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
            """See how long the bot has been online"""
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
        """Ur nub"""
        await ctx.send("NOOOOOB")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def invite(self, ctx, bot: discord.Member = None, permissions = None):
        """Invite a bot to your server! Defaults to me, but you can mention another bot to get their invite too"""
        bot = bot or self.client.user
        if not bot.bot:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(),title="Error",description="That's not a bot, that's a user."))
        permissions = permissions or "none"
        permissions = permissions if permissions.lower() in ["normal","admin"] else "admin" if bot == self.client.user else "normal"
        permissions = 8 if permissions.lower() == "admin" else 0
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title=f"Bot invite for: {bot.name}", timestamp=ctx.message.created_at, description=f"Link: [Click Here]({str(discord.utils.oauth_url(bot.id, discord.Permissions(permissions=permissions), guild=ctx.guild))})")
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def add(self, ctx, a: int, b: int):
        """I'm learning new math, but I only do addition for now. I'm pretty fast at it though!"""
        answer = (a + b)
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Math", timestamp=ctx.message.created_at, description="I think the answer to that is **" + str(answer) + "**") 
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def slap(self, ctx, members: commands.Greedy[discord.Member], *, reason='no reason'):
        """Use this to slap someone
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
        """Use the bot to say something"""
        quote = arg
        author = ctx.author.name
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title=f"{author} says:", timestamp=ctx.message.created_at, description=f'{quote}')
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedVar)

    @commands.command(aliases=['pong'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def ping(self, ctx):
        """Checks the latency of the bot (lower is better)"""
        ping = int(self.client.latency * 1000)
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title="***PONG!***  :ping_pong:", timestamp=ctx.message.created_at, description=f"My websocket ping is: **{ping}ms**")
        embedVar.set_footer(text=f"Getting database ping")
        message = await ctx.send(embed=embedVar)
        db_start = time.perf_counter()
        async with aiosqlite.connect('users.db') as connection:
            async with connection.cursor() as cursor:
                pass
        db_end = time.perf_counter()
        embedVar.add_field(name="Database ping",value=f'*{(db_end - db_start) * 1000:,.2f}ms*')
        embedVar.set_footer(text=f"Getting total ping")
        start = time.perf_counter()
        await message.edit(embed=embedVar)
        end = time.perf_counter()
        duration = int((end - start) * 1000)
        embedVar.add_field(name="Total ping",value="*" + str(duration) + "ms*")
        embedVar.set_footer(text=f"Getting API ping")
        await message.edit(embed=embedVar)
        try:
            api_ping = None
            api_ping = await asyncio.wait_for(apiPing(), timeout=5.0)
        except asyncio.TimeoutError:
            embedVar.add_field(name="API ping",value="API did not respond")
            api_ping = False
        if api_ping:
            embedVar.add_field(name="API ping",value="*" + str(api_ping) + "ms*")
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await message.edit(embed=embedVar)
        
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def porn(self, ctx):
        """Use if you are really horny"""
        await ctx.send("Shut up, horny kid.")


    @commands.command(aliases=["credit", "owner"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def credits(self, ctx):
        """Shows the credits for the bot"""
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
        embed.add_field(name=f'{yo56789}', value=f'Yo56789 helped me get started when I was new.', inline=False)
        embed.add_field(name=f'Servers', value=f'{tcc} -- This was the first server that I got help from, and they are quite active and able to help.\n{dpy} -- This is the official discord.py server, and it has an extremely active help chat, where you can get help with almost anything about discord.py.', inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['xp', 'rank', 'levels'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def level(self, ctx, member: discord.Member = None):
        """Lists a user's level. You can level up by talking in any channel/server that the bot is in"""
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
        """Ligmabols"""
        await ctx.send("slurp")

    @commands.command(aliases=['suggestion'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def suggest(self, ctx, *, suggestion):
        """Make a suggestion about the bot, it can be a new command that you would like to see, or anything else that you want to suggest. NOTE: do not use this command for bugs. To report a bug, use the bug command."""
        embed = discord.Embed(timestamp=ctx.message.created_at, title='Success!',description='Also, consider joining the support server: [Click here](https://discord.gg/3seAXGr)')
        c = self.client.get_guild(727739470731935765).get_channel(751834280929525791)
        embed1 = discord.Embed(title="Suggestion",description=suggestion,timestamp=ctx.message.created_at)
        embed1.set_footer(text="Submitted")
        embed1.set_author(name=ctx.author,icon_url=ctx.author.avatar_url)
        msg = await c.send(embed=embed1)
        async with aiosqlite.connect('logs.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO suggestions (userid, content, status, messageid) VALUES (?,?,?,?);",(ctx.author.id,suggestion,"submitted",msg.id,))
                await connection.commit()
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❎')
        await ctx.send(embed=embed)

    @commands.command(aliases=['bugs'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def bug(self, ctx, *, report):
        """Let the owner know about a bug in the bot. NOTE: do not use this command for suggestions. To make a suggestion, use the suggestion command."""
        embed = discord.Embed(timestamp=ctx.message.created_at, title='Success!',description='Also, consider joining the support server: [Click here](https://discord.gg/3seAXGr)')
        c = self.client.get_guild(727739470731935765).get_channel(751971356865986731)
        embed1 = discord.Embed(title="Bug Report",description=report,timestamp=ctx.message.created_at)
        embed1.set_footer(text="Reported")
        embed1.set_author(name=ctx.author,icon_url=ctx.author.avatar_url)
        msg = await c.send(embed=embed1)
        async with aiosqlite.connect('logs.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO reports (userid, content, status, messageid) VALUES (?,?,?,?);",(ctx.author.id,report,"reported",msg.id,))
                await connection.commit()
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❎')
        await ctx.send(embed=embed)
    @commands.command(aliases=["emoji"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def emoji_id(self,ctx,emoji: discord.Emoji):
        """Get the ID of any custom emoji that the bot can see"""
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
    @commands.command(name="serverinfo", aliases=["si"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def serverinfo(self, ctx):
        """Get the info of the server that you are in"""
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
        """Get the avatar of a user"""
        member = ctx.author if not member else member

        aembed = discord.Embed(
            title=f"{member}"
        )

        aembed.set_image(url=f"{member.avatar_url}")
        await ctx.send(embed=aembed)
    @commands.command(name="mystbin",aliases=["mb"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def mystbin(self,ctx,*,code: codeblock_converter = None):
      """Send your code to [Mystb.in](https://mystb.in). You may use codeblocks(by putting your code inside \`\`\`, followed by the language you want to use) Currently, this bot recognizes python and javascript codeblocks, but will support more in the future."""
      code = code.content if code else None
      if len(ctx.message.attachments) != 0:
        for attachment in ctx.message.attachments:
            print(attachment.filename)
            if attachment.filename[-4:] == ".txt":
                code = await attachment.read()
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
        """Google something. Returns the first 10 results. Has a cooldown to avoid hitting the google api ratelimit."""
        my_api_key = GOOGLE_API_KEY
        my_cse_id = GOOGLE_CSE_ID
        def google_search(search_term, api_key, cse_id, **kwargs):
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
            try:
                return res['items']
            except:
                print(res)
                return

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
    @commands.command(name="rules",aliases=["ruleschannel"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def rule(self,ctx):
        """Get the rule channel in the current server"""
        rules = ctx.guild.rules_channel
        if rules:
            text = f"Hey, your rules channel is {rules.mention}"
        else:
            rules_channel = None
            if "COMMUNITY" in ctx.guild.features:
                for channel in ctx.guild.channels:
                    if "rules" in channel.name.lower():
                        rules_channel = channel
                        break
                if rules_channel:
                    text = f"I think that your rules channel is {rules_channel.mention}, but I am not sure, because this server is not a community server! Please ask an admin to enable communitry server and set a rules channel, so I can be sure"
                else:
                    text = f"I couldn't find a rules channel, because this server is not a community server! Please ask an admin to enable communitry server and set a rules channel, so I can be sure"
            else:
                for channel in ctx.guild.channels:
                    if "rules" in channel.name.lower():
                        rules_channel = channel
                        break
                if rules_channel:
                    text = f"I think that your rules channel is {rules_channel.mention}, but I am not sure, because this server does not have a rules channel set! Please ask an admin to set a rules channel in the community server settings, so I can be sure"
                else:
                    text = f"I couldn't find a rules channel, because this server does not have a rules channel set! Please ask an admin to set a rules channel in the community server settings, so I can be sure"
        embed = discord.Embed(title="Rules Channel", description=text,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command(name="github",aliases=["source","info"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def github(self,ctx):
        """Get my github link"""
        await ctx.send("https://github.com/BobDotCom/BobDotBot")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def autoemoji(self,ctx):
        """Toggle autoemoji"""
        async with aiosqlite.connect("emojis.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT status FROM users WHERE userid = ?",(ctx.author.id,))
                row = await cursor.fetchone()
                if not row:
                    await cursor.execute("INSERT INTO users (userid, status) VALUES (?,?)",(ctx.author.id,"true",))
                    await connection.commit()
                    await ctx.send("Enabled autoemoji")
                    return
                if row[0] == "true":
                    set_to = "false"
                    self.client.emoji_users.remove(ctx.author.id)
                    await ctx.send("Disabled autoemoji")
                else:
                    set_to = "true"
                    self.client.emoji_users = self.client.emoji_users.append(ctx.author.id)
                    await ctx.send("Enabled autoemoji")
                await cursor.execute("UPDATE users SET status = ? WHERE userid = ?",(set_to,ctx.author.id))
                await connection.commit() 
def setup(client):
    client.add_cog(MainCog(client))
