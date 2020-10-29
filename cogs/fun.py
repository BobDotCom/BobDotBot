import sr_api
import discord
import datetime
import asyncio
import os
import aiohttp
from io import BytesIO
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import Bot, BucketType
from aiohttp import request
load_dotenv()
SR_API_TOKEN = os.getenv("SR_API_TOKEN")
api = sr_api.Client(SR_API_TOKEN)
async def get_the_image(self, ctx, animal):
    try:
      data = await api.get_image(animal)
    except:
      data = "None"
    try:
      animal = "bird" if animal == "birb" else animal
      fact = await api.get_fact(getattr(sr_api.Animal,animal))
    except:
      fact = "No fact provided"
    embed = discord.Embed(title=animal,description=fact,timestamp=ctx.message.created_at)
    if data != "None":
      embed.set_image(url=data)
    await ctx.send(embed=embed)
    
async def get_thingy(self,ctx,type,member):
        try:
          gif = api.filter(type, member.avatar_url)
          buf = BytesIO(await gif.read())
          await ctx.send(file=discord.File(buf, filename=f"{member.name}.gif"))
          worked = True
        except: #HTTPError as error
          try:
            await ctx.send(f'Error: {error.code}, Reason:{error.reason}. API may be down')
          except:
            await ctx.send("error")
        else:
          if not worked:
            await ctx.send('i am dead')
    
async def get_the_gif(self, ctx, option):
  try:
    data = await api.get_gif(option)
  except:
    await ctx.send("error")
  else:
    embed = discord.Embed(title=option)
    embed.set_image(url=data)
    await ctx.send(embed=embed)

class FunCog(commands.Cog, name = "Fun"):
    """Fun Commands"""
    def __init__(self, client):
        self.client = client
        self.bot = client
        self.client.owner_id = 690420846774321221

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def amongus(self, ctx, *, member: discord.Member = None):
      async with ctx.typing():
        member = ctx.author if not member else member
        try:
          gif = api.amongus(member.name, member.avatar_url)
          buf = BytesIO(await gif.read())
          await ctx.send(file=discord.File(buf, filename=f"{member.name}.gif"))
          worked = True
        except: #HTTPError as error
          try:
            await ctx.send(f'Error: {error.code}, Reason:{error.reason}. API may be down')
          except:
            await ctx.send("error")
        else:
          if not worked:
            await ctx.send('This command requires a premium API key, and the key that I use has expired! To be able to use this command, contact my owner(@BobDotCom#0001) to discuss it.(This could also mean that the website is down)')

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def dog(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"dog")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def cat(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"cat")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def panda(self, ctx):
      async with ctx.typing():
        await get_the_image(self, ctx, "panda")
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def red_panda(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"red_panda")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def fox(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"fox")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def bird(self, ctx):
      async with ctx.typing():
        await get_the_image(self, ctx, "birb")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def koala(self, ctx):
      async with ctx.typing():
        await get_the_image(self, ctx, "koala")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def kangaroo(self, ctx):
      async with ctx.typing():
        await get_the_image(self, ctx, "kangaroo")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def giraffe(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"giraffe")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def whale(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"whale")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def raccoon(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"raccoon")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def pikachu(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"pikachu")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def elephant(self,ctx):
      async with ctx.typing():
        await get_the_image(self,ctx,"elephant")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def random_token(self, ctx):
      async with ctx.typing():
        token = await api.bot_token()
        await ctx.send(token)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def wink(self, ctx):
      async with ctx.typing():
        await get_the_gif(self, ctx, "wink")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def pat(self,ctx):
      async with ctx.typing():
        await get_the_gif(self,ctx,"pat")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def hug(self,ctx):
      async with ctx.typing():
        await get_the_gif(self,ctx,"hug")
    @commands.command(aliases=["fp"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def facepalm(self,ctx):
      async with ctx.typing():
        await get_the_gif(self,ctx,"face-palm")
    
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    @commands.max_concurrency(1, per=BucketType.channel)
    async def chatbot(self,ctx,*,chat = None):
      """Start a chat with a bot. Once you send your first message
      Uses `chatbot <chat>`
      Once you send your first message, the bot will reply to your messages until you say cancel"""
      errortimes = 0
      try:
        if chat:
          async with ctx.typing():
            try:
                data = await api.chatbot(chat)
                embed = discord.Embed(title="Chatbot says:",description=data,timestamp=ctx.message.created_at)
                embed.set_footer(text="Chatbot api by some-random-api - Say cancel to exit\nTimeout:45 seconds")
                await ctx.send(embed=embed)
            except:
                await ctx.send("Error with Chatbot, please send another message. If this continues, it will automatically exit. Send cancel to cancel")
                errortimes += 1
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
                    embed = discord.Embed(title="Chatbot says:",description=data)
                    embed.set_footer(text=f"Say cancel to exit - Timeout:45s - started at: {ctx.message.created_at}")
                    await ctx.send(embed=embed)
                except:
                  if errortimes <= 3:
                    await ctx.send("Error with Chatbot, please send another message. If this continues, it will automatically exit. Send cancel to cancel")
                    errortimes += 1
                  else:
                    await ctx.send("Error with Chatbot continued, please try again later")
                    return
      except:
        try:
            await ctx.send("Error with Chatbot, please try again later")
            return
        except:
            return
    @commands.command(aliases=["mc"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def minecraft(self,ctx,*,username):
      async with ctx.typing():
        user = await api.mc_user(username)
        try:
          embed = discord.Embed(title='Minecraft User Details:',description="Provided by some-random-api",timestamp=ctx.message.created_at)
          embed.add_field(name="Username:",value=user.name)
          embed.add_field(name='User UUID',value=user.uuid)
          embed.add_field(name='Name History',value=user.formatted_history)
        except:
          embed = discord.Embed(title='Error',descriptiom="Api may be down",timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def pokemon(self, ctx, name):
      async with ctx.typing():
        x = await api.get_pokemon(name)
        try:
          embed = discord.Embed(title='Pokémon Details:',description="Provided by some-random-api",timestamp=ctx.message.created_at)
          embed.add_field(name="Name",value=x.name)
          embed.add_field(name="ID", value=x.id)
          embed.add_field(name="Type",value=', '.join(x.type))
          embed.add_field(name="Abilities",value=', '.join(x.abilities))
          embed.add_field(name="Height",value=x.height)
          embed.add_field(name="Weight", value=x.weight)
          embed.add_field(name="Base Experience",value=x.base_experience)
          embed.add_field(name="Gender",value=', '.join(x.gender))
          embed.add_field(name="Egg Groups", value=', '.join(x.egg_groups))
          embed.add_field(name="HP", value=x.hp)
          embed.add_field(name="Attack", value=x.attack)
          embed.add_field(name="Defense",value=x.defense)
          embed.add_field(name="Special Attack",value=x.sp_atk)
          embed.add_field(name="Special Defense",value=x.sp_def)
          embed.add_field(name="Speed",value=x.speed)
          embed.add_field(name="Total",value=x.total)
          embed.add_field(name="Evolution Stage",value=x.evolutionStage)
          embed.add_field(name="Evolution Line",value=', '.join(x.evolutionLine))
          embed.add_field(name="Description",value=x.description)
          embed.add_field(name="Generation",value=x.generation)
          #embed.set_image(url=x.spriteNormal)
          embed.set_thumbnail(url=x.spriteAnimated)
          await ctx.send(embed=embed)
        except:
          await ctx.send("error")
    @commands.command(aliases=["ttb", "text_to_binary"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def binary(self,ctx,*,arg):
        """Take a string of ASCII text and translate it to binary"""
        binary = ' '.join(format(ord(i), 'b') for i in arg)
        embed = discord.Embed(timestamp=ctx.message.created_at, title="Text to binary", description=binary)
        await ctx.send(embed=embed)
    @commands.command(aliases=["btt", "binary_to_text"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def text(self,ctx,*,arg):
        """Take a string of binary and translate it back to ASCII text"""
        lists = ""
        newarg = arg.split(" ")
        for x in newarg:
            asdf = chr(int(x, 2))
            thevar = (lists,asdf)
            lists = "".join(thevar)
        embed = discord.Embed(timestamp=ctx.message.created_at, title="Binary to text", description=lists)
        await ctx.send(embed=embed)
    @commands.command(aliases=["base64"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def encode(self,ctx,*,arg):
      async with ctx.typing():
        asdf = await api.encode_base64(arg)
        embed=discord.Embed(title="Text to Base64",description=asdf,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command(aliases=["base64_decode"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def decode(self,ctx,*,arg):
      async with ctx.typing():
        asdf = await api.decode_base64(arg)
        embed=discord.Embed(title="Base64 to Text",description=asdf,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def anothermemecommandlol(self,ctx):
      async with ctx.typing():
        asdf = await api.get_meme()
        embed = discord.Embed(title=asdf.category,description=asdf.caption,timestamp=ctx.message.created_at)
        embed.set_image(url=asdf.image)
        embed.set_footer(text=f"Meme ID: {asdf.id}")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def animequote(self,ctx):
      async with ctx.typing():
        asdf = await api.anime_quote()
        anime = asdf.anime.strip(" ")
        character = asdf.character.strip(" ")
        embed = discord.Embed(title=f"From: {anime} | Said by: {character}",description=asdf.quote,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def joke(self,ctx):
      async with ctx.typing():
        asdf = await api.get_joke()
        embed=discord.Embed(title="Joke",description=asdf,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def youtube(self,ctx,member: discord.Member,*,comment):
      async with ctx.typing():
        asdf = api.youtube_comment(member.avatar_url, member.name, comment)
        buf = BytesIO(await asdf.read())
        await ctx.send(file=discord.File(buf, filename=f"{member.name}_youtube.png"))
    @commands.command(aliases=["ytm"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def youtubeme(self,ctx,*,comment):
      async with ctx.typing():
        member = ctx.author
        asdf = api.youtube_comment(member.avatar_url, member.name, comment)
        buf = BytesIO(await asdf.read())
        await ctx.send(file=discord.File(buf, filename=f"{member.name}_youtube.png"))
    @commands.command(aliases=["word"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def define(self,ctx,arg):
      async with ctx.typing():
        asdf = await api.define(arg)
        embed=discord.Embed(title=asdf.word,description=asdf.definition,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def gay(self,ctx,member: discord.Member = None):
      async with ctx.typing():
        member = ctx.author if not member else member
        await get_thingy(self,ctx,"gay",member)
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def triggered(self, ctx, *, member: discord.Member = None):
      async with ctx.typing():
        member = ctx.author if not member else member
        await get_thingy(self,ctx,"triggered",member)
        

def setup(client):
    client.add_cog(FunCog(client))
