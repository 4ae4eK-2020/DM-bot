from datetime import datetime
import discord
import disnake
from dotenv import load_dotenv
from model import *
import os

load_dotenv()

prefix = '+'

bot = discord.Bot()


@bot.event
async def on_ready():
    print(
        f"We have logged in as {bot.user}. Invite link: https://discord.com/api/oauth2/authorize?client_id"
        f"=1089791970886557696&permissions=8&scope=bot")


@bot.slash_command(description='say hello to you sweetly)')
async def hello(message):
    if message.author == bot.user:
        return
    await message.respond("Привет, " + message.author.name)


with db:
    tables = [Place, Event, User]
    if not all(table.table_exists() for table in tables):
        db.create_tables(tables)


    @bot.command(name="give_role", description='give role to you (if you has permission)')
    async def giveRole(ctx, role_name: str, author="`"):
        print(role_name)
        guild = ctx.guild

        if author == "`":
            user = ctx.author
        else:
            user = author
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await user.add_roles(role)
        else:
            await guild.create_role(name=role_name)
            await user.add_roles(user, role)
        if type(ctx) == discord.interactions.Interaction:
            await ctx.response.send_message(f'Роль {role_name} была успешно выдана')
        else:
            await ctx.respond(f'Роль {role_name} была успешно выдана')


    @bot.command(name="new_game", description='DM only; create event message')
    async def newGame(ctx, *, title: str, description: str, min_players_count: int, max_players_count: int, place: str,
                      date_time: str):

        title = title
        description = description
        min_players_count = min_players_count
        max_players_count = max_players_count
        place = place
        date_time = date_time

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
        embed.set_author(name=ctx.author)

        new_event = Event.insert(name=title, description=description, min_count=min_players_count,
                                 max_count=max_players_count, place=Place.select().where(Place.name == "НТИ"),
                                 date_time=date_time, poster_url="_", discord_role_id=role.id)
        new_event.execute()
        await ctx.respond(embed=embed, view=GameEmbedView())


class GameEmbedView(discord.ui.View):
    @discord.ui.button(label="Принять участие", style=discord.ButtonStyle.secondary, emoji="✅")
    async def participate_callback(self, newGame, interaction):
        embed = interaction.message.embeds[0]
        await giveRole(interaction, embed.title, interaction.user)

    @discord.ui.button(label="Подписаться на новости", style=discord.ButtonStyle.secondary, emoji="🔔")
    async def subscribe_callback(self, newGame, interacrion):
        await giveRole(interacrion, "новости", interacrion.user)

    @bot.command(name="new_channel", description='moderators only; create new channel in category')
    async def new_channel(self, channel_name: str, category_name: str):
        guild = self.guild

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        embed = disnake.Embed(
            title="Успех!",
            description=f"Канал {channel_name} был успешно создан",
            color=disnake.Colour.dark_green(),
        )

        await guild.create_text_channel(name=channel_name, category=category)
        await self.respond(embed=embed)


bot.run(os.getenv("TOKEN"))
