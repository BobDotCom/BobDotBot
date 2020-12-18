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

import asyncio
import discord
from discord.ext import commands
from typing import Optional
from otherscripts.helpers import create_mute_role
from cogs.anothermoderationcog import mutes

class Moderator(commands.Cog):
    """Special moderation commands for moderators in the server"""
    def __init__(self, client):
        self.bot = client
        self.warn_count = {}

    @commands.command(name="warn")
    @commands.has_guild_permissions(administrator=True)
    async def warn(self, ctx, user: discord.User = None, *, reason=None):
        """Give a warning to a member. If automod is enabled, it will give them certain punishments at different increments"""
        reason = "No specified reason" if not reason else reason
        if user is None:
            await ctx.send("Please choose a user")
        else:
            print(f"Warning user {user.name} for {reason}...")

            if str(user) not in self.warn_count:
                self.warn_count[str(user)] = 1
            else:
                self.warn_count[str(user)] += 1

            embed = discord.Embed(
                title=f"{user.name} has been warned")
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="This user has been warned",
                            value=f"{self.warn_count[str(user)]} time(s)")
    @commands.command(aliases=['nick'])
    @commands.has_guild_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member : discord.Member, *args):
        """Change the nickname of a user"""
        if member == None:
            await ctx.send('Give me a user please')
        elif member == ctx.guild.owner:
            await ctx.send('You cant name the owner!')
        else:
          try:
            x = ' '.join(map(str, args))
            await member.edit(nick=f'{x}')
            await ctx.send(f'{member.name} has been changed to {x}')
          except:
            await ctx.send("I cant")

    @commands.command(name="clearwarn")
    @commands.has_guild_permissions(administrator=True)
    async def clearwarn(self, ctx, user: discord.User = None):
        """Clear warnings of every user, or just the set user"""
        if user is None:
            self.warn_count = {}
            await ctx.send("Clearing all warns.")
        else:
            self.warn_count[str(user)] = 0
            await ctx.send(f"Clearing warns for {user}.")

    @commands.command(name="warncount")
    async def warncount(self, ctx, user: discord.User):
        """Get the amount of warnings that a user has"""
        if str(user) not in self.warn_count:
            self.warn_count[str(user)] = 0

        count = self.warn_count[str(user)]
        await ctx.send(f"{user} has been warned {count} time(s)")

    @commands.command(name="mute")
    @commands.has_guild_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member = None, time = None, *, reason = None):
        """Mute a member in the server. If you already have a role named muted, it will use that. If not, it will make one for you."""
        if user is None:
            await ctx.send("Insufficient arguments.")
        await mutes(self,ctx,user,time,reason)

    @commands.command(name="unmute")
    @commands.has_guild_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member = None):
        """Unmute a member. This will remove all roles named muted from the member"""
        if user is None:
            await ctx.send("Insufficient arguments.")
        else:
            guild = ctx.guild
            mute_role = None

            for role in guild.roles:
                if role.name.lower() == "muted":
                    mute_role = role
                    break

            if mute_role in user.roles:
                if not mute_role:
                    mute_role = await create_mute_role(guild)

                await user.remove_roles(mute_role)
                await ctx.send(f"User {user} has been unmuted! They can now speak.")

            else:
                await ctx.send("This user was never muted.")

    @commands.command()
    @commands.has_permissions(ban_members = True)
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def ban(self, ctx, member: discord.Member, delete_days: Optional[int] = 0, *,reason: str = None):
        """Ban a member with an optional delete_days parameter
        The reason must not start with a number, and you may give a reason without deleting messages"""
        if True:
            try:
                asdf = ctx.author
                f = member.top_role
                h = asdf.top_role
                if h > f or ctx.guild.owner == ctx.author and not member == ctx.author:
                  if member.guild_permissions.ban_members and not ctx.guild.owner == ctx.author:
                    await ctx.send("This person has to not have the ban members permission.")
                  else:
                    await member.ban(delete_message_days=delete_days, reason="Banned by: " + ctx.author.mention + ": " + (reason or "No reason specified"))
                    await ctx.send("Ok, I banned them for you")
                else:
                  if member == ctx.author:
                    await ctx.send("You can't ban yourself. -_-")
                  else:
                    await ctx.send("Error, this person has a higher or equal role to you")
            except:
                await ctx.send(f"Hmmm, I do not have permission to ban {member}, or that is not a valid member")
            try:
                await member.send(f"You have been **banned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
            except:
                pass

    @commands.command(name="unban")
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, username: str = None, *, reason=None):
        """Unban a member. Use this format: `"Username 1234#0001"`"""
        if username is None:
            await ctx.send("Insufficient arguments.")
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = username.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user,reason="Unbanned by: " + ctx.author.mention + ": " + (reason or "No reason specified"))

            try:
                if reason:
                    await ctx.send(f"User **{username}** has been unbanned for reason: **{reason}**.")
                else:
                    await ctx.send(f"User **{username}** has been unbanned.")
                await user.send(f"You have been **unbanned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
            except NameError:
                await ctx.send(f"{username} is has not been banned in this server.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        """Kick someone"""
        if True:
            try:
                asdf = ctx.author
                f = member.top_role
                h = asdf.top_role
                if h > f or ctx.guild.owner == ctx.author and not member == ctx.author:
                  if member.guild_permissions.kick_members and not ctx.guild.owner == ctx.author:
                    await ctx.send("This person has to not have the kick members permission.")
                  else:
                    await member.kick(reason=reason)
                    await ctx.send("Ok, I kicked them for you")
                else:
                  if member == ctx.author:
                    await ctx.send("You can't kick yourself. -_-")
                  else:
                    await ctx.send("Error, this person has a higher or equal role to you")
            except:
                await ctx.send(f"Hmmm, I do not have permission to kick {member}, or that is not a valid member")
            await member.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")

    @commands.command(name="lockchannel")
    @commands.has_guild_permissions(administrator=True)
    async def lockchannel(self, ctx, channel: discord.TextChannel = None):
        """Prevent users from speaking in a channel. If no channel is specified, it will lock the current channel"""
        if channel is None:
            channel = ctx.channel

        for role in ctx.guild.roles:
            if role.permissions.administrator:
                await channel.set_permissions(role, send_messages=True, read_messages=True)
            elif role.name == "@everyone":
                await channel.set_permissions(role, send_messages=False)

        await ctx.send(f"🔒The channel {channel.mention} has been locked")

    @commands.command(name="unlockchannel")
    @commands.has_guild_permissions(administrator=True)
    async def unlockchannel(self, ctx, channel: discord.TextChannel = None):
        """Allow everyone to talk in a channel. If no channel is specified, it will unlock the current channel"""
        if channel is None:
            channel = ctx.channel

        await channel.set_permissions(ctx.guild.roles[0], send_messages=True)

        await ctx.send(f"🔓The channel {channel.mention} has been unlocked")
    @commands.command(aliases=['c'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx,amount=2):
        """Clears messages. If not amount is specified, it will clear 2 messages"""
        await ctx.channel.purge(limit = amount + 1)
        msg = await ctx.send(f"I ate {amount} messages for you! ;)")
        await asyncio.sleep(5)
        await msg.delete()
def setup(client):
    client.add_cog(Moderator(client))
