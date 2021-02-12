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
    self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5001) 
    self.update_stats.start()

  # The decorator below will work only on discord.py 1.1.0+ 
  # In case your discord.py version is below that, you can use self.bot.loop.create_task(self.update_stats()) 

  @tasks.loop(minutes=30.0) 
  async def update_stats(self):
    """This function runs every 30 minutes to automatically update your server count"""
    try: 
      await self.dblpy.post_guild_count() 
    except Exception as e: 
      print('failed to update stats')

    # if you are not using the tasks extension, put the line below 

    # await asyncio.sleep(1800) 

  @commands.Cog.listener() 
  async def on_dbl_vote(self, data): 
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
  bot.add_cog(TopGG(bot))
