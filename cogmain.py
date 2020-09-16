# import stuff
import discord

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


# Load .env file
load_dotenv()

# Grab api token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# gets client stuff
client = discord.Client()
client = commands.Bot(command_prefix=['B.', 'b.'])
client.remove_command('help')
client.uptime = datetime.utcnow()
owner = client.get_user(client.owner_id)
client.owner_id = 690420846774321221
client.load_extension("jishaku")

@client.event
async def on_ready():
	# server counter
	guild_count = 0

	# gets guild info
	for guild in client.guilds:
		# prints guild name
		print(f"- {guild.id} (name: {guild.name})")

		# guild counter
		guild_count = guild_count + 1

	# prints amount of servers
	print("BobDotBot is in " + str(guild_count) + " guilds.")
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="" + str(guild_count) + " servers"))

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
    await ctx.send('Reloading all Cogs...')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.unload_extension(f'cogs.{filename[:-3]}')
            client.load_extension(f'cogs.{filename[:-3]}')
            print(f'Cog: {filename[:-3]} was reloaded')
            await ctx.send(f'Cog: {filename[:-3]} was reloaded')
    print('}')
    await ctx.send('Successfully reloaded all Cogs')

@client.command(aliases=['la'])
@commands.is_owner()
async def loadall(ctx):
    """Loads all Cogs"""
    print('All Cogs were loaded{')
    await ctx.send('Loading all Cogs...')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            print(f'Cog: {filename[:-3]} was loaded')
            await ctx.send(f'Cog: {filename[:-3]} was loaded')
    print('}')
    await ctx.send('Successfully loaded all Cogs')

@client.command(aliases=['ua'])
@commands.is_owner()
async def unloadall(ctx):
    """Loads all Cogs"""
    print('All Cogs were unloaded{')
    await ctx.send('Unloading all Cogs...')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.unload_extension(f'cogs.{filename[:-3]}')
            print(f'Cog: {filename[:-3]} was unloaded')
            await ctx.send(f'Cog: {filename[:-3]} was unloaded')
    print('}')
    await ctx.send('Successfully unloaded all Cogs')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

# token
client.run(DISCORD_TOKEN)
