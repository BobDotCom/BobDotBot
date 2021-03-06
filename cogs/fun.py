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

import sr_api
import discord
import asyncio
import random
import os
from io import BytesIO
from dotenv import load_dotenv
from discord.ext import commands
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
          await ctx.send("error")
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
    
    def percentage_bool(self,x: int) -> bool:
        if x > 100:
            raise ValueError('Number must be ≤ 100')
        return bool(int(random.choice(list("1" * x) + list("0" * (100-x)))))

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def amongus(self, ctx, member: discord.Member = None, impostor: bool = None):
      """Eject a member of the current server into space. If you dont say whether they are the impostor or not, there will be a 1 in 10 chance that they are."""
      async with ctx.typing():
        impostor = self.percentage_bool(10) if impostor == None else impostor # have to do this because impostor can be false or none
        member = member or ctx.author
        try:
          gif = api.amongus(member.name, member.avatar_url,impostor) # if sr api has been updated
        except:
          gif = api.amongus(member.name, member.avatar_url) # if sr_api hasnt been updated yet
          if impostor:
            await ctx.send('Dutchy hasnt updated the wrapper, or Bob hasnt installed the new version yet. For now, I can only eject crewmates. Loading...')
        try:
          buf = BytesIO(await gif.read())
        except ValueError as error:
          embed = discord.Embed(title='Error with API',description='```{}```'.format(error))
          await ctx.send(embed=embed)
          if '403' in str(error):
            await ctx.send('I have detected that this error is because my API key expired! Please contact my owner, {0.mention} ({0}), and remind him to renew my API key!'.format(self.bot.get_user(self.bot.owner_ids[0])))
        else:
          await ctx.send(file=discord.File(buf, filename=f"{member.name}.gif"))

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def petpet(self, ctx, member: discord.Member = None):
      """Pet someone. Defaults to yourself"""
      async with ctx.typing():
        member = member or ctx.author
        try:
          gif = api.petpet(member.avatar_url) # if sr api has been updated
        except:
          return await ctx.send('Dutchy hasnt updated the wrapper, or Bob hasnt installed the new version yet. I cannot provide petpet images until both of these happen.')
        try:
          buf = BytesIO(await gif.read())
        except ValueError as error:
          embed = discord.Embed(title='Error with API',description='```{}```'.format(error))
          await ctx.send(embed=embed)
          if '403' in str(error):
            await ctx.send('I have detected that this error is because my API key expired! Please contact my owner, {0.mention} ({0}), and remind him to renew my API key!'.format(self.bot.get_user(self.bot.owner_ids[0])))
        else:
          await ctx.send(file=discord.File(buf, filename=f"{member.name}.gif"))

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def dog(self,ctx):
      """Get an image/fact about dogs"""
      async with ctx.typing():
        await get_the_image(self,ctx,"dog")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def cat(self,ctx):
      """Get an image/fact about cats"""
      async with ctx.typing():
        await get_the_image(self,ctx,"cat")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def panda(self, ctx):
      """Get an image/fact about pandas"""
      async with ctx.typing():
        await get_the_image(self, ctx, "panda")
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def red_panda(self,ctx):
      """Get an image/fact about red pandas"""
      async with ctx.typing():
        await get_the_image(self,ctx,"red_panda")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def fox(self,ctx):
      """Get an image/fact about foxes"""
      async with ctx.typing():
        await get_the_image(self,ctx,"fox")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def bird(self, ctx):
      """Get an image/fact about birds"""
      async with ctx.typing():
        await get_the_image(self, ctx, "birb")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def koala(self, ctx):
      """Get an image/fact about koalas"""
      async with ctx.typing():
        await get_the_image(self, ctx, "koala")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def kangaroo(self, ctx):
      """Get an image/fact about kangaroos"""
      async with ctx.typing():
        await get_the_image(self, ctx, "kangaroo")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def giraffe(self,ctx):
      """Get an image/fact about giraffes"""
      async with ctx.typing():
        await get_the_image(self,ctx,"giraffe")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def whale(self,ctx):
      """Get an image/fact about whales"""
      async with ctx.typing():
        await get_the_image(self,ctx,"whale")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def raccoon(self,ctx):
      """Get an image/fact about racoons"""
      async with ctx.typing():
        await get_the_image(self,ctx,"raccoon")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def pikachu(self,ctx):
      """Get an image/fact about pikachu"""
      async with ctx.typing():
        await get_the_image(self,ctx,"pikachu")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def elephant(self,ctx):
      """Get an image/fact about elephants"""
      async with ctx.typing():
        await get_the_image(self,ctx,"elephant")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def random_token(self, ctx):
      """Get a random token (they are fake, just randomly generated)"""
      async with ctx.typing():
        token = await api.bot_token()
        await ctx.send(token)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def wink(self, ctx):
      """Get a wink gif"""
      async with ctx.typing():
        await get_the_gif(self, ctx, "wink")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def pat(self,ctx):
      """Get a pat gif"""
      async with ctx.typing():
        await get_the_gif(self,ctx,"pat")
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def hug(self,ctx):
      """Get a hug gif"""
      async with ctx.typing():
        await get_the_gif(self,ctx,"hug")
    @commands.command(aliases=["fp"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def facepalm(self,ctx):
      """Get a facepalm gif"""
      async with ctx.typing():
        await get_the_gif(self,ctx,"face-palm")
    
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def chatbot(self,ctx,*,chat = None):
      """Start a chat with a bot. Once you send your first message, the bot will reply to your messages until you say cancel, or it times out"""
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
                  try:
                    data = await asyncio.wait_for(api.chatbot(source), timeout=5)
                  except asyncio.TimeoutError:
                    await asyncio.sleep(5)
                    data = await asyncio.wait_for(api.chatbot(source), timeout=5)
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
      """Get information about a minecraft player"""
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
      """Get information about a pokemon from a pokedex"""
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
      """Take a string of ASCII text and translate it to base64"""
      async with ctx.typing():
        asdf = await api.encode_base64(arg)
        embed=discord.Embed(title="Text to Base64",description=asdf,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command(aliases=["base64_decode"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def decode(self,ctx,*,arg):
      """Take a string of base64 and translate it back to ASCII text"""
      async with ctx.typing():
        asdf = await api.decode_base64(arg)
        embed=discord.Embed(title="Base64 to Text",description=asdf,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def anothermemecommandlol(self,ctx):
      """A less advanced meme command. Not reccomended for use"""
      async with ctx.typing():
        asdf = await api.get_meme()
        embed = discord.Embed(title=asdf.category,description=asdf.caption,timestamp=ctx.message.created_at)
        embed.set_image(url=asdf.image)
        embed.set_footer(text=f"Meme ID: {asdf.id}")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def animequote(self,ctx):
      """Get a random quote from an anime"""
      async with ctx.typing():
        asdf = await api.anime_quote()
        anime = asdf.anime.strip(" ")
        character = asdf.character.strip(" ")
        embed = discord.Embed(title=f"From: {anime} | Said by: {character}",description=asdf.quote,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def joke(self,ctx):
      """Get a random joke"""
      async with ctx.typing():
        asdf = await api.get_joke()
        embed=discord.Embed(title="Joke",description=asdf,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def youtube(self,ctx,member: discord.Member,*,comment):
      """Pretend to comment as someone else on youtube"""
      async with ctx.typing():
        asdf = api.youtube_comment(member.avatar_url, member.name, comment)
        buf = BytesIO(await asdf.read())
        await ctx.send(file=discord.File(buf, filename=f"{member.name}_youtube.png"))
    @commands.command(aliases=["ytm"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def youtubeme(self,ctx,*,comment):
      """Get an image of you commenting on youtube"""
      async with ctx.typing():
        member = ctx.author
        asdf = api.youtube_comment(member.avatar_url, member.name, comment)
        buf = BytesIO(await asdf.read())
        await ctx.send(file=discord.File(buf, filename=f"{member.name}_youtube.png"))
    @commands.command(aliases=["word"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def define(self,ctx,arg):
      """Get the definition of a word. Currently not working"""
      async with ctx.typing():
        asdf = await api.define(arg)
        embed=discord.Embed(title=asdf.word,description=asdf.definition,timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def gay(self,ctx,member: discord.Member = None):
      """Get a gay pfp of any user"""
      async with ctx.typing():
        member = ctx.author if not member else member
        await get_thingy(self,ctx,"gay",member)
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def triggered(self, ctx, *, member: discord.Member = None):
      """Get a triggered photo of any user"""
      async with ctx.typing():
        member = ctx.author if not member else member
        await get_thingy(self,ctx,"triggered",member)
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def wide(self, ctx, *, text):
      """Widen your text"""
      await ctx.send(' '.join([x for x in text]))

def setup(client):
    client.add_cog(FunCog(client))
