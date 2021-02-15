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

"""
BobDotBot
~~~~~~~~~~~~~~~~~~
This file contains elements that are under the following licenses:

Copyright (c) 2015 Rapptz
license MIT, see https://github.com/Rapptz/RoboDanny/blob/e1c3c28fe20eb192463f7fc224a399141f0d915d/LICENSE.txt for more details.

Copyright (c) 2021 FalseDev
license MIT, see https://github.com/FalseDev/Tech-Struck/blob/6ebfb91fbe41119027eb96a6cd97dfb0b85e1ec7/LICENSE for more details.
"""

import discord
import os
import zlib
import io
import re
import aiohttp
from discord.ext import commands
from .utils import fuzzy

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
        self.bot = client
        self.client.session = aiohttp.ClientSession(loop=self.client.loop)
        self.regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
        
    @property
    def session(self):
        return self.bot.http._HTTPClient__session

    async def _run_code(self, *, lang: str, code: str):
        res = await self.session.post(
            "https://emkc.org/api/v1/piston/execute",
            json={"language": lang, "source": code})
        return await res.json()

    @commands.command()
    async def run(self, ctx: commands.Context, *, codeblock: str):
        """
        Run code and get results instantly
        **Note**: You must use codeblocks around the code
        Supported languages: awk, bash, brainfuck, c, cpp, crystal, csharp, d, dash, deno, elixer, emacs, go, haskell, java, jelly, julia, kotlin, lisp, lua, nasm, nasm64, nim, node, osabie, paradoc, perl, php, prolog, python2, python, ruby, rust, scala, swift, typescript, zig
        """
        matches = self.regex.findall(codeblock)
        if not matches:
            return await ctx.reply(embed=discord.Embed(title="Uh-oh", description="Couldn't quite see your codeblock"))
        lang = matches[0][0] or matches[0][1]
        if not lang:
            return await ctx.reply(embed=discord.Embed(title="Uh-oh", description="Couldn't find the language hinted in the codeblock or before it"))
        code = matches[0][2]
        result = await self._run_code(lang=lang, code=code)

        await self._send_result(ctx, result)

    @commands.command()
    async def runl(self, ctx:commands.Context, lang:str, *, code:str):
        """
        Run a single line of code, **must** specify language as first argument
        Supported languages: awk, bash, brainfuck, c, cpp, crystal, csharp, d, dash, deno, elixer, emacs, go, haskell, java, jelly, julia, kotlin, lisp, lua, nasm, nasm64, nim, node, osabie, paradoc, perl, php, prolog, python2, python, ruby, rust, scala, swift, typescript, zig
        """
        result = await self._run_code(lang=lang, code=code)
        await self._send_result(ctx, result)



    async def _send_result(self, ctx:commands.Context, result:dict):
        if "message" in result:
            return await ctx.reply(embed=discord.Embed(title="Uh-oh", description=result["message"], color=Color.red()))
        output = result['output']
#        if len(output) > 2000:
#            url = await create_guest_paste_bin(self.session, output)
#            return await ctx.reply("Your output was too long, so here's the pastebin link " + url)
        embed = discord.Embed(
            title=f"{result['language'][0].upper() + result['language'][1:]}")
        newline = '\n'
        rep = {"python3": "py", "python2": "py", 'node': 'js'}
        rep = dict((re.escape(k), v) for k, v in rep.items()) 
        pattern = re.compile("|".join(rep.keys()))
        converted_language = pattern.sub(lambda m: rep[re.escape(m.group(0))], result['language'])
        limit = 1024 - (27 + len(converted_language))
        output = f"```{converted_language}\n{output[:limit]}```{(len(output)>limit) * (newline + '**Output shortened**')}"
        embed.add_field(name="Output", value=output or "**No output**")
        try:
            await ctx.reply(embed=embed)
        except:
            await ctx.reply(output)
        
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
