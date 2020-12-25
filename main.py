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
import json
# import stuff
import os
import time
# import stuff
import typing
import asyncio
import aiosqlite
import datetime
import sys
import math 
import humani
import traceback
# import stuff
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime
from discord.ext.tasks import loop
from otherscripts.data import Data
from halo import Halo
from stringcolor import * 
start_time = time.perf_counter()

# Load .env file
load_dotenv()
THEME_COLOR = discord.Colour.blurple()
# Grab api token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SR_API_TOKEN = os.getenv("SR_API_TOKEN")
DBL_TOKEN = os.getenv("DBL_TOKEN")
# gets client stuff
def get_prefix(client, message):
	if not message.guild:
		return ['B!', 'b!']
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)
	try:
		x = prefixes[str(message.guild.id)]
	except:
		x = ["B.","b."]
	if x == []:
		x += ["B.","b.",]
	if not client.user.id == 745044803732897802:
		return commands.when_mentioned_or(*x)(client, message)
	else:
		y = ['B,','b,','Bob,','bob,']
		return commands.when_mentioned_or(*y)(client, message)
def get_logs(client, message):
	if not message.guild:
		return ["None"]
	with open('logs.json', 'r') as f1:
		logs = json.load(f1)
	return logs[str(message.guild.id)]

intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_prefix,intents=intents,embed_color = discord.Color.blurple(),case_insensitive = True)
try:
    with open('blacklisted.json','r') as f:
        data = json.load(f)
    client.blacklisted = data['users']
except:
    client.blacklisted = []
    print('Blacklist not loaded')
#client.remove_command('help')
client.uptime = datetime.utcnow()
owner = client.get_user(client.owner_id)
client.owner_id = None
client.owner_ids = [690420846774321221,748937160731918378]
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ['JISHAKU_RETAIN'] = "True"
client.load_extension("jishaku")
client.sr_api = SR_API_TOKEN
prefixes1 = get_prefix
logs = get_logs
client.dbltoken = DBL_TOKEN
connect_spinner = Halo(text='Connecting', spinner='dots')
start_spinner = Halo(text='Starting up', spinner='dots')

@client.event
async def on_connect():
    try:
        connect_spinner.succeed('Connected')
    except:
        pass
    start_spinner.start()

@client.event
async def on_ready():
    end_time = time.perf_counter()
    try:
        start_spinner.succeed('Ready')
    except:
        pass
    print(f"Bot online.\nStats:\n• Python {sys.version} on {sys.platform}\n• discord.py {discord.__version__}".replace(' \n',' '))

    cache_summary = f"{len(client.guilds)} guilds and {len(client.users)} users"
    if isinstance(client, discord.AutoShardedClient):
        print(f"{client.user.name} is automatically sharded ({len(client.shards)} shards) and can see {cache_summary}.")
    elif client.shard_count:
        print(f"{client.user.name} is manually sharded ({len(client.shards)} shards) and can see {cache_summary}.")
    else:
        print(f"{client.user.name} is not sharded and can see {cache_summary}.")
    print(cs('Bot is ready','green'))
    total_time = int((end_time - start_time))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Bot starting up... | Startup took {total_time} seconds"))

async def log_error(ctx,error,handled):
    if not handled:
        title = 'Ignoring exception in command {}:'.format(ctx.command)
        err = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        try:
            channel = client.get_channel(787461422896513104)
            embed = discord.Embed(title=title,description=f'```py\n{err}```',timestamp=ctx.message.created_at,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url)
            await channel.send(embed=embed)
        except:
            try:
                channel = client.get_channel(787461422896513104)
                await channel.send(f"{client.get_user(client.owner_ids[0]).mention} **An error occurred but for an unknown reason, I couldn't log it here**")
            except:
                pass
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        finally:
            return
    else:
        err = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        title = 'Ignoring exception in command {}:'.format(ctx.command)
        try:
            channel = client.get_channel(787476834689744926)
            embed = discord.Embed(title=title,description=f'```py\n{err}```',timestamp=ctx.message.created_at,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url)
            await channel.send(embed=embed)
        except:
            try:
                channel = client.get_channel(787476834689744926)
                await channel.send(f"{client.get_user(client.owner_ids[0]).mention} **An error occurred but for an unknown reason, I couldn't log it here**")
            except:
                pass
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        finally:
            pass

@client.event
async def on_command_error(ctx, error):
        exception = error
        if hasattr(ctx.command, 'on_error'):
            pass
        #ignored = (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, commands.CheckFailure, commands.CommandNotFound, commands.DisabledCommand, commands.CommandInvokeError, commands.TooManyArguments, commands.UserInputError, commands.CommandOnCooldown, commands.NotOwner, commands.MissingPermissions, commands.BotMissingPermissions)   
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.BadArgument):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.MissingRequiredArgument):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.NoPrivateMessage):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.CheckFailure):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.DisabledCommand):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.CommandInvokeError):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.TooManyArguments):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.UserInputError):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.CommandOnCooldown):
            await log_error(ctx,exception,True)
            time = datetime.timedelta(seconds=math.ceil(error.retry_after))
            error = f'You are on cooldown. Try again after {humanize.precisedelta(time)}'
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.NotOwner):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.MissingPermissions):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.BotMissingPermissions):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))

        elif isinstance(error, commands.MaxConcurrencyReached):
            await log_error(ctx,exception,True)
            error=str(error)
            await ctx.send(embed=discord.Embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url))
        
        else:
            try:
                embed = discord.Embed(title='Oh no!',description=f"An error occurred. My developer has been notified of it, but you may still report it (`{ctx.prefix}help bug`) if you wish.",color=discord.Color.red())
                await ctx.send(embed=embed)
            except:
                pass
            await log_error(ctx,exception,False)
            
@client.event
async def on_message(message):
	if message.author.id in client.emoji_users and (message.content.startswith(":") or message.content.startswith(";")):
		async with aiosqlite.connect("emojis.db") as connection:
			async with connection.cursor() as cursor:
				await cursor.execute("SELECT status FROM users WHERE userid = ?",(message.author.id,))
				rows = await cursor.fetchone()
		if rows[0] != "false":
			for emoji in client.emojis:
				if emoji.name == message.content[1:-1]:
					return await message.channel.send(emoji)
	await client.process_commands(message)
	if str(message.guild.id) not in Data.server_data:
            Data.server_data[str(message.guild.id)] = Data.create_new_data()

	data = Data.server_data[str(message.guild.id)]
	x = await client.get_context(message)
	if client.user.mentioned_in(message) and not x.valid:
            if not message.mention_everyone:
                with open("prefixes.json","r") as f:
                    prefixes = json.load(f)

                if str(message.guild.id) in prefixes:
                    prefix = prefixes[str(message.guild.id)]

                else:
                    prefix = 'B. or b.'
                owner = client.get_user(client.owner_id)
                # await message.channel.send("Hi, i'm BobDotBot, and my prefix is `B.` If you don't know any of my commands yet, try doing `B.help`, and i will DM you a list of commands that you can use with me!")
                embedVar = discord.Embed(title="Hi, i'm BobDotBot!", description=f"My prefix(es) here: `{', '.join(prefix)}`", color=0x00ff00, timestamp=message.created_at)
                embedVar.add_field(name="What do I do?", value="If you don't know any of my commands yet, try using my `help` command, and I will DM you a list of commands that you can use with me!\nThis message will delete after 15 seconds")
                embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
                msg = await message.channel.send(embed=embedVar)
                await asyncio.sleep(15)
                await msg.delete()


@client.event
async def on_guild_join(guild):
	guild_count = 0
	users = 0
	#Data.server_data[str(guild.id)]["welcome_msg"] = ""
	#Data.server_data[str(guild.id)]["leave_msg"] = ""
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)
	prefixes[str(guild.id)] = ['B.', 'b.']
	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)
	#for guild in client.guilds:
	# prints guild name

	# guild counter
	#guild_count = guild_count + 1
	#for member in guild.members:
	#users = users + 1

	# prints amount of servers
	#print("BobDotBot is now in " + str(guild_count) + " guilds.")
	#await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"" + str(guild_count) + f" servers | " + str(users) + " users"))

@loop(seconds=0)
async def server_timer():
	await client.wait_until_ready()
	async with aiosqlite.connect("emojis.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute("SELECT * FROM users")
			rows = await cursor.fetchall()
	client.emoji_users = [row[1] for row in rows]
	guild_count = 0
	users = 0
	for guild in client.guilds:
		# prints guild name

		# guild counter
		guild_count = guild_count + 1
		for member in guild.members:
			users = users + 1
	await asyncio.sleep(15)
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"" + str(guild_count) + f" servers | " + str(users) + " users"))
	await asyncio.sleep(60)
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"B.help | B.invite"))
	await asyncio.sleep(45)
@client.event
async def on_guild_remove(guild):
  guild_count = 0
  users = 0
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)
  prefixes.pop(str(guild.id))
  with open('prefixes.json', 'w') as f:
	  json.dump(prefixes, f, indent=4)
	#with open('logs.json', 'r') as f1:
		#logs = json.load(f1)
	#logs.pop(str(guild.id))
	#with open('logs.json', 'w') as f1:
		#json.dump(logs, f1, indent=4)
  for guild in client.guilds:
		# prints guild name

		# guild counter
	  guild_count = guild_count + 1
	  for member in guild.members:
		  users = users + 1

	# prints amount of servers
  print("BobDotBot is now in " + str(guild_count) + " guilds.")
  #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"" + str(guild_count) + f" servers | " + str(users) + " users"))
@client.event
async def on_member_join(member):
    """on member join"""
    guild: discord.Guild = member.guild
    channels = guild.channels

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()
    data = Data.server_data[str(guild.id)]

    print(f"{member} has joined {guild} server...")

    join_role = guild.get_role(data["join_role"])
    if join_role is not None:
        await member.add_roles(join_role)

    # Welcome Message
    if data["welcome_msg"] is None:
        server_wlcm_msg = f"Welcome, {member.mention}, to the Official **{guild.name}** Server"
    else:
        server_wlcm_msg = data["welcome_msg"]
        server_wlcm_msg = server_wlcm_msg.replace(
            "{member_mention}", f"{member.mention}")
        server_wlcm_msg = server_wlcm_msg.replace(
            "{member_count}", f"{len(member.guild.members)}")
        server_wlcm_msg = server_wlcm_msg.replace(
            "{server_name}", f"{member.guild.name}")
        server_wlcm_msg = server_wlcm_msg.replace(
            "{member}", f"{member}")
        server_wlcm_msg = server_wlcm_msg.replace(
            "{member_name}", f"{member.name}")
        server_wlcm_msg = server_wlcm_msg.replace(
            "{server_name}", f"{member.guild.name}")

    for channel in channels:
        if str(channel).find("welcome") != -1:
            await channel.send(server_wlcm_msg)
            break
    guildvar = client.get_guild(727739470731935765)
    if member.guild == guildvar:
        human = guildvar.get_role(745834807258251325)
        badges = guildvar.get_role(762684938226630666)
        members = guildvar.get_role(762684570474643507)
        colors = guildvar.get_role(762718919764082710)
        await member.add_roles(human)
        await member.add_roles(badges)
        await member.add_roles(members)
        await member.add_roles(colors)
        
@client.event
async def on_member_remove(member):
    """on member remove"""
    guild: discord.Guild = member.guild
    channels = guild.channels

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()
    data = Data.server_data[str(guild.id)]
    # Welcome Message
    if data["leave_message"] is None:
        server_wlcm_msg = f"Goodbye, {member}"
    else:
        server_wlcm_msg = data["leave_message"]
        server_wlcm_msg = server_wlcm_msg.replace(
            "[member]", f"{member}")

    for channel in channels:
        if str(channel).find("bye") != -1 or str(channel).find("leave") != -1:
            await channel.send(server_wlcm_msg)
            break
@client.command(aliases=['l'])
@commands.is_owner()
async def load(ctx, extension):
    """Loads the specified Cog"""
    client.load_extension(f'cogs.{extension}')
    print(f'Cog "{extension}" was loaded')
    await ctx.send(f'Loaded Cog "{extension}"')

@client.command(aliases=['u'])
@commands.is_owner()
async def unload(ctx, extension):
    """Unloads the specified Cog"""
    client.unload_extension(f'cogs.{extension}')
    print(f'Cog "{extension}" was unloaded')
    await ctx.send(f'Unloaded Cog "{extension}"')

@client.command(aliases=['re'])
@commands.is_owner()
async def reload(ctx, extension):
    """Reloads the specified Cog"""
    client.reload_extension(f'cogs.{extension}')
    print(f'Cog "{extension}" was reloaded')
    await ctx.send(f'Reloaded Cog "{extension}"')

@client.command(aliases=['ra'])
@commands.is_owner()
async def reloadall(ctx):
    """Reloads all Cogs"""
    print('All Cogs were reloaded{')
    reloaded = []
    notr = []
    embedvar = discord.Embed(title='Reloading Cogs...', description='If you see this message for more than 10 seconds, an error most likely occurred, no cogs were reloaded')
    msg = await ctx.send(embed=embedvar)
    debug = client.get_command("jishaku dbg")
    for x in list(client.extensions):
      if x != "jishaku":
        try:
            client.reload_extension(x)
            reloaded += [x[5:], ]
        except:
            notr += [x[5:], ]
        if len(notr) == 0:
            embedvar1 = discord.Embed(title='Reloading Cogs...', description=f"Reloaded cog(s): {', '.join(reloaded)}", color=0xff0000)
        else:
            embedvar1 = discord.Embed(title='Reloading Cogs...', description=f"Reloaded cog(s): {', '.join(reloaded)}\nNot loaded: {', '.join(notr)}", color=0xff0000)
        await asyncio.sleep(1)
        await msg.edit(embed=embedvar1)
        print(f'Cog: {x[5:]} was reloaded')
                #await ctx.send(f'Cog: {filename[:-3]} was reloaded')
    print('}')
    if len(notr) == 0:
        embedvar1 = discord.Embed(title='Reloading Cogs...', description=f"Reloaded cog(s): {', '.join(reloaded)}", color=0x00ff00)
        embedvar1.add_field(name='Success!', value="Successfully reloaded all Cogs")
    else:
        embedvar1 = discord.Embed(title='Reloading Cogs...', description=f"Reloaded cog(s): {', '.join(reloaded)}\nNot loaded: {', '.join(notr)}", color=0xff0000)
        embedvar1.add_field(name='Failure', value="Failed to reload all cogs")
        for x in notr:
            await ctx.invoke(debug, command_string=f"reload {x}")
    await msg.edit(embed=embedvar1)


@client.command(aliases=['la'])
@commands.is_owner()
async def loadall(ctx):
    """Loads all Cogs"""
    print('All Cogs were loaded{')
    firstTime = True
    loaded = []
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
                client.load_extension(f'cogs.{filename[:-3]}')
                loaded += [filename[:-3], ]
                if firstTime:
                        embedvar = discord.Embed(title='Loading Cogs...', description='If you see this message for more than 10 seconds, an error most likely occurred, no cogs were loaded')
                        msg = await ctx.send(embed=embedvar)
                        firstTime = False
                else:
                        embedvar1 = discord.Embed(title='Loading Cogs...', description=f"Loaded cog(s): {', '.join(loaded)}", color=0xff0000)
                        await msg.edit(embed=embedvar1)
                print(f'Cog: {filename[:-3]} was Loaded')
                #await ctx.send(f'Cog: {filename[:-3]} was reloaded')
    print('}')
    embedvar = discord.Embed(title='Success!', description="Successfully Loaded all Cogs", color=0x00ff00)
    await ctx.send(embed=embedvar)

@client.command(aliases=['ua'])
@commands.is_owner()
async def unloadall(ctx):
    """Unloads all Cogs"""
    print('All Cogs were unloaded{')
    firstTime = True
    unloaded = []
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
                client.unload_extension(f'cogs.{filename[:-3]}')
                unloaded += [filename[:-3], ]
                if firstTime:
                        embedvar = discord.Embed(title='Unloading Cogs...', description='If you see this message for more than 10 seconds, an error most likely occurred, no cogs were Unloaded')
                        msg = await ctx.send(embed=embedvar)
                        firstTime = False
                else:
                        embedvar1 = discord.Embed(title='Unloading Cogs...', description=f"Unloaded cog(s): {', '.join(unloaded)}", color=0xff0000)
                        await msg.edit(embed=embedvar1)
                print(f'Cog: {filename[:-3]} was unloaded')
                #await ctx.send(f'Cog: {filename[:-3]} was reloaded')
    print('}')
    embedvar = discord.Embed(title='Success!', description="Successfully unloaded all Cogs", color=0x00ff00)
    await ctx.send(embed=embedvar)

@client.check
def blacklist(ctx):
    return not ctx.message.author.id in client.blacklisted
print("----------Cogs----------")
for filename in os.listdir('./cogs'):
    try:
        if filename.endswith('.py'):
            filename = f'cogs.{filename[:-3]}'
            cog_spinner = Halo(text=filename, spinner='dots')
            cog_spinner.start()
            client.load_extension(filename)
            cog_spinner.succeed()
    except:
    	cog_spinner.fail()
print("")

server_timer.start()
connect_spinner.start()
try:
    client.run(DISCORD_TOKEN)
except:
    connect_spinner.fail('Failed to connect')
