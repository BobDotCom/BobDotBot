import asyncio
import discord
from discord.ext import commands

from otherscipts.helpers import create_mute_role


class Moderator(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.warn_count = {}

    @commands.command(name="warn")
    @commands.has_guild_permissions(administrator=True)
    async def warn(self, ctx, user: discord.User = None, *, reason=None):
        if user is None or reason is None:
            await ctx.send("Insufficient arguments.")
        else:
            print(f"Warning user {user.name} for {reason}...")

            if str(user) not in self.warn_count:
                self.warn_count[str(user)] = 1
            else:
                self.warn_count[str(user)] += 1

            embed = discord.Embed(
                title=f"{user.name} has been warned", color=self.theme_color)
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="This user has been warned",
                            value=f"{self.warn_count[str(user)]} time(s)")

            await ctx.send(content=None, embed=embed)

    @commands.command(name="clearwarn")
    @commands.has_guild_permissions(administrator=True)
    async def clearwarn(self, ctx, user: discord.User = None):
        if user is None:
            self.warn_count = {}
            await ctx.send("Clearing all warns.")
        else:
            self.warn_count[str(user)] = 0
            await ctx.send(f"Clearing warns for {user.mention}.")

    @commands.command(name="warncount")
    async def warncount(self, ctx, user: discord.User):
        if str(user) not in self.warn_count:
            self.warn_count[str(user)] = 0

        count = self.warn_count[str(user)]
        await ctx.send(f"{user.mention} has been warned {count} time(s)")

    @commands.command(name="mute")
    @commands.has_guild_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member = None, time: str = None):
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
                await ctx.send("This user is already muted.")
            else:
                if not mute_role:
                    await ctx.send("This server does not have a `Muted` Role. Creating one right now.")
                    await ctx.send("This may take some time.")
                    mute_role = await create_mute_role(guild)

                if time is None:
                    await user.add_roles(mute_role)
                    await ctx.send(f"User {user.mention} has been muted! They cannot speak.")
                else:
                    time_unit = None
                    parsed_time = None

                    if "s" in time:
                        time_unit = "seconds"
                        parsed_time = time[0:(len(time) - 1)]
                    elif "m" in time:
                        time_unit = "minutes"
                        parsed_time = time[0:(len(time) - 1)]
                    elif "h" in time:
                        time_unit = "hours"
                        parsed_time = time[0:(len(time) - 1)]
                    else:
                        time_unit = "minutes"  # default to minutes if user doesn't provide a time unit
                        parsed_time = time[0:len(time)]

                    await user.add_roles(mute_role)
                    await ctx.send(f"User {user.mention} has been muted for {parsed_time} {time_unit}! They cannot speak.")

                    if time_unit == "seconds":
                        await asyncio.sleep(int(parsed_time))
                    elif time_unit == "minutes":
                        await asyncio.sleep(int(parsed_time) * 60)
                    elif time_unit == "hours":
                        await asyncio.sleep(int(parsed_time) * 3600)

                    await user.remove_roles(mute_role)
                    await ctx.send(f"User {user.mention} has been unmuted after {parsed_time} {time_unit}! They can speak now.")

    @commands.command(name="unmute")
    @commands.has_guild_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member = None):
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
                await ctx.send(f"User {user.mention} has been unmuted! They can now speak.")

            else:
                await ctx.send("This user was never muted.")

    @commands.command(name="ban")
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User = None, *, reason=None):
        if user is None:
            await ctx.send("Insufficient arguments.")
        else:
            await ctx.guild.ban(user, reason=reason)
            if reason:
                await ctx.send(f"User **{user}** has been banned for reason: **{reason}**.")
            else:
                await ctx.send(f"User **{user}** has been banned.")
            await user.send(f"You have been **banned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")

    @commands.command(name="tempban")
    @commands.has_guild_permissions(ban_members=True)
    async def tempban(self, ctx, user: discord.User = None, days: int = 1):
        if user is None:
            await ctx.send("Insufficient arguments.")
        else:
            await ctx.guild.ban(user)
            await ctx.send(f"User **{user}** has been temporarily banned for **{days} day(s)**")
            await user.send(f"You have been **temporarily banned** from **{ctx.guild}** server for **{days} day(s)**")
            await asyncio.sleep(days * 86400)  # convert days to seconds
            await ctx.guild.unban(user)
            await ctx.send(f"**{user}** has been unbanned after a {days} day Temp Ban.")

    @commands.command(name="unban")
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, username: str = None, *, reason=None):
        if username is None:
            await ctx.send("Insufficient arguments.")
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = username.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)

            try:
                if reason:
                    await ctx.send(f"User **{username}** has been unbanned for reason: **{reason}**.")
                else:
                    await ctx.send(f"User **{username}** has been unbanned.")
                await user.send(f"You have been **unbanned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
            except NameError:
                await ctx.send(f"{username} is has not been banned in this server.")

    @commands.command(name="kick")
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User = None, *, reason=None):
        if user is None:
            await ctx.send("Insufficient arguments.")
        else:
            await ctx.guild.kick(user, reason=reason)
            if reason:
                await ctx.send(f"User **{user}** has been kicked for reason: **{reason}**.")
            else:
                await ctx.send(f"User **{user}** has been kicked.")
            await user.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")

    @commands.command(name="lockchannel")
    @commands.has_guild_permissions(administrator=True)
    async def lockchannel(self, ctx, channel: discord.TextChannel = None):
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
        if channel is None:
            channel = ctx.channel

        await channel.set_permissions(ctx.guild.roles[0], send_messages=True)

        await ctx.send(f"🔓The channel {channel.mention} has been unlocked")
