# import stuff
import discord

# import stuff
import os
import random
# import stuff
import typing
import asyncio
import datetime
import json
# import stuff
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime
from discord.ext.commands import MissingPermissions

class MemberRoles(commands.MemberConverter):
    async def convert(self, ctx, argument):
        member = await super().convert(ctx, argument)
        return [role.mention for role in member.roles[1:]] # Remove everyone role!

class MainCog(commands.Cog, name = "General"):
    """General commands that anyone can use"""

    def __init__(self, client):
        self.client = client
        self.client.uptime = datetime.utcnow()
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221
        self.client.helper1_id = 716503311402008577
        self.client.helper2_id = 280667989370732545
        self.client.helper3_id = 706898741499789364

    @commands.Cog.listener()
    async def on_ready(self):
        print('MainCog is active')

    @commands.Cog.listener()
    async def on_message(self, message):
	# check if msg is hello
        if message.content.lower() == "rickroll me please":
	# sends reply
                await message.channel.send("never gonna give you up")
        if "fuck" in message.content.lower():
        # sends reply
                await message.channel.send("LANGUAGE")
                await message.delete()
        if message.content.lower() == "Shadow Legends":
	# sends reply
                await message.channel.send("Today's video is sponsored by Raid Shadow Legends, one of the biggest mobile role-playing games of 2019 and it's totally free! Currently almost 10 million users have joined Raid over the last six months, and it's one of the most impressive games in its class with detailed models, environments and smooth 60 frames per second animations! All the champions in the game can be customized with unique gear that changes your strategic buffs and abilities! The dungeon bosses have some ridiculous skills of their own and figuring out the perfect party and strategy to overtake them's a lot of fun! Currently with over 300,000 reviews, Raid has almost a perfect score on the Play Store! The community is growing fast and the highly anticipated new faction wars feature is now live, you might even find my squad out there in the arena! It's easier to start now than ever with rates program for new players you get a new daily login reward for the first 90 days that you play in the game! So what are you waiting for? Go to the video description, click on the special links and you'll get 50,000 silver and a free epic champion as part of the new player program to start your journey! Good luck and I'll see you there!")
        if message.content.startswith('test embed'):
                embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
                embedVar.add_field(name="Field1", value="hi", inline=False)
                embedVar.add_field(name="Field2", value="hi2", inline=False)
                await message.channel.send(embed=embedVar)



    @commands.command()
    async def test(self, ctx):
        """Its a frickin test command jeez"""
        await ctx.send('testing')

    @commands.command()
    async def uptime(self, ctx):
            """See how long the bot has been online"""
            owner = self.client.get_user(self.client.owner_id)
            minute,hour,day,second = 0,0,0,0
            time = datetime.utcnow()
            time -= self.client.uptime
            second = list(str(time.seconds)).copy()
            second = int("".join(second))
            if second > 60:
                minute =+ second // 60
                second = second % 60
            if minute > 60:
                hour += minute // 60
                minute = minute % 60
            if hour > 24:
                day += hour // 24
                hour = hour % 24
            embedVar = discord.Embed(title="Bot Uptime", timestamp=ctx.message.created_at, description=f"Bot has been online for {day}d {hour}h {minute}m {second}s", color=0x00ff00) #,color=Hex code
            embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
            await ctx.send(embed=embedVar)



    @commands.command(aliases=["nub"])
    async def noob(self, ctx):
        """Ur nub"""
        await ctx.send("NOOOOOB")

    @commands.command()
    async def invite(self, ctx):
        """Invite me to your own server!"""
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Wow! I'm really that special?", timestamp=ctx.message.created_at, description="I have 2 different versions, here they are:", color=0x00ff00) #,color=Hex code
        embedvar.add_field(name="BobDotBot(Reccomended)", value="This bot is online almost 24/7, and the code works a lot better than alpha, though it still has lots of new features. [Click Here](https://discord.com/api/oauth2/authorize?client_id=746045299125911562&permissions=8&scope=bot)", inline=False)
        embedvar.add_field(name="BobDotBot Alpha(Unstable)", value="This bot has code that updates as I write it, so it may be buggy. Only online part of the day.(You will have to request permission from the owner to invite this bot) [Click Here](https://discord.com/api/oauth2/authorize?client_id=745044803732897802&permissions=8&scope=bot)", inline=False)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)

    @commands.command()
    async def add(self, ctx, a: int, b: int):
        """I'm a baby bot, so i only do baby math(format= "x y" for x+y=z)"""
        answer = (a + b)
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Math", timestamp=ctx.message.created_at, description="I think the answer to that is **" + str(answer) + "**", color=0x9400ff) #,color=Hex code
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)

    @commands.command()
    async def roles(self, ctx, *, member: MemberRoles):
        """Tells you a member's roles."""
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Roles", timestamp=ctx.message.created_at, description='I see the following roles: ' + ', '.join(member), color=0xfff300) #,color=Hex code
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)

    @commands.command()
    async def slap(self, ctx, members: commands.Greedy[discord.Member], *, reason='no reason'):
        """Use this to slap someone(B.slap <@user> <reason>)"""
        slapped = ", ".join(x.name for x in members)
        slapself = f"{ctx.author.name}"
        owner = self.client.get_user(self.client.owner_id)
        if slapped:
            embedvar = discord.Embed(title="***SLAP***", timestamp=ctx.message.created_at, description='*{}* just got **slapped** for {}'.format(slapped, reason), color=0xff8400) #,color=Hex code
            embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        else:
            embedvar = discord.Embed(title="***OOPS***", timestamp=ctx.message.created_at, description=f"{slapself} just **slapped** themselves because they didn't mention someone valid to slap!", color=0x000000)
        await ctx.send(embed=embedvar)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        """Kick someone"""
        await member.kick(reason=reason)

    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, *, member: discord.Member):
        """Tells you some info about the member."""
        fmt = '{0.mention}: {0} joined on {0.joined_at} and has {1} roles.'
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title="User Info", timestamp=ctx.message.created_at, description="" + fmt.format(member, len(member.roles)-1), color=0xfff300)
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedVar)

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('I could not find that member...')

    @commands.command()
    async def say(self, ctx, *, arg):
        """Says what you want"""
        quote = arg
        author = ctx.author.name
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title=f"{author} says:", timestamp=ctx.message.created_at, description=f'{quote}', color=0x00ff00)
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedVar)

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """Checks ping(alais=pong)"""
        ping = int(self.client.latency * 1000)
        owner = self.client.get_user(self.client.owner_id)
        embedVar = discord.Embed(title="***PONG!***  :ping_pong:", timestamp=ctx.message.created_at, description="My ping is *" + str(ping) + "ms*", color=0x00ff00)
        embedVar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedVar)

    @commands.command()
    async def porn(self, ctx):
        """Use if you are really horny"""
        await ctx.send("Shut up, horny kid.")

    @commands.command()
    async def displayembed(self, ctx):
        """This is an embed tester"""
        owner = self.client.get_user(self.client.owner_id)
        embedvar = discord.Embed(title="Title", timestamp=ctx.message.created_at, description="desc", color=0xff0000) #,color=Hex code
        embedvar.add_field(name="subheader", value="desc2", inline=False)
        embedvar.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
        await ctx.send(embed=embedvar)

    @commands.command(pass_context=True)
    @commands.has_permissions(add_reactions=True,embed_links=True)
    async def help(self,ctx,*cog):
        """Lists all command categories and owner commands of mine."""
        try:
            if not cog:
                """Cog listing.  What more?"""
                owner = self.client.get_user(self.client.owner_id)
                halp=discord.Embed(title='Command Categories', timestamp=ctx.message.created_at,
                                   description='Use `B.help *category*` to see a list of commands!')#\nYou can use commands in this DM, just use the prefix like normal.
                cogs_desc = ''
                for x in self.client.cogs:
                    cogs_desc += ('***{}*** - {}'.format(x,self.client.cogs[x].__doc__)+'\n')
                halp.add_field(name='Categories',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
                halp.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
                cmds_desc = 'test'
                Uncategorized_Command_Exist = False
                for y in self.client.walk_commands():
                    if not y.cog_name and not y.hidden:
                        Uncategorized_Command_Exist = True
                        cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
                #if Uncategorized_Command_Exist == True:
                        #halp.add_field(name='Owner Commands',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
                await ctx.message.add_reaction(emoji='✉')
                await ctx.send('',embed=halp)
            else:
                """Helps me remind you if you pass too many args."""
                if len(cog) > 1:
                    owner = self.client.get_user(self.client.owner_id)
                    halp = discord.Embed(title='Error!', timestamp=ctx.message.created_at,description="Can't get more than one category at once!",color=discord.Color.red())
                    halp.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
                    await ctx.send('',embed=halp)
                else:
                    """Command listing within a cog."""
                    splice = cog[0]
                    cog = splice[0].upper() + splice[1:].lower()
                    #printing commands of cog
                    """Command listing within a cog."""
                    found = False
                    #finding Cog
                    for x in self.client.cogs:
                        #for y in cog:
                        if x == cog:
                            #making title
                            owner = self.client.get_user(self.client.owner_id)
                            halp=discord.Embed(title=cog+' Commands', timestamp=ctx.message.created_at,description=self.client.cogs[cog].__doc__, color=0x000000)
                            halp.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
                            for c in self.client.get_cog(cog).get_commands():
                                if not c.hidden: #if cog not hidden
                                    halp.add_field(name=c.name,value=c.help,inline=False)
                            found = True
                    if not found:
                        """Reminds you if that cog doesn't exist."""
                        owner = self.client.get_user(self.client.owner_id)
                        halp = discord.Embed(title='Error!', timestamp=ctx.message.created_at,description='Ummmm, "'+cog+'" is not a command...',color=discord.Color.red())
                        halp.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url) #if you like to
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                    await ctx.send('',embed=halp)

        except:
            await ctx.send("Error, I can't send embeds.")

    def setup(client):
        client.add_command(help)

    @commands.command(aliases=["credit", "owner"])
    async def credits(self, ctx):
        """Shows the credits for the bot"""
        owner = self.client.get_user(self.client.owner_id)
        routergtx = self.client.get_user(self.client.helper1_id)
        gamin = self.client.get_user(self.client.helper2_id)
        yo56789 = self.client.get_user(self.client.helper3_id)
        tcc = "The Coding Community - https://discord.gg/a84amZ4"
        dpy = "discord.py - https://discord.gg/dpy"
        embed = discord.Embed(color=0x00ff00, timestamp=ctx.message.created_at, inline=False)
        embed.set_author(name=f"Bot created by {owner}", icon_url=owner.avatar_url)
        embed.add_field(name=f"Others", value=f"Special thanks to everyone who helped me with learning how to create this bot, especially the following people and servers", inline=False)
        embed.add_field(name=f'{routergtx}', value=f"RouterGTX was a really big help with learning how the code worked, and giving me examples, but still letting me figure out most of it on my own", inline=False)
        embed.add_field(name=f'{gamin}', value=f'Okct was one of the first people to help me, and was able to help me solve problems that I was having trouble with at the beginning', inline=False)
        embed.add_field(name=f'{yo56789}', value=f'Yo56789 helped me get pointed in the right direction even from my first day making a bot, and gave me some help servers where I could ask questions', inline=False)
        embed.add_field(name=f'Servers', value=f'{tcc} -- This was the first server that I got help from, and they are quite active and able to help.\n{dpy} -- This is the official discord.py server, and it has an extremely active help chat, where you can get help with almost anything about discord.py.', inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['xp', 'rank', 'levels'])
    async def level(self, ctx, member: discord.Member = None):
        """Lists a users level. You can level up by talking in any channel/server that the bot is in"""
        member = ctx.author if not member else member
        member_id = str(member.id)
        owner = self.client.get_user(self.client.owner_id)
	with open("users.json", 'r') as f1:
            self.users = json.load(f1)

        if not member_id in self.users:
            await ctx.send("Member doesn't have a level. This could be because they have not talked yet.")
        else:
            embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
            embed.set_author(name=f"Level - {member}", icon_url=member.avatar_url)
            embed.add_field(name="Level", value=self.users[member_id]['level'])
            embed.add_field(name="XP", value=self.users[member_id]['exp'])
            embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
            await ctx.send(embed=embed)
    @commands.command()
    async def ligma(self, ctx):
        """Ligmabols"""
        await ctx.send("slurp")

    @commands.command(aliases=['suggestion'])
    async def suggest(self, ctx, *, arg):
        """Make a suggestion about the bot, it can be a new command that you would like to see, or anything else that you want to suggest. NOTE: do not use this command for bugs. To report a bug, use the bug command."""
        suggestion = arg
        owner = self.client.get_user(self.client.owner_id)
        embed = discord.Embed(color=0x00ff00, timestamp=ctx.message.created_at, title='Success!',description='Also, consider joining the support server: [Click here](https://discord.gg/3seAXGr)')
        embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        suggestor = ctx.author.name
        c = self.client.get_guild(727739470731935765).get_channel(751834280929525791)
        msg = await c.send(f"{suggestor} suggests {suggestion}")
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❎')
        await ctx.send(embed=embed)

    @commands.command(aliases=['bugs'])
    async def bug(self, ctx, *, arg):
        """Let the owner know about a bug in the bot. NOTE: do not use this command for suggestions. To make a suggestion, use the suggestion command."""
        report = arg
        owner = self.client.get_user(self.client.owner_id)
        reporter = ctx.author.name
        embed = discord.Embed(color=0x00ff00, timestamp=ctx.message.created_at, title='Success!',description='Also, consider joining the support server: [Click here](https://discord.gg/3seAXGr)')
        embed.set_footer(text=f"Bot made by {owner}", icon_url=owner.avatar_url)
        c = self.client.get_guild(727739470731935765).get_channel(751971356865986731)
        msg = await c.send(f"{reporter} reported {report}")
        await msg.add_reaction(emoji='✅')
        await msg.add_reaction(emoji='❎')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(MainCog(client))
