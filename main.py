import datetime
import discord
from discord.ext import commands
from discord.ui import Button, View
import disnake
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

prefix = '+'
emg = None
isNewPlayer = False
isListPlayer = False

bot = commands.Bot(command_prefix=prefix, intents=intents)
@bot.event
async def on_ready():

    print(f"We have logged in as {bot.user}. Invite link: https://discord.com/api/oauth2/authorize?client_id=1089791970886557696&permissions=8&scope=bot")

@bot.command()
async def hello(message):
    if message.author == bot.user:
        return
    await message.send("Привет, " + message.author.name)

@bot.command()
async def giveRole(ctx, *,roleName):
    print(roleName)
    guild = ctx.guild
    user = ctx.message.author
    role = discord.utils.get(guild.roles, name=roleName)
    if role:
        await user.add_roles(role)
    else:
        await guild.create_role(name=roleName)
        await user.add_roles(user, role)

@bot.command()
async def newGame(ctx, title, *, args):
    embed = disnake.Embed(
        title=title,
        description=args,
        color=disnake.Colour.dark_green()
    )

    accept = Button(label="Принять участие", style=discord.ButtonStyle.secondary, emoji="✅")
    cancel = Button(label="Подписаться", style=discord.ButtonStyle.secondary, emoji="❌")
    view = View()
    view.add_item(accept)
    view.add_item(cancel)
    await ctx.send(embed=embed, view=view)


@bot.command()
async def новыйКанал(ctx, channelName):

    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="Лобби")

    embed = disnake.Embed(
        title="Успех!",
        description=f"Канал {channelName} был успешно создан",
        color=disnake.Colour.dark_green(),
    )

    await guild.create_text_channel(name=channelName, category=category)
    await ctx.send(embed=embed)

@bot.command()
async def новыйИгрок(ctx, *, message):
    # do something with DB
    print("1")


bot.run(os.getenv("TOKEN"))


