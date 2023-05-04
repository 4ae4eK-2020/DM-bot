from datetime import datetime
import discord
from discord.ext import commands
from discord.ui import Button, View
import disnake
from dotenv import load_dotenv
from model import *
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
    print(
        f"We have logged in as {bot.user}. Invite link: https://discord.com/api/oauth2/authorize?client_id"
        f"=1089791970886557696&permissions=8&scope=bot")


@bot.command()
async def hello(message):
    if message.author == bot.user:
        return
    await message.send("Привет, " + message.author.name)


with db:
    tables = [Place, Event, User]
    if not all(table.table_exists() for table in tables):
        db.create_tables(tables)


    @bot.command()
    async def giveRole(ctx, *, roleName):
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
    async def newGame(ctx, *, args):

        args_arr = args.split('; ')
        title = args_arr[0]
        description = args_arr[1]
        min_players_count = args_arr[2]
        max_players_count = args_arr[3]
        place = args_arr[4]
        date_time = args_arr[5]

        role = discord.utils.get(ctx.guild.roles, name=title)
        if not role:
            role = await ctx.guild.create_role(name=title)

        embed = disnake.Embed(
            title=title,
            description=description,
            timestamp=datetime.strptime(date_time + " 00:00:00", '%d.%m.%y %H:%M:%S'),
            color=disnake.Colour.dark_green()
        )

        embed.add_field("На сколько игроков рассчитано", f"от {min_players_count} до {max_players_count}")
        embed.add_field("Где будет проходить", place)

        accept = Button(label="Принять участие", style=discord.ButtonStyle.secondary, emoji="✅",
                        custom_id="participate")
        cancel = Button(label="Подписаться", style=discord.ButtonStyle.secondary, emoji="🔔", custom_id="subscription")
        view = View()
        view.add_item(accept)
        view.add_item(cancel)

        new_event = Event.insert(name=title, description=description, min_count=min_players_count,
                                 max_count=max_players_count, place=Place.select().where(Place.name == "НТИ"),
                                 date_time=date_time, poster_url="_", discord_role_id=role.id)
        new_event.execute()
        await ctx.send(embed=embed, view=view)

        async def participate_callback(interaction):
            await giveRole(ctx, roleName=title)

        accept.callback = participate_callback(disnake.MessageInteraction)


    @bot.command()
    async def newChannel(ctx, channelName, categoryName):
        guild = ctx.guild

        category = discord.utils.get(guild.categories, name=categoryName)
        if not category:
            category = await guild.create_category(categoryName)

        embed = disnake.Embed(
            title="Успех!",
            description=f"Канал {channelName} был успешно создан",
            color=disnake.Colour.dark_green(),
        )

        await guild.create_text_channel(name=channelName, category=category)
        await ctx.send(embed=embed)

bot.run(os.getenv("TOKEN"))
