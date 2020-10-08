import discord, datetime, time, aiohttp, asyncio, random
from discord.ext import commands
from random import randint
from random import choice
from urllib.parse import quote_plus
from collections import deque

acceptableImageFormats = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]
memeHistory = deque()
memeSubreddits = ["BikiniBottomTwitter", "memes", "2meirl4meirl", "deepfriedmemes", "MemeEconomy"]

async def getSub(self, ctx, sub):
        """Get stuff from requested sub"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r{sub}/hot.json?limit=450") as response:
                request = await response.json()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                print("failed request {}".format(attempts))
                await asyncio.sleep(2)
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=450") as response:
                        request = await response.json()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'url' in val['data']:
                        url = val['data']['url']
                        urlLower = url.lower()
                        accepted = False
                        for j, v, in enumerate(acceptableImageFormats): #check if it's an acceptable image
                            if v in urlLower:
                                accepted = True
                        if accepted:
                            if url not in memeHistory:
                                memeHistory.append(url)  #add the url to the history, so it won't be posted again
                                if len(memeHistory) > 500: #limit size
                                    memeHistory.popleft() #remove the oldest

                                break #done with this loop, can send image
                embed = discord.Embed(title=sub, timestamp=ctx.message.created_at, color=discord.Color.blurple())
                embed.set_image(url=memeHistory[len(memeHistory) - 1])
                await ctx.send(embed=embed) #send the last image
                return
        await ctx.send("_{}! ({})_".format(str(request['message']), str(request['error'])))

class Reddit(commands.Cog):
    """Reddit features."""
    def __init__(self, client):
        self.bot = client

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def meme(self, ctx):
      """Memes from various subreddits"""
      async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.reddit.com/r/{0}/hot.json?limit=450".format(random.choice(memeSubreddits))) as response:
                request = await response.json()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                print("failed request {}".format(attempts))
                await asyncio.sleep(2)
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://www.reddit.com/r/{0}/hot.json?limit=450".format(random.choice(memeSubreddits))) as response:
                        request = await response.json()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'url' in val['data']:
                        url = val['data']['url']
                        urlLower = url.lower()
                        accepted = False
                        for j, v, in enumerate(acceptableImageFormats): 
                            if v in urlLower:
                                accepted = True
                        if accepted:
                            if url not in memeHistory:
                                memeHistory.append(url)  
                                if len(memeHistory) > 500: 
                                    memeHistory.popleft() 

                                break 
                embed = discord.Embed(title=f"Meme", timestamp=ctx.message.created_at, color=discord.Color.blurple())
                embed.set_image(url=memeHistory[len(memeHistory) - 1])
                await ctx.send(embed=embed)
                return
        await ctx.send(url="_{}! ({})_".format(str(request['message']), str(request['error'])))
    
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def showerthought(self, ctx):
      """A random showerthought from r/showerthoughts"""
      async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.reddit.com/r/showerthoughts/hot.json?limit=450") as response:
                request = await response.json()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                print("failed request {}".format(attempts))
                await asyncio.sleep(2)
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://www.reddit.com/r/showerthoughts/hot.json?limit=450") as response:
                        request = await response.json()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'title' in val['data']:
                        url = val['data']['title']
                        urlLower = url.lower()
                        accepted = False
                        if url == "What Is A Showerthought?":
                            accepted = False
                        elif url == "Showerthoughts is looking for new moderators!":
                            accepted = False
                        else:
                            accepted = True
                        if accepted:
                            if url not in memeHistory:
                                memeHistory.append(url)
                                if len(memeHistory) > 63:
                                    memeHistory.popleft()

                                break
                embed = discord.Embed(title=f"Showerthought", timestamp=ctx.message.created_at, description=memeHistory[len(memeHistory) - 1], color=discord.Color.blurple())
                await ctx.send(embed=embed)
                return
        await ctx.send("_{}! ({})_".format(str(request['message']), str(request['error'])))

    
    @commands.command(aliases=['dankmeme', 'dank'])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def dankmemes(self, ctx):
      """Get an image from the dankmemes subreddit. Uses: `B.dankmemes`"""
      async with ctx.typing():
        await getSub(self, ctx, 'dankmemes')
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def me_irl(self, ctx):
      """Get an image from the me_irl subreddit. Uses: `B.me_irl`"""
      async with ctx.typing():
        await getSub(self, ctx, 'me_irl')

    @commands.command(aliases=["ph"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def programmerhumor(self, ctx):
      """Get an image from the ProgrammerHumor subreddit. Uses: `B.programmerhumor`"""
      async with ctx.typing():
        await getSub(self, ctx, 'ProgrammerHumor')
        
    @commands.command(aliases=["ri"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def redditimage(self, ctx, arg):
      """Get an image from a subreddit. Uses: `B.redditimage memes`"""
      async with ctx.typing():
        await getSub(self, ctx, arg)
def setup(client):
    client.add_cog(Reddit(client))
