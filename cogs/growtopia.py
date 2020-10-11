# import stuff
import discord

# import stuff
import os
import json
# import stuff
import typing
import asyncio
import aiohttp
import requests
import datetime
# import stuff
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime

class GrowtopiaCog(commands.Cog, name = "Growtopia"):
    """Commands relating to the online sandbox game, Growtopia"""

    def __init__(self, client):
        self.client = client
        self.client.uptime = datetime.utcnow()
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221

    @commands.Cog.listener()
    async def on_ready(self):
        print('GrowtopiaCog is active')

    @commands.command(aliases=["rw"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def renderworld(self,ctx,arg):
        """Get a world render of any rendered world in Growtopia
        Uses: `B.renderworld <world>`"""
        try:
            embed = discord.Embed(color=discord.Color.blurple(), timestamp=ctx.message.created_at, title=f"Here is a render of the world: {arg}")
            embed.set_image(url=f"https://s3.amazonaws.com/world.growtopiagame.com/{arg}.png")
        except:
            embed = discord.Embed(color=discord.Color.red(), timestamp=ctx.message.created_at, title=f"That world hasn't been rendered yet")
        await ctx.send(embed=embed)
    @commands.command(aliases=["gt"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def online(self,ctx):
        """See how many people are playing the game right now
        Uses: `B.online`"""
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://growtopiagame.com/detail") as resp:
              data = await resp.json(content_type="text/html")
              data = data["online_user"]
        embed = discord.Embed(color=discord.Color.blurple(), timestamp=ctx.message.created_at, title=f"Growtopia stats", description=f"Players online: {data}")
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(GrowtopiaCog(client))
