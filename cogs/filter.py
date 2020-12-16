import discord, re, json, aiosqlite
from discord.ext import commands,tasks


class FilterCog(commands.Cog, name = "Filter"):
    """Commands for filtering things"""

    def __init__(self, client):
        self.client = client
        self.channel = 745390366802575391
        #self.sync_filter.start()

    # LISTENERS #

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('CREATE TABLE IF NOT EXISTS guilds (id INTEGER, ignored TEXT, words TEXT, enabled BOOL);')
                await connection.commit()

    @commands.Cog.listener()
    async def on_message(self,message):
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT words, ignored, enabled FROM guilds WHERE id = ?',(message.guild.id,))
                data = await cursor.fetchone()
                enabled = data[2]
                words = None
                try:
                    words = json.loads(data[0])
                    ignored = json.loads(data[1])
                except:
                    words = words or []
                    ignored = []
        new_message = message.content
        caught = False
        if enabled and not message.channel.id in ignored:
            for word in words:
                if re.search('+\s*'.join(word),message.content):
                    caught = True
                    try:
                        await message.delete()
                    except:
                        pass
                    new_message = re.sub('+'.join(word),'\*'*len(word),new_message)
            if caught:
                webhooks = await message.channel.webhooks()
                try:
                    webhook = webhooks[0]
                except:
                    try:
                        webhook = await message.channel.create_webhook(name='BobDotBot filter')
                    except:
                        pass
                if webhook:
                    member = message.author # We get the member
                    await webhook.send( # We send 
                        content=new_message, # The message
                        username=member.nick or member.name, # The user name
                        avatar_url=member.avatar_url # the user avatar
                    )

    # COMMANDS #

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def filter(self,ctx):
        """Toggle the word filter. When the filter is on, messages are automatically deleted, and replaced with a filtered webhook message, with the avatar and name set. The bot needs manage message and create webhook permissions for this to work."""
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT enabled FROM guilds WHERE id = ?',(ctx.guild.id,))
                previous = await cursor.fetchone()
                if not previous:
                    await cursor.execute('INSERT INTO guilds (id, ignored, words, enabled) VALUES (?,?,?,?)',(ctx.guild.id,'','',True,))
                    previous = False
                else:
                    previous = previous[0]
                    await cursor.execute('UPDATE guilds SET enabled = ? WHERE id = ?',(not previous,ctx.guild.id,))
                await connection.commit()
        await ctx.send(f'filter status: {not previous}')

    @filter.command()
    @commands.has_permissions(manage_channels=True)
    async def add(self,ctx,word):
        """Add a word to the filter"""
        try:
            await ctx.message.delete()
        except:
            pass
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT words FROM guilds WHERE id = ?',(ctx.guild.id,))
                data = await cursor.fetchone()
                if data:
                    try:
                        words = json.loads(data[0])
                    except:
                        words = []
                    if not word in words:
                        words.append(word)
                        await cursor.execute('UPDATE guilds SET words = ? WHERE id = ?',(json.dumps(words),ctx.guild.id,))
                        await ctx.send("added to filter")
                    else:
                        await ctx.send('That is already in the filter')
                else:
                    await cursor.execute('INSERT INTO guilds (id, ignored, words, enabled) VALUES (?,?,?,?)',(ctx.guild.id,'',json.dumps([word]),False,))
                await connection.commit()

    @filter.command()
    @commands.has_permissions(manage_channels=True)
    async def remove(self,ctx,word):
        """Remove a word from the filter"""
        try:
            await ctx.message.delete()
        except:
            pass
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT words FROM guilds WHERE id = ?',(ctx.guild.id,))
                data = await cursor.fetchone()
                if data:
                    if data[0]:
                        words = json.loads(data[0])
                    else:
                        words = []
                    if word in words:
                        words.remove(word)
                        await cursor.execute('UPDATE guilds SET words = ? WHERE id = ?',(json.dumps(words),ctx.guild.id,))
                        await ctx.send("removed from filter")
                    else:
                        await ctx.send("That isn't in the filter")
                else:
                    await cursor.execute('INSERT INTO guilds (id, ignored, words, enabled) VALUES (?,?,?,?)',(ctx.guild.id,'',json.dumps([word]),False,))
                await connection.commit()
    
    @filter.command(aliases=['list'])
    @commands.has_permissions(manage_channels=True)
    async def words(self,ctx):
        """Get a list of currently filtered words"""
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT words FROM guilds WHERE id = ?',(ctx.guild.id,))
                data = await cursor.fetchone()
        try:
            try:
                data = json.loads(data[0])
            except:
                return await ctx.send("No word filter set")
            if len(data) > 0:
                await ctx.author.send(f"Current word list: `{', '.join(data)}`")
            else:
                await ctx.author.send(f"No words")
            await ctx.send("Check your DMs")
        except:
            await ctx.send("Please open your DMs")

    @filter.command()
    @commands.has_permissions(manage_channels=True)
    async def ignore(self,ctx,channel: discord.TextChannel = None):
        """Ignore a channel. Defaults to the current channel if none is specified."""
        channel = channel or ctx.channel
        async with aiosqlite.connect('filter.db') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT ignored FROM guilds WHERE id = ?',(ctx.guild.id,))
                data = await cursor.fetchone()
                if data:
                    if data[0]:
                        channels = json.loads(data[0])
                    else:
                        channels = []
                    if not channel.id in channels:
                        channels.append(channel.id)
                        await ctx.send(f"Ok, I will start ignoring {channel.mention}")
                    else:
                        channels.remove(channel.id)
                        await ctx.send(f"Ok, I will stop ignoring {channel.mention}")
                    await cursor.execute('UPDATE guilds SET ignored = ? WHERE id = ?',(json.dumps(channels),ctx.guild.id,))
                    await connection.commit()
                else:
                    await ctx.send("Please enable the filter first!")

    # LOOPS #

    @tasks.loop(seconds=60)
    async def sync_filter(self):
        with open('filter.json','r') as f:
            data = json.load(f)
        self.filtered_words = data['words']

    # CHECKS #

    async def cog_check(self,ctx):
        return True # ctx.author.id == 690420846774321221

def setup(client):
    client.add_cog(FilterCog(client))
