import discord
import os
import random
import typing
import asyncio
import datetime
import zlib
import functools
import io
import time
import sr_api
import re
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
from .utils import fuzzy
from collections import OrderedDict, deque, Counter
import copy
import unicodedata
import inspect
import itertools
from typing import Union
from datetime import datetime
from discord.ext.commands import MissingPermissions
from jishaku.codeblocks import codeblock_converter
from discord.ext import menus

class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')

class ProgrammingCog(commands.Cog, name = "Programming"):
    """Commands for programmers"""

    def __init__(self, client):
        self.client = client
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221
        self.client.session = aiohttp.ClientSession(loop=self.client.loop)

    @commands.Cog.listener()
    async def on_ready(self):
        print('ProgrammingCog is active')
    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result
    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            sub = cache[key] = {}
            async with self.bot.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    raise RuntimeError('Cannot build rtfm lookup table, try again later.')

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache
    async def do_rtfm(self, ctx, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
            'python': 'https://docs.python.org/3',
            'python-jp': 'https://docs.python.org/ja/3',
        }

        if obj is None:
            await ctx.send(page_types[key])
            return

        if not hasattr(self, '_rtfm_cache'):
            await ctx.trigger_typing()
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            # point the abc.Messageable types properly:
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())
        def transform(tup):
            return tup[0]

        matches = fuzzy.finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(colour=discord.Colour.blurple())
        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry.')

        e.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
        await ctx.send(embed=e)

    def transform_rtfm_language_key(self, ctx, prefix):
        if ctx.guild is not None:
            #                             日本語 category
            if ctx.channel.category_id == 490287576670928914:
                return prefix + '-jp'
            #                    d.py unofficial JP
            elif ctx.guild.id == 463986890190749698:
                return prefix + '-jp'
        return prefix

    @commands.group(aliases=['rtfd'], invoke_without_command=True)
    async def rtfm(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity.
        Events, objects, and functions are all supported through a
        a cruddy fuzzy algorithm.
        """
        key = self.transform_rtfm_language_key(ctx, 'latest')
        await self.do_rtfm(ctx, key, obj)

    @rtfm.command(name='jp')
    async def rtfm_jp(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity (Japanese)."""
        await self.do_rtfm(ctx, 'latest-jp', obj)

    @rtfm.command(name='python', aliases=['py'])
    async def rtfm_python(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a Python entity."""
        key = self.transform_rtfm_language_key(ctx, 'python')
        await self.do_rtfm(ctx, key, obj)

    @rtfm.command(name='py-jp', aliases=['py-ja'])
    async def rtfm_python_jp(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a Python entity (Japanese)."""
        await self.do_rtfm(ctx, 'python-jp', obj)

    async def _member_stats(self, ctx, member, total_uses):
        e = discord.Embed(title='RTFM Stats')
        e.set_author(name=str(member), icon_url=member.avatar_url)
def setup(client):
    client.add_cog(ProgrammingCog(client))
