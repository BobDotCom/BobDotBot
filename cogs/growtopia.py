# import stuff
import discord
import aiohttp
from discord.ext import commands
from bs4 import BeautifulSoup

class GrowtopiaCog(commands.Cog, name = "Growtopia"):
    """Commands relating to the online sandbox game, Growtopia"""

    def __init__(self, client):
        self.client = client
        self.client.owner_id = 690420846774321221
        self.url = "https://growtopiagame.com"

    @commands.Cog.listener()
    async def on_ready(self):
        print('GrowtopiaCog is active')
    @commands.command(aliases=["rw", "render"])
    async def renderworld(self,ctx,world):
        """Get a render of a world in Growtopia
        Uses: `B.renderworld <world>`"""
        async with ctx.typing():
            async with aiohttp.ClientSession() as sess:
                async with sess.get(self.url+f'/worlds/{world.lower()}.png') as resp:
                    if not resp.status == 200:
                        embed = discord.Embed(color=discord.Color.red(), timestamp=ctx.message.created_at, title=f"That world hasn't been rendered yet")
                        await ctx.send(embed=embed)
                        return
                    embed = discord.Embed(title=f"Here is a render of the world: {world.upper()}")
                    embed.set_image(url=self.url+f'/worlds/{world.lower()}.png') 
                    await ctx.send(embed=embed)             
    @commands.command(aliases=["gt"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def online(self,ctx):
        """See how many people are playing the game right now
        Uses: `B.online`"""
        async with aiohttp.ClientSession() as sess:
            async with sess.get(self.url+'/detail') as resp:
              data = await resp.json(content_type="text/html")
              data = data["online_user"]
        embed = discord.Embed(timestamp=ctx.message.created_at, title=f"Growtopia stats", description=f"Players online: {data}")
        await ctx.send(embed=embed)
    @commands.command(aliases=["wiki"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def gt_wiki(self,ctx,*,item):
        item = item.replace(" ","+")
        url = "https://growtopia.fandom.com/wiki/"
        search = "Special:Search?query=" + item
        async with aiohttp.ClientSession() as cs:
          async with cs.get(url + search) as r:
            html = await r.text()
        soup = BeautifulSoup(html, 'html.parser')
        article = ''
        content = soup.find('li', {"class": "unified-search__result"})
        for i in content.findAll('article'):
          article = article + ' ' +  i.text
        start = article.find("https://")
        items_link = article[start:].replace("\n","")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url + "Dirt") as r:
                html = await r.text()
        soup1 = BeautifulSoup(html, 'html.parser')
        contents = soup1.find('div', {"class": "gtw-card item-card"})
        article = ''
        article1 = ''
        for i in contents.findAll('div',"card-text"):
            article = article + ' ' +  i.text
        for i in contents.findAll('div',"card-header"):
            article1 = article1 + ' ' +  i.text
        contents1 = soup1.find('span', {"class": "growsprite"})
        x = ''
        for i in contents1.findAll("img"):
            x = x + ' ' +  i["src"]
        class html:
          content = article[:-53]
          content1 = article1
          thumbnail = x
        embed = discord.Embed(title=article1,description=html.content,timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=html.thumbnail)
        await ctx.send(embed=embed)
def setup(client):
    client.add_cog(GrowtopiaCog(client))
