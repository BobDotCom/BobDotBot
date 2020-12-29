import discord, humanize, aiosqlite_pool, datetime, time, string, io, random, asyncio
from discord.ext import commands
import extensions.verification as verification
from claptcha import Claptcha

class Verify(commands.Cog):

    def __init__(self,bot):
        """Verify new members"""
        self.bot = bot
        self.bot.verify_pool = aiosqlite_pool.Pool("./storage/verify.db",max_connection=5)
        self.pending_verification = []

    @commands.Cog.listener()
    async def on_ready(self):
        """Setup the databases"""
        async with self.bot.verify_pool.acquire(timeout=5) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY, enabled BOOL, time INTEGER, captcha INTEGER, roleid INTEGER, channelid INTEGER, messageid INTEGER, logid INTEGER, modid INTEGER, notifid INTEGER, ping BOOL)')
                await connection.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != '\U00002705':
            return # we dont need to do anything
        async with self.bot.verify_pool.acquire(timeout=5) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT * FROM guilds WHERE id = ?',(payload.guild_id,))
                data = await cursor.fetchone()
        if not data: # not set yet
            return
        if not bool(data[1]): # not enabled
            return
        if not (payload.message_id == data[6] and payload.channel_id == data[5]):
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji,payload.member)
        if not payload.member.id in self.pending_verification:
            self.pending_verification.append(payload.member.id)
        else:
            return
        result = verification.VerifyMember(self.bot, payload, data) # this is blocking but it takes < 1ms so its fine
        role = guild.get_role(data[4])
        if role in payload.member.roles:
            self.pending_verification.remove(payload.member.id)
            return await payload.member.send('You are already verified')
        if result.failed:
            if result.needs_captcha:
                for i in range(5):
                    captcha_embed = discord.Embed(title='Captcha', description=f'Please send the text seen in this image. Once you send the correct text, you will be allowed to join **{guild.name}**. (case insensitive, letters and numbers)').set_footer(text=f'Attempt {i + 1}/5')
                    s = string.ascii_uppercase + string.ascii_lowercase + string.digits
                    rand_str = ''.join(random.choices(s, k=6))
                    c = Claptcha(rand_str, "extensions/Courier.dfont")
                    text, byte = c.bytes
                    await payload.member.send(content='Hey! I just need to make sure you are human.', embed=captcha_embed,file=discord.File(byte, 'image.png'))
                    def check(message):
                        if message.author == payload.member and not message.guild:
                            return True
                    try:
                        msg = await self.bot.wait_for('message',check=check,timeout=60)
                        if msg.content.lower() == text.lower():
                            await payload.member.send(f'Correct! You have been verified in **{guild.name}**')
                            await payload.member.add_roles(role)
                            result = verification.VerifyMember(self.bot, payload, data, override='Passed Captcha', failed=False)
                            break
                        else:
                            await payload.member.send('Incorrect!')
                            result = verification.VerifyMember(self.bot, payload, data, override="Failed Captcha", result=False)
                    except asyncio.TimeoutError:
                        await payload.member.send('Time is up! Try verifying again.')
                        result = verification.VerifyMember(self.bot, payload, data, override="Failed Captcha", result=False)
                        break
            else:
                await payload.member.send(result.failed)

        else:
            await payload.member.add_roles(role)
            try:
                await payload.member.send(f'Successfully verified in **{guild.name}**')
            except:
                pass
        if data[7] != 0 and result.embed:
            logs = guild.get_channel(data[7])
            await logs.send(embed=result.embed)
        self.pending_verification.remove(payload.member.id)

    async def verify_embed(self, ctx: commands.Context, data: tuple) -> discord.Embed:
        embed = discord.Embed(title='Guild Join Verification',description='Here are your current settings',timestamp=ctx.message.created_at)
        embed.add_field(name='Enabled',value=bool(data[1]))
        time = humanize.precisedelta(datetime.timedelta(seconds=data[2]))
        embed.add_field(name='Time before verification is allowed',value=time)
        captcha_settings = 'Always' if data[3] == 2 else 'Sometimes' if data[3] == 1 else 'Disabled'
        embed.add_field(name='Captcha Required',value=captcha_settings)
        role = None if data[4] == 0 else ctx.guild.get_role(data[4])
        embed.add_field(name='Verified Role',value=role.mention if role else role)
        message_link = f'[Click Here](https://discord.com/channels/{ctx.guild.id}/{data[5]}/{data[6]})' if data[5] and data[6] else 'Not set'
        embed.add_field(name='Reaction Message',value=message_link)
        channel = None if data[7] == 0 else ctx.guild.get_channel(data[7])
        embed.add_field(name='Log Channel',value=channel.mention if channel else channel)
        role = None if data[8] == 0 else ctx.guild.get_role(data[8])
        embed.add_field(name='Manual Verification Role',value=role.mention if role else role)
        channel = None if data[9] == 0 else ctx.guild.get_channel(data[9])
        embed.add_field(name='Manual Notification Channel',value=channel.mention if channel else channel)
        embed.add_field(name='Manual Verification Ping',value=bool(data[10]))
        return embed

    @commands.group(invoke_without_command=True)
    async def verify(self, ctx, member: discord.Member = None):
        """The command group for verification. Running this command will show you your current settings, if you specify a member, it will manually verify them. To run a subcommand, the syntax is `B.verify <subcommand> [arguments]`"""
        if member:
            command = self.bot.get_command('verify member')
            await ctx.invoke(command,member=member)
        else:
            command = self.bot.get_command('verify settings')
            await ctx.invoke(command)

    @verify.command()
    async def member(self, ctx, member: discord.Member):
        """Manually verify a member. Members with the Manual Verification role or the Kick Members permission can run this command"""
        async with self.bot.verify_pool.acquire(timeout=5) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                data = await cursor.fetchone()
        mod_role = None if data[8] == 0 else ctx.guild.get_role(data[8])
        if mod_role in ctx.author.roles or ctx.author.guild_permissions.kick_members:
            role = None if data[4] == 0 else ctx.guild.get_role(data[4])
            if role:
                await member.add_roles(role)
                try:
                    await member.send(f'You have been manually verified in **{ctx.guild.name}**')
                except:
                    pass
                await ctx.send(f'Successfully verified {member.mention}')
        else:
            await ctx.send('You do not have permissions to do that')

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def toggle(self, ctx, toggle: bool = None):
        """Toggle the verification system"""
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, 1, 0, 0, 0, 0, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        if toggle == None:
                            toggle = not bool(data[1])
                        data[1] = toggle
                        await cursor.execute('UPDATE guilds SET enabled = ? WHERE id = ?',(data[1], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def captcha(self, ctx, toggle = 'sometimes'):
        """Toggle whether the captcha is always, sometimes, or never on. 
        **Always:** Users will always have to complete a captcha, if their account is highly suspicious they will require manual verification
        **Sometimes:** Users will have to complete a captcha if their account is suspicious, if their account is highly suspicious they will require manual verification
        **Never:** Users will never have to complete a captcha, if their account is suspicious they will require manual verification"""
        toggle = 2 if toggle.lower() == 'always' else 1 if toggle.lower() == 'sometimes' else 0 if toggle.lower() == 'never' else None
        if toggle is None:
            return await ctx.send('Valid options are: always, sometimes, and never')
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, toggle, 0, 0, 0, 0, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[3] = toggle
                        await cursor.execute('UPDATE guilds SET captcha = ? WHERE id = ?',(data[3], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel = None, *, quote = 'Click here to verify'):
        """Pick a channel to start verification in, defaults to the current channel. You may also set a quote to display in the embed. The bot will send a message to that channel and people who react to it will be checked for verification"""
        async with ctx.typing():
            channel = channel or ctx.channel
            embed = discord.Embed(title='Verify',description=quote)
            embed.set_footer(text='React with \U00002705 to verify. Your DMs must be open!')
            try:
                message = await channel.send(embed=embed)
                await message.add_reaction('\U00002705')
            except:
                return await ctx.send("Please make sure I can send messages, add reactions, and manage messages in that channel!")
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, 1, 0, channel.id, message.id, 0, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[5] = channel.id
                        data[6] = message.id
                        await cursor.execute('UPDATE guilds SET channelid = ?, messageid = ? WHERE id = ?',(data[5], data[6], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)
            msg = f"""Hey, I saw you enabled my verification! Thanks! If you are experienced with setting up verification, you can ignore this. However, if you aren't quite sure that you have everything right, keep reading and I will show you some default permissions. The @everyone role should have the following permissions in #{channel}: View Channel, View Message History, NOT Send messages. In every other channel, it should have Send Messages or View Channel denied. The verified role should have no permissions to see #{channel}, but normal permissions everywhere else. I hope this helped!"""
            try:
                await ctx.author.send(msg)
            except:
                await ctx.send(f'Your DMs are closed, so I will send this here. \n{msg}')

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def role(self, ctx, role: discord.Role):
        """Set a role to gain on verification"""
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, 1, role.id, 0, 0, 0, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[4] = role.id
                        await cursor.execute('UPDATE guilds SET roleid = ? WHERE id = ?',(data[4], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def time(self, ctx, seconds: int):
        """Set an amount of time before users can verify"""
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, seconds, 1, 0, 0, 0, 0, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[2] = seconds
                        await cursor.execute('UPDATE guilds SET time = ? WHERE id = ?',(data[2], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def log(self, ctx, channel: discord.TextChannel = None):
        """Set a log channel for verification"""
        channel = channel or ctx.channel
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, 1, 0, 0, 0, channel.id, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[7] = channel.id
                        await cursor.execute('UPDATE guilds SET logid = ? WHERE id = ?',(data[7], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command(aliases=['verifier'])
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def verifyrole(self, ctx, role: discord.Role):
        """Set a role for users to manually verify members. Users with this role will be able to manually approve members."""
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, 1, 0, 0, 0, 0, role.id, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[8] = role.id
                        await cursor.execute('UPDATE guilds SET modid = ? WHERE id = ?',(data[8], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command(aliases=['notif'])
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def notification(self, ctx, channel: discord.TextChannel = None):
        """Set a notification channel for when members need to be manually verified"""
        channel = channel or ctx.channel
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, True, 0, 1, 0, 0, 0, 0, 0, channel.id, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        data[9] = channel.id
                        await cursor.execute('UPDATE guilds SET notifid = ? WHERE id = ?',(data[9], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def ping(self, ctx, toggle: bool = None):
        """Toggle whether to ping the manual verification role when someone needs to be manually verified"""
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, False, 0, 1, 0, 0, 0, 0, 0, 0, True,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    else:
                        data = list(data)
                        if toggle == None:
                            toggle = not bool(data[10])
                        data[10] = toggle
                        await cursor.execute('UPDATE guilds SET ping = ? WHERE id = ?',(data[10], ctx.guild.id,))
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send('Success!',embed=embed)

    @verify.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_guild=True)
    async def settings(self, ctx):
        async with ctx.typing():
            async with self.bot.verify_pool.acquire(timeout=5) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute('SELECT * FROM guilds WHERE id = ?',(ctx.guild.id,))
                    data = await cursor.fetchone()
                    if not data:
                        data = (ctx.guild.id, False, 0, 1, 0, 0, 0, 0, 0, 0, 0,)
                        await cursor.execute('INSERT INTO guilds (id, enabled, time, captcha, roleid, channelid, messageid, logid, modid, notifid, ping) VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
                    await connection.commit()
            embed = await self.verify_embed(ctx,data)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Verify(bot))