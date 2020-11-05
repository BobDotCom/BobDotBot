# import stuff
import discord
import asyncio
import subprocess as sp
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter

class OwnerCog(commands.Cog, name = "Owner"):
    """Special commands that only the owner of the bot can use"""

    def __init__(self, client):
        self.client = client
        self.client.owner_id = 690420846774321221

    @commands.Cog.listener()
    async def on_ready(self):
        print('OwnerCog is active')

    @commands.command(aliases=['update', 'maintenence', 'logout', 'die', 'kill'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shuts the bot down
        Uses: `B.shutdown`"""
        owner = self.client.get_user(self.client.owner_id)
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
        owner = self.client.get_user(self.client.owner_id)
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
        owner = self.client.get_user(self.client.owner_id)
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
        owner = self.client.get_user(self.client.owner_id)
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
        owner = self.client.get_user(self.client.owner_id)
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
def setup(client):
    client.add_cog(OwnerCog(client))
