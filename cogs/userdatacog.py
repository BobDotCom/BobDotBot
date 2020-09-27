# import stuff
import discord

# import stuff
import os
import json
# import stuff
import typing
import asyncio
import datetime
import sqlite3
import sys
# import stuff
from dotenv import load_dotenv
from sqlite3 import Error
from termcolor import colored, cprint
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime

class Levels(commands.Cog, name = "User database"):
    """There are no commands in this category"""

    def __init__(self, client):
        self.client = client
        self.client.owner_id = 690420846774321221


        with open("users.json", 'r') as f:
            self.users = json.load(f)


        self.client.loop.create_task(self.save_users())

    async def save_users(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            json.dump(self.users, open("users.json", "w"), indent=4)


            await asyncio.sleep(60)

    def lvl_up(self, author_id):
        cur_xp = self.users[author_id]['exp']
        cur_lvl = self.users[author_id]['level']

        if cur_xp >= round((4 * (cur_lvl ** 3)) / 7):
            self.users[author_id]['level'] += 1
            return True
        else:
            return False
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if message.author.bot: return
        author_id = str(message.author.id)
        if author_id in self.users:
            self.users[author_id]['exp'] += 1
        else:
            self.users[author_id] = {}
            self.users[author_id]['level'] = 1
            self.users[author_id]['exp'] = 1



        if self.lvl_up(author_id):
            await message.channel.send(f"{message.author.mention} is now level {self.users[author_id]['level']}")


    @commands.Cog.listener()
    async def on_ready(self):
        print('UserDataCog is active')

def setup(client):
    client.add_cog(Levels(client))
