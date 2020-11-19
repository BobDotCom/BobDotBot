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
THEME_COLOR = discord.Colour.blurple()
# Grab api token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SR_API_TOKEN = os.getenv("SR_API_TOKEN")
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
client = commands.Bot(command_prefix=get_prefix,intents=intents,embed_color = discord.Color.blurple())
#client.remove_command('help')
client.uptime = datetime.utcnow()
owner = client.get_user(client.owner_id)
client.owner_ids = {690420846774321221}
client.load_extension("jishaku")
client.case_insensitive = True
client.sr_api = SR_API_TOKEN
prefixes1 = get_prefix
logs = get_logs

@client.event
async def on_ready():
	client.loop.create_task(Data.auto_update_data())
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
  setattr(ctx, "original_author_id", getattr(ctx, "original_author_id", ctx.author.id))
  owner_reinvoke_errors = (
    commands.MissingAnyRole, commands.MissingPermissions,
    commands.MissingRole, commands.CommandOnCooldown, commands.DisabledCommand
    )

  if ctx.original_author_id in client.owner_ids and isinstance(error, owner_reinvoke_errors):
    return await ctx.reinvoke()
  ignored = (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, commands.CheckFailure, commands.CommandNotFound, commands.DisabledCommand, commands.CommandInvokeError, commands.TooManyArguments, commands.UserInputError, commands.CommandOnCooldown, commands.NotOwner, commands.MissingPermissions, commands.BotMissingPermissions, commands.MaxConcurrencyReached)
  error = getattr(error, 'original', error)


  if isinstance(error, commands.CommandNotFound):
    if ctx.prefix.lower() != "bob ":
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
  elif isinstance(error, commands.MaxConcurrencyReached):
    await ctx.send(embed=discord.Embed(color=0xff0000).set_footer(text=f"Seems like {error}.", icon_url=ctx.author.avatar_url))
@client.event
async def on_message(message):
	await client.process_commands(message)
	if str(message.guild.id) not in Data.server_data:
            Data.server_data[str(message.guild.id)] = Data.create_new_data()

	data = Data.server_data[str(message.guild.id)]
	if client.user.mentioned_in(message):
            try:
                if message.channel.last_message.author == client.user:
                    return
            except:
                pass
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
    return ctx.message.author.id != 0
for filename in os.listdir('./cogs'):
    try:
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
    except:
    	continue


server_timer.start()
# token
client.run(DISCORD_TOKEN)
