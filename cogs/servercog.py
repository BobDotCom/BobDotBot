# import stuff
import discord

# import stuff
import os
import json
# import stuff
import typing
import asyncio
import datetime
# import stuff
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime

class ServerCog(commands.Cog, name = "Server"):
    """Special commands that only administrators/moderators in the server can use"""

    def __init__(self, client):
        self.client = client
        self.client.uptime = datetime.utcnow()
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221

    @commands.Cog.listener()
    async def on_ready(self):
        print('ServerCog is active')

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def prefix(self, ctx, *args):
        """Set one or multiple prefixes for BobDotBot in your server"""
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        with open('prefixes.json', 'r') as f:
            notprefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = args
        notprefixes[str(ctx.guild.id)] = ['B.', 'b.']
        args = None if not args else args
        if args:
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Prefix(s) changed to {args}')
        else:
            await ctx.send('To use the prefixes command, type B.prefix prefix1 prefix2(optional) etc. Since you did not specify any prefixes this time, I reset your server prefixes to the default B. or b.')
            with open('prefixes.json', 'w') as f:
                json.dump(notprefixes, f, indent=4)

    @commands.command(aliases=['c'])
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx,amount=2):
        """Clears messages"""
        await ctx.channel.purge(limit = amount + 1)
        await ctx.send(f"I ate {amount} messages for you! ;)")

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member],
                   delete_days: typing.Optional[int] = 0, *,
                   reason: str = None):
        """Mass bans members with an optional delete_days parameter"""
        for member in members:
            try:
                asdf = ctx.author
                f = member.top_role
                h = asdf.top_role
                if h > f or ctx.guild.owner == ctx.author and not member == ctx.author:
                  if member.guild_permissions.ban_members and not ctx.guild.owner == ctx.author:
                    await ctx.send("This person has to not have the ban members permission.")
                  else:
                    await member.ban(delete_message_days=delete_days, reason=reason)
                    await ctx.send("Ok, I banned them for you")
                else:
                  if member == ctx.author:
                    await ctx.send("You can't ban yourself. -_-")
                  else:
                    await ctx.send("Error, this person has a higher or equal role to you")
            except:
                await ctx.send(f"Hmmm, I do not have permission to ban {member}, or that is not a valid member")

def setup(client):
    client.add_cog(ServerCog(client))
