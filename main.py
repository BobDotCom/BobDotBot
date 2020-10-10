# import stuff
import discord
import json
# import stuff
import os

# import stuff
import typing
import asyncio
import datetime
# import stuff
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime
from discord.ext.tasks import loop
from otherscripts.data import Data


# Load .env file
load_dotenv()

# Grab api token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# gets client stuff
def get_prefix(client, message):
	if not message.guild:
		return ['B!', 'b!']
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)
	return prefixes[str(message.guild.id)]
def get_logs(client, message):
	if not message.guild:
		return ["None"]
	with open('logs.json', 'r') as f1:
		logs = json.load(f1)
	return logs[str(message.guild.id)]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=get_prefix,intents=intents)
client.remove_command('help')
client.uptime = datetime.utcnow()
owner = client.get_user(client.owner_id)
client.owner_id = 690420846774321221
client.load_extension("jishaku")
prefixes1 = get_prefix
logs = get_logs
@client.event
async def on_ready():
	# server counter
	guild_count = 0
	users = 0
	# gets guild info
	for guild in client.guilds:

		# prints guild name
		print(f"- {guild.id} (name: {guild.name})")

		# guild counter
		guild_count = guild_count + 1
		for member in guild.members:
			users = users + 1

	# prints amount of servers
	print("BobDotBot is in " + str(guild_count) + " guilds.")
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Bot starting up..."))

@client.event
async def on_command_error(ctx, error):
  if hasattr(ctx.command, 'on_error'):
    return

  ignored = (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, commands.CheckFailure, commands.CommandNotFound, commands.DisabledCommand, commands.CommandInvokeError, commands.TooManyArguments, commands.UserInputError, commands.CommandOnCooldown, commands.NotOwner, commands.MissingPermissions, commands.BotMissingPermissions)
  error = getattr(error, 'original', error)


  if isinstance(error, commands.CommandNotFound):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Sorry, {error}. Use my help command for a command list", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.BadArgument):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like {error}.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like {error}.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.NoPrivateMessage):
    return

  elif isinstance(error, commands.CheckFailure):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"You do not have the required permissions to run this command", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.DisabledCommand):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like this command in disabled.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.CommandInvokeError):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like something went wrong. Report this issue to the developer.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.TooManyArguments):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like you gave too many arguments.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.UserInputError):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like you did something wrong.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.CommandOnCooldown):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like {error}.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.NotOwner):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like you do not own this bot.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.MissingPermissions):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like {error}.", icon_url=ctx.author.avatar_url))

  elif isinstance(error, commands.BotMissingPermissions):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like {error}.", icon_url=ctx.author.avatar_url))
@client.event
async def on_message(message):
	await client.process_commands(message)
	if client.user.mentioned_in(message):
            if message.mention_everyone is False:
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
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)
	prefixes[str(guild.id)] = ['B.', 'b.']
	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)
	for guild in client.guilds:
		# prints guild name

		# guild counter
		guild_count = guild_count + 1
		for member in guild.members:
			users = users + 1

	# prints amount of servers
	print("BobDotBot is now in " + str(guild_count) + " guilds.")
	#await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"" + str(guild_count) + f" servers | " + str(users) + " users"))

@loop(seconds=0)
async def server_timer():
	await client.wait_until_ready()
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
    guildvar = client.get_guild(727739470731935765)
    welcome = guildvar.get_channel(755259446724263996)
    roles = guildvar.get_channel(762721025912733696)
    rules = guildvar.get_channel(747275116194431088)
    if member.guild == guildvar:
        human = guildvar.get_role(745834807258251325)
        badges = guildvar.get_role(762684938226630666)
        members = guildvar.get_role(762684570474643507)
        colors = guildvar.get_role(762718919764082710)
        await member.add_roles(human)
        await member.add_roles(badges)
        await member.add_roles(members)
        await member.add_roles(colors)
        if not member.bot:
            await welcome.send(f"Hello {member.mention}, welcome to {member.guild.name}! Please read the {rules.mention} and have fun! You can get your roles at {roles.mention}.")
@client.event
async def on_member_remove(member):
    """on member remove"""
    guildvar = client.get_guild(727739470731935765)
    channelvar = guildvar.get_channel(755259446724263996)
    if member.guild == guildvar:
        await channelvar.send(f"Oh no! {member.name} left the server! We hope you had fun and will come back!")
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

@client.command(aliases=['r'])
@commands.is_owner()
async def reload(ctx, extension):
    """Reloads the specified Cog"""
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print(f'Cog "{extension}" was reloaded')
    await ctx.send(f'Reloaded Cog "{extension}"')

@client.command(aliases=['ra'])
@commands.is_owner()
async def reloadall(ctx):
    """Reloads all Cogs"""
    print('All Cogs were reloaded{')
    firstTime = True
    reloaded = []
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
                client.reload_extension(f'cogs.{filename[:-3]}')
                reloaded += [filename[:-3], ]
                if firstTime:
                        embedvar = discord.Embed(title='Reloading Cogs...', description='If you see this message for more than 10 seconds, an error most likely occurred, no cogs were reloaded')
                        msg = await ctx.send(embed=embedvar)
                        firstTime = False
                else:
                        embedvar1 = discord.Embed(title='Reloading Cogs...', description=f"Reloaded cog(s): {', '.join(reloaded)}", color=0xff0000)
                        await msg.edit(embed=embedvar1)
                print(f'Cog: {filename[:-3]} was reloaded')
                #await ctx.send(f'Cog: {filename[:-3]} was reloaded')
    print('}')
    embedvar = discord.Embed(title='Success!', description="Successfully reloaded all Cogs", color=0x00ff00)
    await ctx.send(embed=embedvar)


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
@client.command(name="activateautomod")
@commands.has_guild_permissions(administrator=True)
async def activateautomod(ctx):
    if str(ctx.guild.id) not in Data.server_data:
        Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

    Data.server_data[str(ctx.guild.id)]["active"] = True
    await ctx.send("Automod is now active in your server...")


@client.command(name="stopautomod")
@commands.has_guild_permissions(administrator=True)
async def stopautomod(ctx):
    if str(ctx.guild.id) not in Data.server_data:
        Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

    Data.server_data[str(ctx.guild.id)]["active"] = False
    await ctx.send("Automod is now inactive in your server...")


@client.command(name="whitelistuser")
@commands.has_guild_permissions(administrator=True)
async def whitelistuser(ctx, user: discord.User = None):
    if user is None:
        ctx.send("Insufficient Arguments")
    else:
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["users"].append(str(user.id))
        await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")


@client.command(name="whitelisturl")
@commands.has_guild_permissions(administrator=True)
async def whitelisturl(ctx, url: str = None):
    if url is None:
        ctx.send("Insufficient Arguments")
    else:
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["urls"].append(url)
        await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")


@client.command(name="whitelistchannel")
@commands.has_guild_permissions(administrator=True)
async def whitelistchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        ctx.send("Insufficient Arguments")
    else:
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["channels"].append(
            str(channel.id))
        await ctx.send(f"Added {channel.mention} to AutoMod Channel whitelist.")


@client.command(name="automodstatus")
async def automodstatus(ctx):
    status = Data.server_data[str(ctx.guild.id)]["active"]
    await ctx.send(f"AutoMod Active: **{status}**")
@client.check
def blacklist(ctx):
    return ctx.message.author.id != 706898741499789364
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


server_timer.start()
# token
client.run(DISCORD_TOKEN)
