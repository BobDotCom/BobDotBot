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

class BlockCorpCog(commands.Cog, name = "BlockCorp"):
    """Commands for the BlockCorp staff"""

    def __init__(self, client):
        self.client = client
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221

    @commands.command(aliases=["bc"])
    @commands.is_owner()
    async def blockcorp(self,ctx):
        """Poggers"""
        await ctx.send("test")

def setup(client):
    client.add_cog(BlockCorpCog(client))
