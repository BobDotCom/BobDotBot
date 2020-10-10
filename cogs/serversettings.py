import discord
from discord.ext import commands

from otherscripts.data import Data


class Serversettings(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.theme_color = discord.Color.blurple()

    @commands.command(name="welcomemessage")
    @commands.has_guild_permissions(administrator=True)
    async def welcome_message(self, ctx, *, msg: str = ""):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["welcome_msg"] = msg
        if len(msg.strip()) == 0:
            await ctx.send("This server's welcome message has been disabled")
        else:
            await ctx.send(f"This server's welcome message has been set to ```{msg}```")
    @commands.command(name="leavemessage")
    @commands.has_guild_permissions(administrator=True)
    async def leave_message(self, ctx, *, msg: str = ""):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["leave_message"] = msg
        if len(msg.strip()) == 0:
            await ctx.send("This server's leave message has been disabled")
        else:
            await ctx.send(f"This server's leave message has been set to ```{msg}```")

    @commands.command(name="joinrole")
    @commands.has_guild_permissions(administrator=True)
    async def join_role(self, ctx, *, role: discord.Role):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["join_role"] = role.id
        await ctx.send(f"This server's join role has been set to **{role}**")

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        name = ctx.guild.name
        description = ctx.guild.description
        owner = ctx.guild.owner
        guild_id = ctx.guild.id
        region = ctx.guild.region
        member_count = ctx.guild.member_count
        icon = ctx.guild.icon_url

        embed = discord.Embed(
            title=f"{name} Server Information",
            description=description,
            color=self.theme_color
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=guild_id, inline=True)
        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Member Count", value=member_count, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="useri")
    async def useri(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(
            color=self.theme_color,
            timestamp=ctx.message.created_at,
            description=member.mention
        )

        embed.set_author(name=f"{member} Info")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name="ID:", value=member.id, inline=False)
        embed.add_field(
            name="Registered At:",
            value=member.created_at.strftime("%a, %d %b %Y %I:%M %p"),
            inline=False
        )
        embed.add_field(
            name="Joined Server At:",
            value=member.joined_at.strftime("%a, %d %b %Y %I:%M %p"),
            inline=False
        )
        embed.add_field(
            name=f"{len(member.roles)-1} Roles",
            value=" ".join([role.mention for role in member.roles if role != ctx.guild.default_role]),
            inline=False
        )
        badges = ""
        for i in list(iter(member.public_flags)):
            if i[1] and i[0] == "staff":
                badges += str(self.bot.get_emoji(764456791215046667))+" Discord Staff"
            if  i[1] and i[0] == "partner":
                badges += str(self.bot.get_emoji(764456791345201173))+" Discord Partner"
            if  i[1] and i[0] == "early_supporter":
                badges += str(self.bot.get_emoji(764456791453990933))+" Early Supporter"
            if  i[1] and i[0] == "bug_hunter":
                badges += str(self.bot.get_emoji(764456789440725012))+" Bug Hunter"
            if  i[1] and i[0] == "bug_hunter_level_2":
                badges += str(self.bot.get_emoji(764456791509041152))+" Bug Hunter 2"
            if  i[1] and i[0] == "early_verified_bot_developer":
                badges += str(self.bot.get_emoji(764456791601315860))+" Early Verified Bot Developer"
            if  i[1] and i[0] == "verified_bot":
                badges += str(self.bot.get_emoji(764507982347763712))+str(self.bot.get_emoji(764507981907755018))+" Verified Bot"
            if  i[1] and i[0] == "hypesquad":
                badges += str(self.bot.get_emoji(764456789256830976))+" Hypesquad"
            if  i[1] and i[0] == "hypesquad_bravery":
                badges += str(self.bot.get_emoji(764456791294869506))+" Hypesquad Bravery"
            if  i[1] and i[0] == "hypesquad_brilliance":
                badges += str(self.bot.get_emoji(764456789734588426))+" Hypesquad Brilliance"
            if  i[1] and i[0] == "hypesquad_balance":
                badges += str(self.bot.get_emoji(764456791521361930))+" Hypesquad Balance"
            else:
                badges += ""
        if badges == "":
            badges = "None"
        embed.add_field(name="Badges", value=badges)

        embed.add_field(name="Bot?", value=member.bot)

        await ctx.send(embed=embed)

    @commands.command(name="enablerespects")
    @commands.has_guild_permissions(manage_messages=True)
    async def enablerespects(self, ctx):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["pay_respects"] = True
        await ctx.send("Respects have been enabled!")

    @commands.command(name="disablerespects")
    @commands.has_guild_permissions(manage_messages=True)
    async def disablerespects(self, ctx):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["pay_respects"] = False
        await ctx.send("Respects have been disabled!")
def setup(client):
    client.add_cog(Serversettings(client))
