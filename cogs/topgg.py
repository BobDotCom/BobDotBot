"""
This is copied from their docs, honestly I didn't look what it did but it appears to work
"""
import dbl
import discord 
from discord.ext import commands, tasks
import asyncio 
import logging 
class TopGG(commands.Cog): 
  """Handles interactions with the top.gg API"""
 
  def __init__(self, bot): 
    self.bot = bot 
    self.token = self.bot.dbltoken # set this to your DBL token 
    self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000) 
    self.update_stats.start()

  # The decorator below will work only on discord.py 1.1.0+ 
  # In case your discord.py version is below that, you can use self.bot.loop.create_task(self.update_stats()) 

  @tasks.loop(minutes=30.0) 
  async def update_stats(self): 
    print("test")
    """This function runs every 30 minutes to automatically update your server count"""
    logger.info('Attempting to post server count') 
    try: 
      await self.dblpy.post_guild_count() 
      logger.info('Posted server count ({})'.format(self.dblpy.guild_count())) 
      print("test2")
    except Exception as e: 
      logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e)) 

    # if you are not using the tasks extension, put the line below 

    # await asyncio.sleep(1800) 

  @commands.Cog.listener() 
  async def on_dbl_vote(self, data): 
    logger.info('Received an upvote') 
    print(data) 
    channel = await self.bot.fetch_channel(781291858071912448)
    await channel.send("Upvoted!")
    chnl = await self.bot.fetch_channel(781292491576049665)
    await chnl.send(str(data))

  @commands.command(aliases=["top.gg",'dbl'])
  async def topgg(self,ctx):
    await ctx.send(embed=discord.Embed(title="Top.gg link",description="[Click Here](https://top.gg/bot/746045299125911562) to go to the main page"))

  @commands.command()
  async def vote(self,ctx):
    await ctx.send(embed=discord.Embed(title="Top.gg vote link",description="[Click Here](https://top.gg/bot/746045299125911562/vote) to vote for my bot! Thank you!"))

def setup(bot): 
  global logger 
  logger = logging.getLogger('bot') 
  bot.add_cog(TopGG(bot))