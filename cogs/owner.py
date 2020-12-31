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
import asyncio
import aiohttp
import os
import json
import subprocess as sp
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
import time_str
import humanize

class OwnerCog(commands.Cog, name = "Owner"):
    """Special commands that only the owner of the bot can use"""

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['update', 'maintenence', 'logout', 'die', 'kill'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shuts the bot down
        Uses: `B.shutdown`"""
        owner = self.client.get_user(self.client.owner_ids[0])
        embedvar = discord.Embed(title="*Shutting Down...*", description="Goodbye!", color=0xff0000)
        embedvar.set_footer(text=f"Bot made by {owner}")
        await ctx.send(embed=embedvar)
        print("Bot Shut Down")
        output = sp.getoutput("systemctl stop my_bot")
        await ctx.send(output)
    @commands.command(name="restart")
    @commands.is_owner()
    async def nopnop(self,ctx):
        """Restarts the bot
        Uses: `B.restart`"""
        owner = self.client.get_user(self.client.owner_ids[0])
        embedvar = discord.Embed(title="*Restarting...*", description="Be right back!")
        embedvar.set_footer(text=f"Bot made by {owner}")
        await ctx.send(embed=embedvar)
        await ctx.bot.logout()
    @commands.command(name="reloadplus", aliases=["rp"])
    @commands.is_owner()
    async def nop(self,ctx):
        restart = self.client.get_command("restart")
        sync = self.client.get_command("sync")
        await ctx.invoke(sync)
        await ctx.invoke(restart)
    @commands.command(name="reloadcog", aliases=["rc"])
    @commands.is_owner()
    async def botstop(self,ctx):
        ra = self.client.get_command("ra")
        sync = self.client.get_command("sync")
        await ctx.invoke(sync)
        await ctx.invoke(ra)
    @commands.command()
    @commands.is_owner()
    async def osay(self, ctx, *, arg):
        """Says what you tell it to
        Uses: `B.osay <message>`"""
        await ctx.message.delete()
        await ctx.send(arg)

    @commands.command()
    @commands.is_owner()
    async def ossay(self, ctx, *, arg):
        """Says what you tell it to, and leaves your message
        Uses: `B.ossay <message>`"""
        await ctx.send(arg)

    @commands.command()
    @commands.is_owner()
    async def help_jsk(self, ctx):
        """Lists the help command for jsk
        Uses: `B.help_jsk`"""
        owner = self.client.get_user(self.client.owner_ids[0])
        embedvar = discord.Embed(title="Jishaku Commands", description="Since help jsk doesnt work, these are the commands that jishaku has:", color=0x000000, timestamp=ctx.message.created_at)
        embedvar.add_field(name='cancel', value='Cancels a task with the given index.')
        embedvar.add_field(name='cat', value='Read out a file, using syntax highlighting if detected.')
        embedvar.add_field(name='curl', value='Download and display a text file from the internet.')
        embedvar.add_field(name='debug', value='Run a command timing execution and catching exceptions.')
        embedvar.add_field(name='git', value='Shortcut for "jsk sh git". Invokes the system shell.')
        embedvar.add_field(name='hide', value='Hides Jishaku from the help command.')
        embedvar.add_field(name='in', value='Run a command as if it were run in a different channel.')
        embedvar.add_field(name='load', value='Loads or reloads the given extension names.')
        embedvar.add_field(name='py', value='Direct evaluation of Python code.')
        embedvar.add_field(name='py_inspect', value='Evaluation of Python code with inspect information.')
        embedvar.add_field(name='repeat', value='Runs a command multiple times in a row.')
        embedvar.add_field(name='retain', value='Turn variable retention for REPL on or off.')
        embedvar.add_field(name='shell', value='Executes statements in the system shell.')
        embedvar.add_field(name='show', value='Shows Jishaku in the help command.')
        embedvar.add_field(name='shutdown', value='Logs this bot out.')
        embedvar.add_field(name='source', value='Displays the source code for a command.')
        embedvar.add_field(name='su', value='Run a command as someone else.')
        embedvar.add_field(name='sudo', value='sudo(Run a command bypassing all checks and cooldowns.')
        embedvar.add_field(name='tasks', value='Shows the currently running jishaku tasks.')
        embedvar.add_field(name='unload', value='Unloads the given extension names.')
        embedvar.add_field(name='voice', value='Voice-related commands.')
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        await ctx.send(embed=embedvar)
    @commands.command(aliases=['push'])
    @commands.is_owner()
    async def save(self, ctx):
        """Saves all data to the GitHub repository
        Uses: `B.save`"""
        owner = self.client.get_user(self.client.owner_ids[0])
        embedvar = discord.Embed(title="Saving...", description="Saving to the GitHub repository, this should take up to 15 seconds", color=0xff0000, timestamp=ctx.message.created_at)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        msg = await ctx.send(embed=embedvar)
        async with ctx.channel.typing():
            c = self.client.get_guild(727739470731935765).get_channel(758759590287638571)
            output = sp.getoutput('git pull origin main')
            await c.send(f"""
            ```sh
            {output}
            ```
            """)
            output = sp.getoutput('git add .')
            await c.send(f"""
            ```sh
            {output}
            ```
            """)
            output = sp.getoutput('git commit -m "Save"')
            await c.send(f"""
            ```sh
            {output}
            ```
            """)
            output = sp.getoutput('git push origin main')
            await c.send(f"""
            ```sh
            {output}
            ```
            """)
            msg1 = await ctx.send("Success!")
            await msg1.delete()
        embedvar = discord.Embed(title="Saved", description="Save to the GitHub repository has completed, check the logs to make sure it worked", color=0x00ff00, timestamp=ctx.message.created_at)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        await msg.edit(embed=embedvar)
    @commands.command(aliases=['pull'])
    @commands.is_owner()
    async def sync(self,ctx):
        """Get the most recent changes from the GitHub repository
        Uses: `B.sync`"""
        owner = self.client.get_user(self.client.owner_ids[0])
        embedvar = discord.Embed(title="Syncing...", description="Syncing with the GitHub repository, this should take up to 15 seconds", color=0xff0000, timestamp=ctx.message.created_at)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        msg = await ctx.send(embed=embedvar)
        async with ctx.channel.typing():
            c = self.client.get_guild(727739470731935765).get_channel(758759590287638571)
            output = sp.getoutput('git pull origin main')
            await c.send(f"""
            ```sh
            {output}
            ```
            """)
            msg1 = await ctx.send("Success!")
            await msg1.delete()
        embedvar = discord.Embed(title="Synced", description="Sync with the GitHub repository has completed, check the logs to make sure it worked", color=0x00ff00, timestamp=ctx.message.created_at)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        await msg.edit(embed=embedvar)
    @commands.command()
    @commands.is_owner()
    async def pings(self,ctx,member: discord.Member, times = None):
        times = 1 if not times else int(times)
        for i in range(times):
            await asyncio.sleep(1)
            await ctx.send(member.mention)
    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code: codeblock_converter):
        cog = self.client.get_cog("Jishaku")
        await cog.jsk_python(ctx, argument=code)
    @commands.command()
    @commands.is_owner()
    async def markdown_all_commands(self, ctx):
        """Gets a markdown styled document for all of the commands and their categories and their help"""
        x = ""
        z = ""
        for extension in self.client.extensions:
          if extension.startswith("cogs."):
            try:
              y = extension[5:]
              y = y[0].upper() + y[1:]
              asdf = self.client.get_cog(y)
              entries = asdf.get_commands()
              z += "\n### " + y + "\n#### " + asdf.description
              for a in entries:
                b = a.help if a.help else ""
                z += "\n##### " + a.name + "\n" + b
            except AttributeError:
              continue
        async with aiohttp.ClientSession() as cs:
          async with cs.post('https://mystb.in/documents', data = z) as r:
            res = await r.json()
            key = res["key"]
        await ctx.send(f"https://mystb.in/{key}")
    @commands.command()
    @commands.is_owner()
    async def pip(self, ctx, *, code = None):
        if code:
            #read
            f = open('requirements.txt','r')
            message = f.read()
            f.close()
            #write
            f = open('requirements.txt','wb')
            f.write(f'{message}\n{code}'.encode('utf-8'))
            f.close()
        cog = self.client.get_cog("Jishaku")
        codes = codeblock_converter("python3 -m pip install -r requirements.txt")
        await cog.jsk_shell(ctx, argument=codes)
    @commands.command()
    @commands.is_owner()
    async def loopcommand(self, ctx, command, times = 10, keyword = "f", timeout = 15, useable_by = "me"):
        ph = self.client.get_command(command)
        for i in range(times):
          def check(m):
            if useable_by == "me":
                    return m.content == keyword and m.channel == ctx.channel and m.author == ctx.author
            else:
                return m.content == keyword and m.channel == ctx.channel
          
          msg = await self.client.wait_for('message', check=check,timeout=timeout)
          await ctx.invoke(ph)

    @commands.command()
    @commands.is_owner()
    async def blacklist(self,ctx,action,user_id,time_amount='Permanent',*,reason=None):
        user_id = int(user_id)
        with open("blacklisted.json",'r') as f:
            data = json.load(f)
        data['users'] = data['users'] or []
        if action == "add":
            data['users'].append(user_id)
        elif action == 'remove':
            data['users'].remove(user_id)
        self.client.blacklisted = data["users"]
        with open("blacklisted.json",'w') as f:
            json.dump(data,f,indent=4)
        if not time_amount.lower() in ['permanent',"forever"]:
            time_amount = f"**{time_amount}** \nOnce this time is up, you may make an appeal to my developer."
        else:
            time_amount = f"**{time_amount}**"
        try:
            user = self.client.get_user(user_id)
            if action == "add":
                embed = discord.Embed(title="You've been blacklisted!",description=f"This means you will not be able to use the bot. If you would like to appeal this, or if you think this is a mistake, please contact my developer {self.client.get_user(self.client.owner_ids[0])}.",color=discord.Color.red())
                embed.add_field(name='Time',value=time_amount)
                embed.add_field(name='Reason',value=reason or 'None specified')
                await user.send(embed=embed)
                await ctx.send(f'Successfully blacklisted {user}')
            elif action == 'remove':
                await user.send('You have been removed from the blacklist. You may use the bot now.')
                await ctx.send(f'Successfully unblacklisted {user}')
        except:
            await ctx.send('failed')

    @commands.command()
    @commands.is_owner()
    async def cogs(self,ctx):
        cogs,extensions,notloaded,final = [], [], [], []
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cogs += [filename[:-3], ]
        for extension in self.client.extensions:
            extensions += [extension,]
        for cog in cogs:
            if not cog in extensions:
                notloaded += [cog,]
        for x in cogs:
            if not "cogs." + x in extensions:
                final += [f":x: {x}",]
            else:
                final += [f":white_check_mark: cogs.{x}",]
        for x in extensions:
            if not f":white_check_mark: {x}" in final:
                final += [f":white_check_mark: {x}",]
        displayed = '\n'.join(final)
        embed = discord.Embed(title="Cogs",description=displayed,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.is_owner()
    async def time(self, ctx, time: time_str.convert):
        output = humanize.precisedelta(time)
        await ctx.send(output)

def setup(client):
    client.add_cog(OwnerCog(client))
