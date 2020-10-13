import sr_api
import discord
import datetime
from discord.ext import commands
from discord.ext.commands import Bot, BucketType
api = sr_api.Client()

class FunCog(commands.Cog, name = "Fun"):
    """Fun Commands"""
    def __init__(self, client):
        self.client = client
        self.bot = client
        owner = self.client.get_user(self.client.owner_id)
        self.client.owner_id = 690420846774321221


    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def catpic(self,ctx):
      async with aiohttp.ClientSession() as sess:
        async with sess.get(self.api + '/img/cat') as resp:
          data = await resp.json()
          data = data["link"]
          embed = discord.Embed(title="Cat")
          embed.set_image(url=data)
          await ctx.send(embed=embed)
      await sess.close()
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    @commands.max_concurrency(1, per=BucketType.channel)
    async def chatbot(self,ctx,*,chat = None):
        """Start a chat with a bot. Once you send your first message
        Uses `chatbot <chat>`
        Once you send your first message, the bot will reply to your messages until you say cancel"""
        if chat:
          async with ctx.typing():
            try:
                data = await api.chatbot(chat)
                embed = discord.Embed(title="Chatbot says:",description=data,timestamp=ctx.message.created_at)
                embed.set_footer(text="Chatbot api by some-random-api - Say cancel to exit\nTimeout:45 seconds")
                await ctx.send(embed=embed)
            except:
                await ctx.send("Error with Chatbot, please try again later")
                return
        else:
          async with ctx.typing():
            embed = discord.Embed(title="I started a chat for you with AI. Type any message to send to the bot, or type cancel to exit",timestamp=ctx.message.created_at)
            await ctx.send(embed=embed)
        done = False
        while not done:
            err = None
            def check(msg):
              return msg.author == ctx.author and msg.channel == ctx.channel
            try:
              m = await ctx.bot.wait_for('message', check=check, timeout=45.0)
            except asyncio.TimeoutError:
              err = 'timeout'
            async with ctx.typing():
              source = m.content
              if m.content == 'cancel' or m.content == "Cancel":
                err = 'cancel'
              if err == 'cancel':
                    await ctx.send(':white_check_mark:')
                    done = True
              elif err == 'timeout':
                    await ctx.send(':alarm_clock: **Time\'s up bud**')
                    done = True
              else:
                try:
                    data = await api.chatbot(source)
                    embed = discord.Embed(title="Chatbot says:",description=data,timestamp=ctx.message.created_at)
                    embed.set_footer(text="Chatbot: some-random-api - cancel - Timeout:45")
                    await ctx.send(embed=embed)
                except:
                    await ctx.send("Error with Chatbot, please try again later")
                    return
                  
                  
                  
def setup(client):
    client.add_cog(FunCog(client))
