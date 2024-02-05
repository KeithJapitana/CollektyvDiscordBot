import discord
import os
import asyncio
import json
import random
import datetime
import re
import smtplib
# import youtube_dl
# from youtube_search import YoutubeSearch
from keep_alive import keep_alive
from discord.ext import commands

# help_command = commands.DefaultHelpCommand(
#     no_category = 'Commands'
# )

# defaultPrefix = '/'

# intents = discord.Intents().all()
# bot = commands.Bot(command_prefix=defaultPrefix, description="Sample Bot", help_command=help_command, intents=intents)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)

quest = {}


def load_user_data():
  if not os.path.exists("user_data.json") or os.stat(
      "user_data.json").st_size == 0:
    return {}
  try:
    with open("user_data.json", "r") as file:
      data = json.load(file)
  except json.JSONDecodeError:
    return {}

  return data


def save_user_data(user_data):
  try:
    with open('user_data.json', 'r') as file:
      existing_data = json.load(file)
  except FileNotFoundError:
    existing_data = {}

  for user_id, data in user_data.items():
    if user_id in existing_data:
      existing_data[user_id].update(data)
    else:
      existing_data[user_id] = data

  with open('user_data.json', 'w') as file:
    json.dump(existing_data, file, indent=4)


user_data = load_user_data()


@bot.event
async def on_ready():
  await bot.change_presence(status=discord.Status.online,
                            activity=discord.Game('/help <command>'))
  print(f'Logged in as {bot.user.name}')
  try:
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} command(s)')
  except Exception as e:
    print(e)


@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingRole):
    embed = discord.Embed(
      title="You don't have the permission to create/delete quest")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.colour = discord.Colour.red()
    await ctx.reply(embed=embed)
    await ctx.message.delete()
    await ctx.defer()


def calculate_level(exp):
  level_thresholds = [
    0, 20000, 40000, 80000, 160000, 200000, 300000, 400000, 500000, 600000,
    700000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000
  ]
  level = 0

  for threshold in level_thresholds:
    if exp >= threshold:
      level += 1
    else:
      break

  return level


def update_exp_and_level(user_data, exp, level):
  user_data["exp"] = exp
  user_data["level"] = level
  save_user_data(user_data)


async def assign_roles(user, level):
  guild = user.guild

  level_roles = {
    1: 1094130863190593586,
    2: 1094131120494346290,
    3: 1094131201285042221,
    4: 1094131245014863943,
    5: 1094131409242832999,
    6: 1094131478809554974,
    7: 1094131523785084969,
    8: 1094131571168120872,
    9: 1094131695927689247,
    10: 1094131759110688818,
    11: 1094131802190397520,
    12: 1094131973255090186,
    13: 1094132040305217606,
    14: 1094132102401896448,
    15: 1094132149101273129,
    16: 1094132262645272626,
    17: 1094132301228683295,
    18: 1094132349647720589,
  }

  if level in level_roles:
    role_id = level_roles[level]
    role = guild.get_role(role_id)

    if role is not None:

      for user_role in user.roles:
        if user_role.id in level_roles.values():
          try:
            await user.remove_roles(user_role)
          except discord.Forbidden:
            print(
              f"Failed to remove role '{user_role.name}' from user '{user.name}'"
            )
          else:
            print(f"Removed role '{user_role.name}' from user '{user.name}'")
      try:
        await user.add_roles(role)
      except discord.Forbidden:
        print(f"Failed to assign role '{role.name}' to user '{user.name}'")
      else:
        print(f"Assigned role '{role.name}' to user '{user.name}'")
    else:
      print(f"Role with ID '{role_id}' not found")
  else:
    print(f"No role assigned for level {level}")

def get_level_up_role(level):
  role_thresholds = {
    1: 1094130863190593586,
    2: 1094131120494346290,
    3: 1094131201285042221,
    4: 1094131245014863943,
    5: 1094131409242832999,
    6: 1094131478809554974,
    7: 1094131523785084969,
    8: 1094131571168120872,
    9: 1094131695927689247,
    10: 1094131759110688818,
    11: 1094131802190397520,
    12: 1094131973255090186,
    13: 1094132040305217606,
    14: 1094132102401896448,
    15: 1094132149101273129,
    16: 1094132262645272626,
    17: 1094132301228683295,
    18: 1094132349647720589,
  }

  return role_thresholds.get(level)

def get_level_down_role(level):
  role_thresholds = {
    1: 1094130863190593586,
    2: 1094131120494346290,
    3: 1094131201285042221,
    4: 1094131245014863943,
    5: 1094131409242832999,
    6: 1094131478809554974,
    7: 1094131523785084969,
    8: 1094131571168120872,
    9: 1094131695927689247,
    10: 1094131759110688818,
    11: 1094131802190397520,
    12: 1094131973255090186,
    13: 1094132040305217606,
    14: 1094132102401896448,
    15: 1094132149101273129,
    16: 1094132262645272626,
    17: 1094132301228683295,
    18: 1094132349647720589,
  }

  return role_thresholds.get(level)

def get_role_ids(level):
  role_thresholds = {
    1: 1094130863190593586,
    2: 1094131120494346290,
    3: 1094131201285042221,
    4: 1094131245014863943,
    5: 1094131409242832999,
    6: 1094131478809554974,
    7: 1094131523785084969,
    8: 1094131571168120872,
    9: 1094131695927689247,
    10: 1094131759110688818,
    11: 1094131802190397520,
    12: 1094131973255090186,
    13: 1094132040305217606,
    14: 1094132102401896448,
    15: 1094132149101273129,
    16: 1094132262645272626,
    17: 1094132301228683295,
    18: 1094132349647720589,
  }

  role_ids = []
  for i in range(2, level + 1):
    role_id = role_thresholds.get(i)
    if role_id:
      role_ids.append(role_id)
  return role_ids

def get_level_role(level):
  if level == 1:
    return 1094130863190593586
  elif level == 2:
    return 1094131120494346290
  elif level == 3:
    return 1094131201285042221
  elif level == 4:
    return 1094131245014863943
  elif level == 5:
    return 1094131409242832999
  elif level == 6:
    return 1094131478809554974
  elif level == 7:
    return 1094131523785084969
  elif level == 8:
    return 1094131571168120872
  elif level == 9:
    return 1094131695927689247
  elif level == 10:
    return 1094131759110688818
  elif level == 11:
    return 1094131802190397520
  elif level == 12:
    return 1094131973255090186
  elif level == 13:
    return 1094132040305217606
  elif level == 14:
    return 1094132102401896448
  elif level == 15:
    return 1094132149101273129
  elif level == 16:
    return 1094132262645272626
  elif level == 17:
    return 1094132301228683295
  else:
    return 1094132349647720589

  return None

@bot.hybrid_command(description="Check user's experience")
async def check_exp(ctx, member: discord.Member = None):
  if member is None:
      member = ctx.author

  user_id = str(member.id)
  user_data = load_user_data()

  if user_id in user_data:
      exp = user_data[user_id].get("exp", 0)
      level = user_data[user_id].get("level", 0)
      level_thresholds = [
          0, 20000, 40000, 80000, 160000, 200000, 300000, 400000, 500000, 600000,
          700000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000
      ]
      next_level_exp = level_thresholds[level] if level < len(level_thresholds) else None
      percentage = ((exp - level_thresholds[level - 1]) / (next_level_exp - level_thresholds[level - 1])) * 100 if next_level_exp else 100

      embed = discord.Embed(title="User Experience & Level", color=discord.Color.green())
      embed.set_author(name=member.name, icon_url=member.avatar.url)
      embed.add_field(name='Experience', value=f'{exp}/{next_level_exp}', inline=False)
      embed.add_field(name='Level', value=level, inline=False)

      if next_level_exp:
          progress_bar_length = int(percentage / 10)
          progress_bar = ''.join(['█' for _ in range(progress_bar_length)])
          empty_bar = ''.join(['░' for _ in range(10 - progress_bar_length)])
          embed.add_field(name='Level Progress', value=f'{progress_bar}{empty_bar} {percentage:.2f}%', inline=True)

      await ctx.reply(embed=embed)
  else:
      embed = discord.Embed(title=f'{member.display_name} has not gained any exp yet.', color=discord.Color.red())
      await ctx.reply(embed=embed)

@bot.hybrid_command(description="Add coins to User")
#@commands.has_role('MODERATOR')
@commands.has_permissions(administrator=True)
async def add_coins(ctx, user: discord.Member, amount: float):
  if amount <= 0:
    embed = discord.Embed(
      title="Invalid amount. Please provide a positive number.",
      color=discord.Color.red())
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    await ctx.reply(embed=embed)
    await ctx.message.delete()
    await ctx.defer()
    return

  if str(user.id) in user_data:
    user_data[str(user.id)]['coins'] += amount
  else:
    user_data[str(user.id)] = {'coins': amount}

  save_user_data(user_data)

  embed = discord.Embed(title=f"Added {amount} coins to {user.display_name}.",
                        color=discord.Color.green())
  embed.set_author(name=user.name, icon_url=user.avatar.url)
  await ctx.reply(embed=embed)
  await ctx.message.delete()
  await ctx.defer()

class Menu(discord.ui.View):
  stored_quests = []

  def __init__(self, embed, bot):
    super().__init__()
    self.embed = embed
    self.bot = bot
    self.channel_id = None
    self.author = None
    self.title = None
    self.description = None
    self.footer = None
    self.fields = []
    self.price = None
    self.deadline = None
    self.allowed_member = None
    self.color = None

  @discord.ui.button(label="Edit Author", style=discord.ButtonStyle.blurple)
  async def edit_author(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
    embed = discord.Embed(title="Edit Author",
                          description="Please enter the new author",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_author(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      author_message = await self.bot.wait_for('message',
                                               check=check_author,
                                               timeout=60)
      new_author = author_message.content

      self.embed.set_author(name=new_author)
      self.author = new_author

      await author_message.delete()
      await interaction.message.edit(embed=self.embed)
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Edit Title", style=discord.ButtonStyle.blurple)
  async def edit_title(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
    embed = discord.Embed(title="Edit Title",
                          description="Please enter the new title",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_title(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      title_message = await self.bot.wait_for('message',
                                              check=check_title,
                                              timeout=60)
      new_title = title_message.content

      self.embed.title = new_title
      self.title = new_title

      await title_message.delete()
      await interaction.message.edit(embed=self.embed)
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Edit Description",
                     style=discord.ButtonStyle.blurple)
  async def edit_description(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
    embed = discord.Embed(title="Edit Description",
                          description="Please enter the new description",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_description(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      description_message = await self.bot.wait_for('message',
                                                    check=check_description,
                                                    timeout=60)
      new_description = description_message.content

      self.embed.description = new_description
      self.description = new_description

      await description_message.delete()
      await interaction.message.edit(embed=self.embed)
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Edit Footer", style=discord.ButtonStyle.blurple)
  async def edit_footer(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
    embed = discord.Embed(title="Edit Footer",
                          description="Please enter the new footer",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_footer(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      footer_message = await self.bot.wait_for('message',
                                               check=check_footer,
                                               timeout=60)
      new_footer = footer_message.content

      self.embed.set_footer(text=new_footer)
      self.footer = new_footer

      await footer_message.delete()
      await interaction.message.edit(embed=self.embed)
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Add Field", style=discord.ButtonStyle.blurple)
  async def add_field(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    embed = discord.Embed(
      title="Add Field",
      description="Please enter the title of the new field",
      color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_field_title(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      title_message = await self.bot.wait_for('message',
                                              check=check_field_title,
                                              timeout=60)
      field_title = title_message.content

      embed = discord.Embed(
        title="Field Description",
        description="Please enter the description of the new field",
        color=discord.Color.blurple())
      await title_message.delete()
      await interaction.followup.send(embed=embed, ephemeral=True)

      def check_field_description(m):
        return m.author.id == interaction.user.id and m.channel == interaction.channel

      description_message = await self.bot.wait_for(
        'message', check=check_field_description, timeout=60)
      field_description = description_message.content

      self.embed.add_field(name=field_title,
                           value=field_description,
                           inline=False)
      self.fields.append((field_title, field_description))
      await description_message.delete()
      await interaction.message.edit(embed=self.embed)
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Edit Price", style=discord.ButtonStyle.blurple)
  async def edit_price(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
    embed = discord.Embed(
      title="Edit Price",
      description="Please enter the new price (integer/float value only)",
      color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_price(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      price_message = await self.bot.wait_for('message',
                                              check=check_price,
                                              timeout=60)
      try:
        new_price = float(price_message.content)
      except ValueError:
        embed = discord.Embed(
          title="Invalid Price Format",
          description="Please enter a integer/float value for the price.",
          color=discord.Color.red())
        await price_message.delete()
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

      formatted_price = f"${new_price}"

      price_field_index = None
      for index, field in enumerate(self.embed.fields):
        if field.name == "Price":
          price_field_index = index
          break

      if price_field_index is not None:
        self.embed.set_field_at(price_field_index,
                                name="Price",
                                value=formatted_price)
      else:
        self.embed.add_field(name="Price", value=formatted_price, inline=False)

      embed = discord.Embed(
        title="Price Updated",
        description=f"The new price is set to: {formatted_price}",
        color=discord.Color.green())
      await price_message.delete()
      await interaction.message.edit(embed=self.embed)

      self.price = new_price
    except asyncio.TimeoutError:
      embed = discord.Embed(title="Timeout",
                            description="Timeout. Please try again.",
                            color=discord.Color.red())
      await interaction.followup.send(embed=embed, ephemeral=True)

  @discord.ui.button(label="Edit Deadline", style=discord.ButtonStyle.blurple)
  async def edit_deadline(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
    embed = discord.Embed(
      title="Edit Deadline",
      description="Please enter the new deadline in the format: Month DD, YYYY",
      color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_deadline(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      deadline_message = await self.bot.wait_for('message',
                                                 check=check_deadline,
                                                 timeout=60)
      deadline_input = deadline_message.content

      try:
        deadline = datetime.datetime.strptime(deadline_input, "%B %d, %Y")
      except ValueError:
        embed = discord.Embed(
          title="Invalid Deadline Format",
          description="Please try again with the format: Month DD, YYYY",
          color=discord.Color.red())
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

      current_time = datetime.datetime.now()
      time_difference = deadline - current_time

      if time_difference.total_seconds() <= 0:
        embed = discord.Embed(
          title="Invalid Deadline",
          description="The deadline should be a future date. Please try again.",
          color=discord.Color.red())

        await interaction.followup.send(embed=embed, ephemeral=True)
        return

      new_deadline = deadline.strftime("%B %d, %Y")

      for field in self.embed.fields:
        if field.name == "Deadline":
          field.value = new_deadline
          break
      else:
        self.embed.add_field(name="Deadline", value=new_deadline)

      embed = discord.Embed(
        title="Deadline Updated",
        description=f"The new deadline is set to: {new_deadline}",
        color=discord.Color.green())
      await deadline_message.delete()
      await interaction.message.edit(embed=self.embed)

      self.deadline = deadline
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Edit Allowed Member",
                     style=discord.ButtonStyle.blurple)
  async def edit_allowed_member(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
    embed = discord.Embed(title="Edit Allowed Member",
                          description="Please enter the new allowed member",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_allowed_member(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      member_message = await self.bot.wait_for('message',
                                               check=check_allowed_member,
                                               timeout=60)
      new_allowed_member = member_message.content

      allowed_member_field_index = None
      for index, field in enumerate(self.embed.fields):
        if field.name == "Allowed Member":
          allowed_member_field_index = index
          break

      if allowed_member_field_index is not None:
        allowed_member_field = self.embed.fields[allowed_member_field_index]
        self.embed.set_field_at(
          allowed_member_field_index,
          name=allowed_member_field.name,
          value=f"{allowed_member_field.value}\n**{new_allowed_member}**",
          inline=False)
      else:
        self.embed.add_field(name=f"**{new_allowed_member}**",
                             value="",
                             inline=False)

      await member_message.delete()
      await interaction.message.edit(embed=self.embed)

      self.allowed_member = new_allowed_member
    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @staticmethod
  def store_quest_data(quest_data):
    Menu.stored_quests.append(quest_data)

  @discord.ui.button(label="Select Color", style=discord.ButtonStyle.blurple)
  async def select_color(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
    color_options = [
      (discord.Color.blurple(), "Blurple"),
      (discord.Color.green(), "Green"),
      (discord.Color.gold(), "Gold"),
      (discord.Color.red(), "Red"),
    ]

    options_text = "\n".join([
      f"{i}. {color_name}"
      for i, (_, color_name) in enumerate(color_options, start=1)
    ])
    options_text += "\n\nEnter 'custom' to choose a custom color."

    embed = discord.Embed(title="Select Color",
                          description=options_text,
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_color(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      color_message = await self.bot.wait_for('message',
                                              check=check_color,
                                              timeout=60)
      selected_input = color_message.content.lower()

      if selected_input == "custom":
        await interaction.followup.send(
          "Please enter a custom color as a hexadecimal value (e.g., #FF0000).",
          ephemeral=True)

        custom_color_message = await self.bot.wait_for('message',
                                                       check=check_color,
                                                       timeout=60)
        custom_color_input = custom_color_message.content

        try:
          color = discord.Color(int(custom_color_input.strip("#"), 16))
          await custom_color_message.delete()
        except ValueError:
          await interaction.followup.send("Invalid color. Please try again.",
                                          ephemeral=True)
          return

      else:
        selected_number = int(selected_input)

        if 1 <= selected_number <= len(color_options):
          color = color_options[selected_number - 1][0]
        else:
          await interaction.followup.send(
            "Invalid selection. Please try again.", ephemeral=True)
          return

      self.embed.color = color

      await color_message.delete()
      await interaction.message.edit(embed=self.embed)

    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.",
                                      ephemeral=True)

  @discord.ui.button(label="Save Quest", style=discord.ButtonStyle.blurple)
  async def save_quest(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
    self.embed.timestamp = datetime.datetime.utcnow()

    Menu.stored_quests.append({
      "author": self.author,
      "title": self.title,
      "description": self.description,
      "footer": self.footer,
      "fields": self.fields,
      "price": self.price,
      "deadline": self.deadline,
      "allowed_member": self.allowed_member,
      "color": self.color
    })

    await interaction.response.send_message("Quest saved!", ephemeral=True)

  @discord.ui.button(label="Edit Quest", style=discord.ButtonStyle.green)
  async def edit_quest(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
    embed = discord.Embed(title="Edit Quest",
                          description="Please enter the quest ID:",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_quest_id(m):
      return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
      quest_id_message = await self.bot.wait_for('message',
                                                 check=check_quest_id,
                                                 timeout=60)
      quest_id = quest_id_message.content.strip()

      with open('quest_data.json', 'r') as file:
        stored_quests = json.load(file)

      quest_index = None
      for index, stored_quest in enumerate(stored_quests):
        if stored_quest["quest_id"] == int(quest_id):
          quest_index = index
          break

      if quest_index is None:
        embed = discord.Embed(title="Quest Not Found",
                              description="No quest with that ID was found.",
                              color=discord.Color.red())
        await quest_id_message.delete()
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

      quest = stored_quests[quest_index]

      embed = interaction.message.embeds[0]
      quest["title"] = embed.title
      quest["description"] = embed.description
      quest["author"] = embed.author.name
      quest["footer"] = embed.footer.text if embed.footer else None
      quest["price"] = self.price
      quest["deadline"] = self.deadline.strftime("%B %d, %Y")
      quest["fields"] = []
      for field in embed.fields:
        if field.name not in ["Price", "Deadline"]:
          quest["fields"].append([field.name, field.value])

      with open('quest_data.json', 'w') as file:
        json.dump(stored_quests, file, indent=4)

      await quest_id_message.delete()

      updated_embed = discord.Embed(
        title="Edit Quest",
        description="The quest data has been edited successfully.",
        color=discord.Color.green())

      await interaction.followup.send(embed=updated_embed)
      await interaction.message.delete()

      channel = interaction.channel
      async for message in channel.history():
        if message.author == self.bot.user and len(message.embeds) > 0:
          message_embed = message.embeds[0]
          if re.search(r"\bQuest ID: {}\b".format(quest_id),
                       str(message_embed.title)):
            message_embed.title = updated_embed.title
            message_embed.description = updated_embed.description
            message_embed.set_author(name=updated_embed.author.name)
            message_embed.set_footer(
              text=updated_embed.footer.text if updated_embed.footer else None)
            message_embed.clear_fields()
            for field in updated_embed.fields:
              message_embed.add_field(name=field.name,
                                      value=field.value,
                                      inline=field.inline)
            message_embed.color = updated_embed.color
            await message.edit(embed=message_embed)

    except asyncio.TimeoutError:
      await interaction.followup.send("Timeout. Please try again.")

  @discord.ui.button(label="Send", style=discord.ButtonStyle.green)
  async def send_embed(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
    guild = interaction.guild

    channel_list = [channel for channel in guild.text_channels]

    options = "\n".join([
      f"{index + 1}. {channel.name}"
      for index, channel in enumerate(channel_list)
    ])

    embed = discord.Embed(
      title="Send Quest",
      description="Please select a channel by typing its corresponding number:",
      color=discord.Color.blurple())
    embed.add_field(name="Channel Options", value=options)

    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check(message):
      return message.author == interaction.user and message.channel == interaction.channel

    try:
      response = await self.bot.wait_for('message', check=check, timeout=60)

      if not response.content:
        embed = discord.Embed(
          title="No Channel Selected",
          description="You did not select a channel. Please try again.",
          color=discord.Color.red())
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

      channel_index = int(response.content) - 1

      if channel_index < 0 or channel_index >= len(channel_list):
        embed = discord.Embed(
          title="Invalid Channel Selection",
          description="Please select a valid channel number.",
          color=discord.Color.red())
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

      selected_channel = channel_list[channel_index]

      embed = discord.Embed(title="Quest Created",
                            description="Quest has been created successfully.",
                            color=discord.Color.green())
      await response.delete()
      await selected_channel.send(embed=self.embed)
      sent_message = await interaction.followup.send(embed=embed)
      await interaction.followup.send(embed=self.embed)
      await interaction.message.delete()

      quest_data = {
        "quest_id": random.randint(1000, 9999),
        "title": self.title,
        "description": self.description,
        "author": self.author,
        "footer": self.footer,
        "fields": self.fields,
        "price": self.price,
        "deadline": self.deadline.strftime("%B %d, %Y"),
        "allowed_member": self.allowed_member,
        "color": self.embed.color.value if self.embed.color else 3447003
      }

      with open('quest_data.json', 'r+') as file:
        file_content = file.read()
        if file_content.strip() == "":
          stored_quests = []
        else:
          try:
            stored_quests = json.loads(file_content)
          except json.JSONDecodeError:
            stored_quests = []

        stored_quests.append(quest_data)

        file.seek(0)
        json.dump(stored_quests, file, indent=4)
        file.truncate()

      quest_id_embed = discord.Embed(
        title="Quest ID",
        description=f"The quest ID is: {quest_data['quest_id']}",
        color=discord.Color.blue())
      await selected_channel.send(embed=quest_id_embed)
      await sent_message.edit(embed=quest_id_embed)

    except asyncio.TimeoutError:
      embed = discord.Embed(title="Timeout",
                            description="Timeout. Please try again.",
                            color=discord.Color.red())
      await interaction.followup.send(embed=embed)

  @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
  async def cancel(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
    embed = discord.Embed(title="Edit Cancelled", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await interaction.message.delete()
    self.clear_items()
    self.stop()


@bot.hybrid_command(description="Accept Quest")
async def accept(ctx, quest_id):
  if not quest_id.isdigit():
    embed = discord.Embed(title="Invalid Quest ID",
                          description="Quest ID must be a valid integer.",
                          color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  with open("quest_data.json", "r") as file:
    stored_quests = json.load(file)

  quest = None
  for stored_quest in stored_quests:
    if stored_quest["quest_id"] == int(quest_id):
      quest = stored_quest
      break

  if not quest:
    embed = discord.Embed(title="Quest Not Found",
                          description="No quest with that ID was found.",
                          color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  deadline = datetime.datetime.strptime(quest["deadline"], "%B %d, %Y")
  current_time = datetime.datetime.now()

  if deadline < current_time:
    embed = discord.Embed(
      title="Quest Expired",
      description="This quest has already expired and cannot be accepted.",
      color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  user_id = str(ctx.author.id)
  price = quest["price"]
  exp = price * 100
  coins = price

  if os.path.exists(
      "user_data.json") and os.stat("user_data.json").st_size != 0:
    with open("user_data.json", "r") as file:
      data = json.load(file)
  else:
    data = {}

  if user_id in data:
    user_exp = data[user_id].get("exp", 0) + exp
    user_level = calculate_level(user_exp)

    if user_level > data[user_id].get("level", 0):
      level_up_role = data[user_id].get("level_up_role")
      if level_up_role is not None:
        await assign_roles(ctx.author, user_level)

    stored_quests.remove(quest)
    update_exp_and_level(data[user_id], user_exp, user_level)
  else:
    user_exp = exp
    user_level = calculate_level(user_exp)

    if user_level > 0:
      await assign_roles(ctx.author, user_level)

    stored_quests.remove(quest)
    data[user_id] = {"exp": user_exp, "level": user_level}

  data[user_id]["coins"] = data[user_id].get("coins", 0) + coins

  with open("user_data.json", "w") as file:
    json.dump(data, file, indent=4)

  with open("quest_data.json", "w") as file:
    json.dump(stored_quests, file, indent=4)

  await assign_roles(ctx.author, user_level)

  accepted_quest = {
    "quest_id": quest["quest_id"],
    "title": quest["title"],
    "deadline": quest["deadline"],
    "price": quest["price"],
    "accepted_by": ctx.author.name
  }

  if os.path.exists(
      "accepted_quest.json") and os.stat("accepted_quest.json").st_size != 0:
    with open("accepted_quest.json", "r") as file:
      accepted_quest_data = json.load(file)
  else:
    accepted_quest_data = []

  accepted_quest_data.append(accepted_quest)

  with open("accepted_quest.json", "w") as file:
    json.dump(accepted_quest_data, file, indent=4)

  embed = discord.Embed(
    title="Quest Accepted",
    description=
    f"{ctx.author.mention} accepted '{quest['title']}' and gained {coins} coins and {exp} experience and is now level {user_level}.",
    color=discord.Color.green())
  await ctx.send(embed=embed)


@bot.hybrid_command(description="Show User's Accepted Quest")
async def accepted_quest(ctx):
  user_id = ctx.author.name

  if not os.path.exists("accepted_quest.json") or os.path.getsize(
      "accepted_quest.json") == 0:
    with open("accepted_quest.json", "w") as file:
      json.dump([], file)

  with open("accepted_quest.json", "r") as file:
    accepted_q = json.load(file)

  accepted_quest = [
    accepted for accepted in accepted_q
    if accepted.get("accepted_by") == user_id
  ]

  if not accepted_quest:
    embed = discord.Embed(title="No Accepted Quest",
                          description="You have not accepted a quest yet.",
                          color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(
    title="Accepted Quest",
    description="Here is the list of the past quests you have accepted:",
    color=discord.Color.blurple())

  for accepted in accepted_quest:
    embed.add_field(
      name=f"Quest ID: {accepted['quest_id']}",
      value=
      f"Title: {accepted['title']}\nDeadline: {accepted['deadline']}\nPrice: ${accepted['price']}",
      inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show All Accepted Quest")
@commands.has_permissions(administrator=True)
async def accepted(ctx):
  if not os.path.exists("accepted_quest.json") or os.path.getsize(
      "accepted_quest.json") == 0:
    with open("accepted_quest.json", "w") as file:
      json.dump([], file)

  with open("accepted_quest.json", "r") as file:
    accepted_q = json.load(file)

  accepted_quest = [accepted for accepted in accepted_q]

  if not accepted_quest:
    embed = discord.Embed(title="No Accepted Quest",
                          description="No quest accepted yet.",
                          color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(
    title="Accepted Quest",
    description="Here is the list of past quests that have been accepted:",
    color=discord.Color.blurple())

  for accepted in accepted_quest:
    embed.add_field(
      name=f"Quest ID: {accepted['quest_id']}",
      value=
      f"Title: {accepted['title']}\nDeadline: {accepted['deadline']}\nPrice: ${accepted['price']}\nAccepted By: {accepted['accepted_by']}",
      inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show all available Quest")
async def available_quest(ctx):
  with open('quest_data.json', 'r') as file:
    quest_data = json.load(file)

  available_quests = []
  current_time = datetime.datetime.now()

  for quest in quest_data:
    deadline = datetime.datetime.strptime(quest["deadline"], "%B %d, %Y")
    if deadline >= current_time:
      available_quests.append(quest)

  if not available_quests:
    embed = discord.Embed(
      title="No Available Quests",
      description="There are no available quests at the moment.",
      color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(title="Available Quests",
                        description="Here are the available quests:",
                        color=discord.Color.blurple())

  for quest in available_quests:
    embed.add_field(name=f"Title: {quest['title']}",
                    value=f"ID: {quest['quest_id']}",
                    inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Search Quest")
async def search_quest(ctx, quest_id):
  with open('quest_data.json', 'r') as file:
    stored_quests = json.load(file)

  quest = None
  for stored_quest in stored_quests:
    if stored_quest["quest_id"] == int(quest_id):
      quest = stored_quest
      break

  if quest is None:
    embed = discord.Embed(title="Quest Not Found",
                          description="No quest with that ID was found.",
                          color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(title=quest["title"],
                        description=quest["description"],
                        color=discord.Color(quest["color"])
                        if quest["color"] else discord.Color.blue())
  embed.set_author(name=quest["author"])
  embed.set_footer(text=quest["footer"])

  for field in quest["fields"]:
    embed.add_field(name=field[0], value=field[1], inline=False)

  embed.add_field(name="Price", value=f"${quest['price']}", inline=False)
  embed.add_field(name="Deadline", value=quest["deadline"], inline=False)

  allowed_member = quest.get("allowed_member")
  if allowed_member:
    embed.add_field(name="", value=f"**{allowed_member}**", inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Delete Quest")
#@commands.has_role('MODERATOR')
@commands.has_permissions(administrator=True)
async def delete_quest(ctx, quest_id):
  with open('quest_data.json', 'r+') as file:
    stored_quests = json.load(file)

    quest_index = None
    for index, quest in enumerate(stored_quests):
      if quest["quest_id"] == int(quest_id):
        quest_index = index
        break

    if quest_index is None:
      embed = discord.Embed(title="Quest Not Found",
                            description="No quest with that ID was found.",
                            color=discord.Color.red())
      await ctx.send(embed=embed)
      return

    deleted_quest = stored_quests.pop(quest_index)

    file.seek(0)
    json.dump(stored_quests, file, indent=4)
    file.truncate()

  channel_list = [channel for channel in ctx.guild.text_channels]
  options = "\n".join([
    f"{index + 1}. {channel.name}"
    for index, channel in enumerate(channel_list)
  ])

  embed = discord.Embed(
    title="Delete Quest",
    description="Please select a channel to send the updated embed:",
    color=discord.Color.blurple())
  embed.add_field(name="Channel Options", value=options)

  await ctx.send(embed=embed, ephemeral=True)

  def check_channel_selection(m):
    return m.author == ctx.author and m.channel == ctx.channel

  try:
    response = await ctx.bot.wait_for('message',
                                      check=check_channel_selection,
                                      timeout=60)

    if not response.content:
      embed = discord.Embed(
        title="No Channel Selected",
        description="You did not select a channel. The embed will not be sent.",
        color=discord.Color.red())
      await ctx.send(embed=embed, ephemeral=True)
      return

    channel_index = int(response.content) - 1

    if channel_index < 0 or channel_index >= len(channel_list):
      embed = discord.Embed(
        title="Invalid Channel Selection",
        description="Please select a valid channel number.",
        color=discord.Color.red())
      await ctx.send(embed=embed, ephemeral=True)
      return

    selected_channel = channel_list[channel_index]

    embed = discord.Embed(
      title="Quest Deleted",
      description=
      f"The quest '{deleted_quest['title']}' (Quest ID: {deleted_quest['quest_id']}) has been deleted.",
      color=discord.Color.red())
    await response.delete()
    await ctx.send(embed=embed)
    await selected_channel.send(embed=embed)

  except asyncio.TimeoutError:
    await ctx.send("Timeout. Please try again.")


@bot.hybrid_command(description="Send Coins to Other User")
@commands.has_permissions(administrator=True)
async def send_coins(ctx, member: discord.Member, amount: int):
  author_id = str(ctx.author.id)
  recipient_id = str(member.id)

  with open('user_data.json', 'r') as file:
    user_data = json.load(file)

  if author_id not in user_data:
    user_data[author_id] = {'coins': 0}
  if recipient_id not in user_data:
    user_data[recipient_id] = {'coins': 0}

  author_coins = user_data[author_id]['coins']

  if author_coins < amount:
    embed = discord.Embed(title="Insufficient Coins",
                          description="You do not have enough coins to send.",
                          color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  recipient_coins = user_data[recipient_id]['coins']

  author_coins -= amount
  recipient_coins += amount

  user_data[author_id]['coins'] = author_coins
  user_data[recipient_id]['coins'] = recipient_coins

  with open('user_data.json', 'w') as file:
    json.dump(user_data, file, indent=4)

  embed = discord.Embed(
    title="Coins Sent",
    description=f"You have sent {amount} coins to {member.mention}.",
    color=discord.Color.green())
  embed.add_field(name=f"{ctx.author.name} new balance: ", value=author_coins)
  await ctx.send(embed=embed)


@bot.hybrid_command(description="Deduct coins from User")
#@commands.has_role('MODERATOR')
@commands.has_permissions(administrator=True)
async def deduct_coins(ctx, member: discord.Member, amount: float):
  author_id = str(ctx.author.id)
  recipient_id = str(member.id)

  with open('user_data.json', 'r') as file:
    user_data = json.load(file)

  if author_id not in user_data:
    user_data[author_id] = {'coins': 0}
  if recipient_id not in user_data:
    user_data[recipient_id] = {'coins': 0}

  if user_data[recipient_id]['coins'] < amount:
    embed = discord.Embed(
      title="Insufficient Coins",
      description=
      f"{member.display_name} does not have enough coins to deduct.",
      color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  user_data[recipient_id]['coins'] -= amount

  with open('user_data.json', 'w') as file:
    json.dump(user_data, file, indent=4)

  embed = discord.Embed(
    title="Coins Deducted",
    description=f"{amount} coins have been deducted from {member.mention}.",
    color=discord.Color.green())
  embed.add_field(name="User's new balance: ",
                  value=user_data[recipient_id]['coins'])
  await ctx.send(embed=embed)


@bot.hybrid_command(description="Show user's coins")
async def show_balance(ctx, member: discord.Member = None):
  user_id = str(member.id) if member else str(ctx.author.id)

  with open('user_data.json', 'r') as file:
    user_data = json.load(file)

  coins = user_data.get(user_id, {}).get('coins', 0)

  embed = discord.Embed(
    title="Coins Balance",
    description=
    f"Balance of {member.mention if member else ctx.author.mention}: {coins}",
    color=discord.Color.blue())
  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Add Experience")
@commands.has_permissions(administrator=True)
async def add_exp(ctx, member: discord.Member, amount: float):
  with open('user_data.json', 'r') as file:
    user_data = json.load(file)

  if str(member.id) not in user_data:
    user_data[str(member.id)] = {'exp': 0, 'level': 1}

  previous_level = user_data[str(member.id)]['level']
  user_data[str(member.id)]['exp'] += amount
  user_data[str(member.id)]['level'] = calculate_level(user_data[str(member.id)]['exp'])
  current_level = user_data[str(member.id)]['level']

  if current_level > previous_level:
    for level in range(1, previous_level + 1):
      level_role_id = get_level_role(level)
      if level_role_id:
        level_role = ctx.guild.get_role(level_role_id)
        if level_role:
          await member.remove_roles(level_role)

    level_up_role_id = get_level_role(current_level)
    if level_up_role_id:
      level_up_role = ctx.guild.get_role(level_up_role_id)
      if level_up_role:
        await member.add_roles(level_up_role)

  with open('user_data.json', 'w') as file:
    json.dump(user_data, file, indent=4)

  embed = discord.Embed(
    title="Experience Points Added",
    description=f"Added {amount} exp to {member.name}.",
    color=discord.Color.blurple())

  await ctx.send(embed=embed)

@bot.hybrid_command(description="Deduct Experience")
@commands.has_permissions(administrator=True)
async def deduct_exp(ctx, member: discord.Member, amount: float):
  with open('user_data.json', 'r') as file:
      user_data = json.load(file)

  if str(member.id) not in user_data:
      user_data[str(member.id)] = {'exp': 0, 'level': 1}

  previous_level = user_data[str(member.id)]['level']
  user_data[str(member.id)]['exp'] -= amount
  user_data[str(member.id)]['level'] = calculate_level(user_data[str(member.id)]['exp'])
  current_level = user_data[str(member.id)]['level']

  if current_level < previous_level:
      level_up_role_id = get_level_up_role(current_level)
      if level_up_role_id:
          level_up_role = ctx.guild.get_role(level_up_role_id)
          if level_up_role:
              await member.add_roles(level_up_role)

      for level in range(previous_level, current_level, -1):
          level_down_role_id = get_level_down_role(level)
          if level_down_role_id:
              level_down_role = ctx.guild.get_role(level_down_role_id)
              if level_down_role:
                  await member.remove_roles(level_down_role)

  with open('user_data.json', 'w') as file:
      json.dump(user_data, file, indent=4)

  embed = discord.Embed(
      title="Experience Points Deducted",
      description=f"Deducted {amount} exp from {member.name}.",
      color=discord.Color.blurple())

  await ctx.send(embed=embed)

# @bot.hybrid_command(description="Remove All Threshold Roles for a User")
# @commands.has_permissions(administrator=True)
# async def reset_role(ctx, member: discord.Member):
#   user_roles = member.roles
#   for threshold in level_thresholds:
#     role_id = get_level_up_role(threshold)
#     if role_id:
#       role = discord.utils.get(user_roles, id=role_id)
#       if role:
#         await member.remove_roles(role)
        
#   embed = discord.Embed(
#     title="Roles Remove",
#     description=f"All threshold roles have been removed for {member.name}.",
#     color=discord.Color.blurple())

#   await ctx.send(embed=embed)
  
@bot.hybrid_command(description="Create Quest")
#@commands.has_role('MODERATOR')
@commands.has_permissions(administrator=True)
async def quest(ctx):
  embed = discord.Embed(title="Sample Title",
                        description="Sample Description",
                        color=discord.Color.blue())
  embed.set_author(name="Sample Author")
  embed.set_footer(text="Sample Footer")

  view = Menu(embed, ctx.bot)
  await ctx.send(embed=embed, view=view)


bot.remove_command('help')


@bot.hybrid_command(description="Collektyv Commands")
async def help(ctx, command_name: str = None):
  if command_name == 'accept':
    embed = discord.Embed(title="Accept Command Help",
                          description="Accepts a quest and provides rewards.",
                          color=discord.Color.blue())

    embed.add_field(name="/accept [quest_id]",
                    value="Accepts the quest with the specified ID.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425014462349463/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425059102347294/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'add_coins':
    embed = discord.Embed(title="Add Coins Command Help",
                          description="Adds coins to user's account.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/add_coins [user][amount]",
      value="Adds the specified amount of coins to the user's balance.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425233526665216/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425267630547026/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'add_exp':
    embed = discord.Embed(title="Add Experience Command Help",
                          description="Adds experience points to a user.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/add_exp [user][amount]",
      value="Adds the specified amount of experience points to the user.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425429555859486/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425473247907921/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'available_quest':
    embed = discord.Embed(title="Available Quests Command Help",
                          description="Displays the available quests.",
                          color=discord.Color.blue())

    embed.add_field(name="/available_quest",
                    value="Shows the list of all available quests.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425855109926942/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121425894943236216/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'check_exp':
    embed = discord.Embed(
      title="Check Experience Command Help",
      description="Checks a user's experience points and level.",
      color=discord.Color.blue())

    embed.add_field(
      name="/check_exp [user]",
      value=
      "Checks the experience and level of the specified user. If no user is provided, checks the author's experience and level."
    )
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121426044784750714/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121459056612216923/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121426745258680330/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121426796123009024/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'deduct_coins':
    embed = discord.Embed(title="Deduct Coins Command Help",
                          description="Deducts coins from a user's balance.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/deduct_coins [amount]",
      value="Deducts the specified amount of coins from the user's balance.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121426949949104248/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121426988863848531/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'deduct_exp':
    embed = discord.Embed(title="Deduct Experience Command Help",
                          description="Deducts experience points from a user.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/deduct_exp [user][amount]",
      value="Deducts the specified amount of experience points from the user.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121427093327183993/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121427297526878288/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'delete_quest':
    embed = discord.Embed(
      title="Delete Quest Command Help",
      description="Deletes a quest from the available quests.",
      color=discord.Color.blue())

    embed.add_field(name="/delete_quest [quest_id]",
                    value="Deletes the quest with the specified Quest ID.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121427415844012163/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121427656966148106/image.png?width=428&height=701"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121429008672882781/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'expired_quest':
    embed = discord.Embed(title="Expired Quest Command Help",
                          description="Show all expired quest.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/expired_quest",
      value=
      "It will display all expired quests that the user has not yet accepted.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121427842534752306/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121427878559625246/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'quest':
    embed = discord.Embed(title="Quest Command Help",
                          description="Allows admin to create a quest.",
                          color=discord.Color.blue())

    embed.add_field(name="/quest",
                    value="Create quest that can be accept by a user.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121429087169282078/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121429295101907025/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121447595743658165/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121447677364813834/image.png?width=487&height=701"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121447757362778112/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(description="Before", color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121456833991819334/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121457551104557189/image.png?width=675&height=701"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121457569366548510/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(description="After", color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121457696915337396/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'search_quest':
    embed = discord.Embed(title="Search Quest Command Help",
                          description="Searches for quests based on Quest ID.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/search_quest [quest_id]",
      value="Searches for quests that match the provided Quest ID.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121447882432716920/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121447914993094706/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'send_coins':
    embed = discord.Embed(title="Send Coins Command Help",
                          description="Sends coins to another user.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/send_coins [user][amount]",
      value="Sends the specified amount of coins to the specified user.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121450443248250971/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121450482276245554/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'show_balance':
    embed = discord.Embed(title="Show Balance Command Help",
                          description="Shows the balance of a user.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/show_balance [user]",
      value=
      "Shows the coin balance of the specified user. If no user is provided, shows the author's coin balance."
    )
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121450716691705936/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121450906328780862/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121450980354039859/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451007382138960/image.png"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'formatting_help':
    embed = discord.Embed(title="Show Text Format Command Help",
                          description="Shows Discord Text Format.",
                          color=discord.Color.blue())

    embed.add_field(name="/formatting_help",
                    value="Show all the available format for Discord Text.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1120947499759312956/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451221992087582/image.png?width=384&height=701"
    )
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'ticket':
    embed = discord.Embed(title="Show Ticket Command Help",
                          description="Create ticketing system.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/ticket",
      value=
      "It will create ticket-channel that allows user-admin private conversation."
    )
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'send_email':
    embed = discord.Embed(title="Show Send Email Command Help",
                          description="Admin can email messages to users.",
                          color=discord.Color.blue())

    embed.add_field(
      name="/send_email [recipient_email][subject][message]",
      value="It will allow admin to send email messages to users.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'request_salary':
    embed = discord.Embed(
      title="Show Request Salary Command Help",
      description="It allows users to send request salary via email.",
      color=discord.Color.blue())

    embed.add_field(
      name="/request_salary [amount]",
      value=
      "It allows users to email the administrator to request a wage, and the administrator will respond."
    )
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'search_salary':
    embed = discord.Embed(
      title="Show Search Salary Command Help",
      description="Searches Salary Transaction Records by Salary ID.",
      color=discord.Color.blue())

    embed.add_field(name="/search_salary [salary_id]",
                    value="It display salary transaction by Salary ID.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'pending_transactions':
    embed = discord.Embed(
      title="Show Pending Transaction (Admin) Command Help",
      description="Display all Pending Transactions.",
      color=discord.Color.blue())

    embed.add_field(name="/pending_transactions",
                    value="It display all pending transactions.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'confirmed_transactions':
    embed = discord.Embed(
      title="Show Confirmed Transaction (Admin) Command Help",
      description="Display all Confirmed Transactions.",
      color=discord.Color.blue())

    embed.add_field(name="/confirmed_transactions",
                    value="It display all Confirmed Transactions")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'pending':
    embed = discord.Embed(
      title="Show Pending (User) Command Help",
      description="Display the user's Pending Transactions.",
      color=discord.Color.blue())

    embed.add_field(name="/pending",
                    value="It display the user's Pending Transactions")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'confirmed':
    embed = discord.Embed(
      title="Show Confirmed (User) Command Help",
      description="Display the user's Confirmed Transactions.",
      color=discord.Color.blue())

    embed.add_field(name="/confirmed",
                    value="It display the user's Confirmed Transactions")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'confirm_salary':
    embed = discord.Embed(title="Show Text Format Command Help",
                          description="Allow admin to Confirm the Request.",
                          color=discord.Color.blue())

    embed.add_field(name="/confirm_salary",
                    value="It allows the admin to confirm the transaction.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'set_email':
    embed = discord.Embed(title="Show Set Email Command Help",
                          description="Allow user to set their email address.",
                          color=discord.Color.blue())

    embed.add_field(name="/set_email",
                    value="It will set the user's email address.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'email':
    embed = discord.Embed(title="Show Email Command Help",
                          description="Display the user's email address.",
                          color=discord.Color.blue())

    embed.add_field(name="/email",
                    value="It display the user's email address.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  elif command_name == 'show_emails':
    embed = discord.Embed(title="Display Show Email Command Help",
                          description="Shows all email address.",
                          color=discord.Color.blue())

    embed.add_field(name="/show_emails",
                    value="It display all the email addresses.")
    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121101730520772638/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451328816824340/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451397850861728/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_image(
      url=
      "https://media.discordapp.net/attachments/1045702456325197854/1121451475378372628/image.png"
    )

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()
  else:
    embed = discord.Embed(title="Show Command Help",
                          description="List of available commands:",
                          color=discord.Color.blue())

    embed.add_field(name="/accept",
                    value="Accepts a quest and provides rewards.")
    embed.add_field(name="/add_coins", value="Adds coins to a user's balance.")
    embed.add_field(name="/add_exp", value="Adds experience points to a user.")
    embed.add_field(name="/available_quest",
                    value="Displays the available quests.")
    embed.add_field(name="/check_exp",
                    value="Checks a user's experience points and level.")
    embed.add_field(name="/deduct_coins",
                    value="Deducts coins from a user's balance.")
    embed.add_field(name="/deduct_exp",
                    value="Deducts experience points from a user.")
    embed.add_field(name="/delete_quest",
                    value="Deletes a quest from the available quests.")
    embed.add_field(
      name="/expired_quest",
      value=
      "It will display all expired quests that the user has not yet accepted.")
    embed.add_field(name="/quest",
                    value="Make a quest that another user can accept.")
    embed.add_field(name="/search_quest",
                    value="Searches for quests based on keywords.")
    embed.add_field(name="/send_coins", value="Sends coins to another user.")
    embed.add_field(name="/show_balance",
                    value="Shows the user's coin balance.")
    embed.add_field(
      name="/formatting_help",
      value="Display every Discord Text format that is available.")
    embed.add_field(
      name="/ticket",
      value=
      "It will create a private ticket channel for admin and user communication."
    )
    embed.add_field(name="/send_email",
                    value="Admin can email messages to users.")
    embed.add_field(
      name="/request_salary",
      value=
      "It allows users to email the administrator to request a wage, and the administrator will respond."
    )
    embed.add_field(name="/search_salary",
                    value="Searches Salary Transaction Records")
    embed.add_field(name="/pending_transactions",
                    value="Display all Pending Transactions")
    embed.add_field(name="/confirmed_transactions",
                    value="Display all Confirmed Transactions")
    embed.add_field(name="/pending",
                    value="Display the user's Pending Transactions")
    embed.add_field(name="/confirmed",
                    value="Display the user's Confirmed Transactions")
    embed.add_field(name="/confirm_salary",
                    value="It allows the admin to confirm the transaction.")
    embed.add_field(name="/set_email",
                    value="It will set the user's email address.")
    embed.add_field(name="/email", value="Display the user's email address.")
    embed.add_field(name="/show_emails",
                    value="Display all the email addresses.")

    await ctx.send(embed=embed, ephemeral=True)
    await ctx.delete()


@bot.hybrid_command(description="Discord Text Format")
async def formatting_help(ctx):
  embed = discord.Embed(
    title="Discord Text Formatting",
    description=
    "This is an example of various Discord text formatting options.",
    color=discord.Color.blue())

  embed.add_field(name="**Bold\*\*", value="**Bold Text**", inline=False)
  embed.add_field(name="***Bold Italic\*\*\*",
                  value="***Bold Italic Text***",
                  inline=False)
  embed.add_field(name="**__Bold & Underlined\_\_\*\*",
                  value="**__Bold and Underlined Text__**",
                  inline=False)
  embed.add_field(name="**~~Bold & Strikethrough\~\~\*\*",
                  value="**~~Bold and Strike through Text~~**",
                  inline=False)
  embed.add_field(
    name="***~~__Bold, Italicized, Strikethrough & Underlined\_\_\~\~\*\*\*",
    value="***~~__Bold, Italicized, Strikethrough and Underlined Text__~~***",
    inline=False)
  embed.add_field(name="_Italic\_", value="_Italic Text_", inline=False)
  embed.add_field(name="__Underline\_\_",
                  value="__Underlined Text__",
                  inline=False)
  embed.add_field(name="~~Strikethrough\~\~",
                  value="~~Strikethrough Text~~",
                  inline=False)
  embed.add_field(name="\`\Code\`", value="`Code Snippet`", inline=False)
  embed.add_field(name="\`\`\`Code Block\`\`\`",
                  value="```Python\nprint('Hello, world!')\n```",
                  inline=False)
  embed.add_field(name=">\Quoting", value="> Quoted Text", inline=False)
  embed.add_field(name="||Spoiler\|\|",
                  value="||Spoiler Text||<-Click Here",
                  inline=False)
  embed.add_field(name="\`\`\`Box\`\`\`",
                  value="``` Box Text ```",
                  inline=False)
  embed.add_field(name="\`\`\`Multiple Line\nLine 1\nLine 2\`\`\`",
                  value="```Multiple Line Text\nLine 1\nLine 2 ```",
                  inline=False)
  embed.add_field(name="[Twitter]\(https://twitter.com/DAGI_2152)",
                  value="[Twitter](https://twitter.com/DAGI_2152)",
                  inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Ticket System")
#@commands.has_role('MODERATOR')
@commands.has_permissions(administrator=True)
async def ticket(ctx):
  embed = discord.Embed(
    title="Ticket Tool",
    description="Click the button below to create a ticket.",
    color=discord.Color.blue())

  message = await ctx.send(embed=embed)
  await message.add_reaction("🎫")


TICKET_CATEGORY_ID = os.environ['TICKET_CATEGORY_ID']

@bot.event
async def on_reaction_add(reaction, user):
  if user.bot:
    return

  if reaction.emoji == "🎫":
    ticket_category_id = int(TICKET_CATEGORY_ID)
    ticket_category = bot.get_channel(ticket_category_id)

    if ticket_category is None:
      print(f"Ticket category with ID '{ticket_category_id}' not found.")
      return

    existing_ticket = discord.utils.get(ticket_category.guild.text_channels,
                                        topic=f"User ID: {user.id}")
    if existing_ticket:
      await user.send("You already have an existing ticket.")
      return

    ticket_channel = await ticket_category.create_text_channel(
      name=f"ticket-{user.name}",
      topic=f"User ID: {user.id}",
      reason="Ticket created.")

    embed = discord.Embed(title="Ticket Created",
                          description=f"Ticket created by {user.mention}!",
                          color=discord.Color.green())
    embed.set_footer(text="React to this message to close the ticket.")

    ticket_message = await ticket_channel.send(embed=embed)
    await ticket_message.add_reaction("❌")

    await ticket_channel.set_permissions(user,
                                         read_messages=True,
                                         send_messages=True)
    await ticket_channel.set_permissions(ticket_category.guild.default_role,
                                         read_messages=False)

    await user.send(
      f"Ticket created! Your ticket channel is {ticket_channel.mention}.")

  elif reaction.emoji == "❌":
    ticket_channel = reaction.message.channel
    ticket_category = ticket_channel.category

    if ticket_category and ticket_category.name == "ticket-category":
      if ticket_channel.topic == f"User ID: {user.id}" or any(
          role.name == "MODERATOR" for role in user.roles):
        transcript = ""
        async for message in ticket_channel.history(limit=None):
          transcript += f"**{message.author.display_name}**:\n{message.content}\n\n"

        transcript_embed = discord.Embed(title="Ticket Transcript",
                                         description=transcript,
                                         color=discord.Color.blue())

        try:
          await user.send("Ticket closed. Here is the transcript:",
                          embed=transcript_embed)
        except discord.Forbidden:
          print(f"Failed to send the transcript to {user.name}")

        await ticket_channel.set_permissions(user,
                                             read_messages=False,
                                             send_messages=False,
                                             reason="Ticket closed.")

        if any(role.name == "MODERATOR" for role in user.roles):
          await reaction.message.add_reaction("🔓")
          await reaction.message.add_reaction("🔙")

  elif reaction.emoji == "🔓" or reaction.emoji == "🔙":
    ticket_channel = reaction.message.channel
    ticket_category = ticket_channel.category

    if ticket_category and ticket_category.name == "ticket-category":
      if any(role.name == "MODERATOR" for role in user.roles):
        user_id = int(ticket_channel.topic.split("User ID: ")[1])
        member = bot.get_user(user_id)
        if member:
          await ticket_channel.set_permissions(member,
                                               read_messages=True,
                                               send_messages=True)
          transcript_url = f"[Transcript]({ticket_channel.mention})"
          await member.send(
            f"Your ticket has been reopened. You can now access the channel again: {transcript_url}"
          )
          await ticket_message.add_reaction("❌")
          await reaction.remove(user)

    if not user.bot:
      await reaction.message.remove_reaction("🔓", user)
      await reaction.message.remove_reaction("🔙", user)
      await reaction.message.remove_reaction("❌", user)


@bot.hybrid_command(description="Show all expired Quest")
async def expired_quest(ctx):
  current_time = datetime.datetime.now()
  expired_quests = []

  with open('quest_data.json', 'r') as file:
    all_quests = json.load(file)

  for quest in all_quests:
    deadline = datetime.datetime.strptime(quest['deadline'], "%B %d, %Y")
    if deadline < current_time:
      expired_quests.append(quest)

  if not expired_quests:
    embed = discord.Embed(
      title="No Expired Quests",
      description="There are no expired quests at the moment.",
      color=discord.Color.orange())
    await ctx.send(embed=embed)
    return

  embed = discord.Embed(title="Expired Quests",
                        description="Here are the expired quests:",
                        color=discord.Color.blurple())

  for quest in expired_quests:
    embed.add_field(name=f"Title: {quest['title']}",
                    value=f"ID: {quest['quest_id']}",
                    inline=False)

  await ctx.send(embed=embed)


EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
ADMIN = os.environ['ADMIN']


@bot.hybrid_command(description="Send Email to Users")
@commands.has_permissions(administrator=True)
async def send_email(ctx, recipient_email: str, subject: str, message: str):
  try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
      server.starttls()
      server.login(EMAIL, PASSWORD)

      email_message = f"Subject: {subject}\n\n{message}"

      server.sendmail(EMAIL, recipient_email, email_message)

    embed = discord.Embed(
      title=f"Email sent successfully to: {recipient_email}")
    await ctx.send(embed=embed, ephemeral=True)
  except Exception as e:
    embed = discord.Embed(
      title=f"An error occurred while sending the email: {str(e)}")
    await ctx.send(embed=embed, ephemeral=True)

@bot.hybrid_command(description="Request Salary to Admin")
async def request_salary(ctx, coins: float):
  admin_id = int(ADMIN)
  admin = bot.get_user(admin_id)

  if admin is None:
      embed = discord.Embed(
          title="Admin Not Found",
          description="The admin user could not be found.",
          color=discord.Color.red()
      )
      await ctx.send(embed=embed, ephemeral=True)
      return

  with open("user_data.json", "r") as file:
      user_data = json.load(file)

  if str(ctx.author.id) not in user_data:
      embed = discord.Embed(
          title="User Not Found",
          description="You are not registered in the system.",
          color=discord.Color.red()
      )
      await ctx.send(embed=embed, ephemeral=True)
      return

  if user_data[str(ctx.author.id)].get("coins", 0) < coins:
      embed = discord.Embed(
          title="Insufficient Coins",
          description="You do not have enough coins to request this salary.",
          color=discord.Color.red()
      )
      await ctx.send(embed=embed, ephemeral=True)
      return

  user_data[str(ctx.author.id)]["coins"] -= coins

  admin_id_str = str(admin_id)
  if admin_id_str not in user_data:
    user_data[admin_id_str] = {"coins": coins}
  else:
    user_data[admin_id_str]["coins"] += coins

  with open("user_data.json", "w") as file:
    json.dump(user_data, file, indent=4)

  payment_modes = ["Gcash", "Paymaya", "Paypal", "Bank to Bank"]
  payment_mode_options = "\n".join(
    [f"{index}. {mode}" for index, mode in enumerate(payment_modes, start=1)])

  payment_mode_embed = discord.Embed(
    title="Payment Mode Selection",
    description=
    "Please select your preferred payment mode by entering the corresponding number.\n\n"
    + payment_mode_options,
    color=discord.Color.blue())
  payment_mode_message = await ctx.send(embed=payment_mode_embed,
                                        ephemeral=True)

  try:
    payment_mode_response = await bot.wait_for(
      "message",
      timeout=60,
      check=lambda message: message.author == ctx.author and message.channel ==
      ctx.channel)
    selected_payment_mode_index = int(payment_mode_response.content)
    selected_payment_mode = payment_modes[selected_payment_mode_index - 1]
    await payment_mode_response.delete()
  except (ValueError, IndexError, asyncio.TimeoutError):
    embed = discord.Embed(
      title="Invalid Payment Mode",
      description="Invalid payment mode selection. Please try again.",
      color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
    await payment_mode_response.delete()
    return

  salary_id = random.randint(1000, 9999)

  embed = discord.Embed(title="Salary Request", color=discord.Color.blue())
  embed.add_field(name="User",
                  value=f"{ctx.author.name} ({ctx.author.id})",
                  inline=False)
  embed.add_field(name="Amount", value=f"${coins}", inline=False)
  embed.add_field(name="Status", value="Pending", inline=False)
  embed.add_field(name="Salary ID", value=salary_id, inline=False)
  embed.add_field(name="Payment Mode",
                  value=selected_payment_mode,
                  inline=False)

  await admin.send(embed=embed)

  recipient_email = EMAIL
  subject = "Salary Request"
  message = f"Salary Request Details:\n\nSalary ID: {salary_id}\nUser ID: {ctx.author.id}\nUsername: {ctx.author.name}\nAmount: ${coins}\nStatus: Pending\nPayment Mode: {selected_payment_mode}"

  await send_email(ctx, recipient_email, subject, message)

  salary_request = {
    "salary_id": salary_id,
    "user_id": ctx.author.id,
    "username": ctx.author.name,
    "coins": coins,
    "status": "Pending",
    "payment_mode": selected_payment_mode
  }

  if os.path.exists("salary.json") and os.stat("salary.json").st_size != 0:
    with open("salary.json", "r") as file:
      salary_data = json.load(file)
  else:
    salary_data = []

  salary_data.append(salary_request)

  with open("salary.json", "w") as file:
    json.dump(salary_data, file, indent=4)

  confirmation_embed = discord.Embed(title="Salary Request Confirmation",
                                     color=discord.Color.green())
  confirmation_embed.add_field(name="Amount", value=f"${coins}", inline=False)
  confirmation_embed.add_field(name="Status", value="Pending", inline=False)
  confirmation_embed.add_field(name="Salary ID", value=salary_id, inline=False)
  confirmation_embed.add_field(name="Payment Mode",
                               value=selected_payment_mode,
                               inline=False)
  confirmation_embed.set_footer(
    text="Your request has been sent to the admin.")

  await ctx.send(embed=confirmation_embed, ephemeral=True)


@bot.hybrid_command(description="Search Salary Transaction")
async def search_salary(ctx, salary_id: int):
  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  found_salaries = [
    salary for salary in salary_data if salary.get("salary_id") == salary_id
  ]

  if not found_salaries:
    embed = discord.Embed(
      title="Salary Not Found",
      description=f"No salary with ID {salary_id} was found.",
      color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(title="Salary Details",
                        description=f"Salary details for ID {salary_id}:",
                        color=discord.Color.blue())

  for salary in found_salaries:
    embed.add_field(name="User ID", value=salary.get("user_id"), inline=False)
    embed.add_field(name="Username",
                    value=salary.get("username"),
                    inline=False)
    embed.add_field(name="Amount",
                    value=f"${salary.get('coins')}",
                    inline=False)
    embed.add_field(name="Status", value=salary.get("status"), inline=False)
    embed.add_field(name="Mode of Payment",
                    value=salary.get("payment_mode"),
                    inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show All Transactions")
@commands.has_permissions(administrator=True)
async def transactions(ctx):
  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  all_transactions = [transaction for transaction in salary_data]

  if not all_transactions:
    embed = discord.Embed(
      title="No Transactions",
      description="There are no salary transactions at the moment.",
      color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(title="Transactions",
                        description="Here are the salary transactions:",
                        color=discord.Color.blurple())

  for transaction in all_transactions:
    embed.add_field(
      name=f"Salary ID: {transaction['salary_id']}",
      value=
      f"Username: {transaction['username']}\nAmount: ${transaction['coins']}\nMode of Payment: {transaction['payment_mode']}",
      inline=False)

  await ctx.send(embed=embed, ephemeral=True)


def load_salary_transactions():
  with open("salary.json", "r") as file:
    return json.load(file)


def save_salary_transactions(salary_transactions):
  with open("salary.json", "w") as file:
    json.dump(salary_transactions, file, indent=4)


@bot.hybrid_command(description="Delete a specified transaction.")
@commands.has_permissions(administrator=True)
async def delete_salary(ctx, salary_id):
  try:
    salary_id = int(salary_id)
    if salary_id <= 0:
      raise ValueError
  except ValueError:
    embed = discord.Embed(title="Invalid Salary ID",
                          description="Salary ID must be a positive integer.",
                          color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
    return

  salary_transactions = load_salary_transactions()

  deleted_transaction = None
  for transaction in salary_transactions:
    if transaction["salary_id"] == salary_id:
      deleted_transaction = transaction
      salary_transactions.remove(transaction)
      break

  if deleted_transaction is None:
    embed = discord.Embed(
      title="Salary Transaction Not Found",
      description="No salary transaction with that ID was found.",
      color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
  else:
    save_salary_transactions(salary_transactions)

    embed = discord.Embed(
      title="Salary Transaction Deleted",
      description=
      f"The salary transaction with ID {deleted_transaction['salary_id']} has been deleted.",
      color=discord.Color.green())
    await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show All Pending Transactions")
@commands.has_permissions(administrator=True)
async def pending_transactions(ctx):
  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  pending_transactions = [
    transaction for transaction in salary_data
    if transaction.get("status") == "Pending"
  ]

  if not pending_transactions:
    embed = discord.Embed(
      title="No Pending Transactions",
      description="There are no pending salary transactions at the moment.",
      color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(
    title="Pending Transactions",
    description="Here are the pending salary transactions:",
    color=discord.Color.blurple())

  for transaction in pending_transactions:
    embed.add_field(
      name=f"Salary ID: {transaction['salary_id']}",
      value=
      f"Username: {transaction['username']}\nAmount: ${transaction['coins']}\nMode of Payment: {transaction['payment_mode']}",
      inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show All Confirmed Transactions")
@commands.has_permissions(administrator=True)
async def confirmed_transactions(ctx):
  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  confirmed_transactions = [
    transaction for transaction in salary_data
    if transaction.get("status") == "Confirmed"
  ]

  if not confirmed_transactions:
    embed = discord.Embed(
      title="No Confirmed Transactions",
      description="There are no confirmed salary transactions at the moment.",
      color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(
    title="Confirmed Transactions",
    description="Here are the confirmed salary transactions:",
    color=discord.Color.blurple())

  for transaction in confirmed_transactions:
    embed.add_field(
      name=f"Salary ID: {transaction['salary_id']}",
      value=
      f"Username: {transaction['username']}\nAmount: ${transaction['coins']}\nMode of Payment: {transaction['payment_mode']}",
      inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show User's Pending Transactions")
async def pending(ctx):
  user_id = ctx.author.id

  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  pending_transactions = [
    transaction for transaction in salary_data
    if transaction.get("user_id") == user_id
    and transaction.get("status") == "Pending"
  ]

  if not pending_transactions:
    embed = discord.Embed(
      title="No Pending Transactions",
      description="You have no pending salary transactions.",
      color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(
    title="Pending Transactions",
    description="Here are your pending salary transactions:",
    color=discord.Color.blurple())

  for transaction in pending_transactions:
    embed.add_field(name=f"Salary ID: {transaction['salary_id']}",
                    value=f"Amount: ${transaction['coins']}",
                    inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show User's Confirmed Transactions")
async def confirmed(ctx):
  user_id = ctx.author.id

  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  pending_transactions = [
    transaction for transaction in salary_data
    if transaction.get("user_id") == user_id
    and transaction.get("status") == "Confirmed"
  ]

  if not pending_transactions:
    embed = discord.Embed(
      title="No Confirmed Transactions",
      description="You have no confirmed salary transactions.",
      color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(
    title="Confirmed Transactions",
    description="Here are your confirmed salary transactions:",
    color=discord.Color.blurple())

  for transaction in pending_transactions:
    embed.add_field(name=f"Salary ID: {transaction['salary_id']}",
                    value=f"Amount: ${transaction['coins']}",
                    inline=False)

  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Set Status for Salary")
@commands.has_permissions(administrator=True)
async def confirm_salary(ctx, salary_id: int, member: discord.Member):
  with open("salary.json", "r") as file:
    salary_data = json.load(file)

  for transaction in salary_data:
    if transaction.get("salary_id") == salary_id:
      transaction["status"] = "Confirmed"
      user_id = transaction.get("user_id")
      coins = transaction.get("coins")
      break
  else:
    embed = discord.Embed(
      title="Salary Request Not Found",
      description=f"The salary request with ID {salary_id} was not found.",
      color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
    return

  with open("salary.json", "w") as file:
    json.dump(salary_data, file, indent=4)

  with open("email.json", "r") as file:
    email_data = json.load(file)

  user_email = email_data.get(str(user_id), {}).get("email")
  if not user_email:
    embed = discord.Embed(
      title="Email Not Found",
      description=
      f"The email address for the user {member.name} was not found. The salary request will not be confirmed.",
      color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)
    return

  recipient_email = user_email
  subject = "Salary Request Confirmation"
  message = f"Dear {member.name},\n\nYour salary request with ID {salary_id} has been confirmed. The requested amount of ${coins} will be credited to your account.\n\nThank you for your patience and understanding.\n\nBest regards,\nCollekytv"

  await send_email(ctx, recipient_email, subject, message)

  embed = discord.Embed(
    title="Salary Request Confirmed",
    description=
    f"The salary request with ID {salary_id} has been confirmed and an email has been sent to the user.",
    color=discord.Color.green())
  await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Set User's Email Address")
async def set_email(ctx, email: str):
  user_id = str(ctx.author.id)

  if os.path.exists("email.json") and os.stat("email.json").st_size != 0:
    with open("email.json", "r") as file:
      email_data = json.load(file)
  else:
    email_data = {}

  if user_id in email_data:
    email_data[user_id]["email"] = email
    message = "Your email address has been updated successfully."
  else:
    email_data[user_id] = {"email": email}
    message = "Your email address has been saved successfully."

  with open("email.json", "w") as file:
    json.dump(email_data, file, indent=4)

  success_embed = discord.Embed(title="Email Saved",
                                description=message,
                                color=discord.Color.green())
  success_embed.set_author(name=ctx.author.name,
                           icon_url=ctx.author.avatar.url)
  success_embed.add_field(name="User ID", value=user_id, inline=False)
  success_embed.add_field(name="Email", value=email, inline=False)
  await ctx.reply(embed=success_embed, ephemeral=True)
  await ctx.message.delete()
  await ctx.defer()


@bot.hybrid_command(description="Show User's Email Address")
async def email(ctx):
  user_id = str(ctx.author.id)

  if os.path.exists("email.json") and os.stat("email.json").st_size != 0:
    with open("email.json", "r") as file:
      email_data = json.load(file)
  else:
    email_data = {}

  if user_id in email_data:
    email = email_data[user_id]["email"]

    embed = discord.Embed(title="Email Address",
                          description=f"\n{email}",
                          color=discord.Color.blurple())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="User ID", value=user_id, inline=False)
    await ctx.send(embed=embed, ephemeral=True)
  else:
    embed = discord.Embed(title="Email Address",
                          description="You have not set an email address.",
                          color=discord.Color.orange())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="User ID", value=user_id, inline=False)
    await ctx.send(embed=embed, ephemeral=True)


@bot.hybrid_command(description="Show All Email Addresses")
@commands.has_permissions(administrator=True)
async def show_emails(ctx):
  if os.path.exists("email.json") and os.stat("email.json").st_size != 0:
    with open("email.json", "r") as file:
      email_data = json.load(file)
  else:
    email_data = {}

  if not email_data:
    embed = discord.Embed(title="No Email Addresses Found",
                          description="There are no email addresses.",
                          color=discord.Color.orange())
    await ctx.send(embed=embed, ephemeral=True)
    return

  embed = discord.Embed(title="Email Addresses",
                        description="Here are the email addresses:",
                        color=discord.Color.blurple())

  for user_id, data in email_data.items():
    user = bot.get_user(int(user_id))
    if user:
      email = data["email"]
      embed.add_field(name=f"User: {user.name}",
                      value=f"Email: {email}",
                      inline=False)

  await ctx.send(embed=embed, ephemeral=True)


level_thresholds = [
  0, 20000, 40000, 80000, 160000, 200000, 300000, 400000, 500000, 600000,
  700000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000
]

roles_thresholds = {
  1: 1094130863190593586,
  2: 1094131120494346290,
  3: 1094131201285042221,
  4: 1094131245014863943,
  5: 1094131409242832999,
  6: 1094131478809554974,
  7: 1094131523785084969,
  8: 1094131571168120872,
  9: 1094131695927689247,
  10: 1094131759110688818,
  11: 1094131802190397520,
  12: 1094131973255090186,
  13: 1094132040305217606,
  14: 1094132102401896448,
  15: 1094132149101273129,
  16: 1094132262645272626,
  17: 1094132301228683295,
  18: 1094132349647720589,
}


@bot.hybrid_command(description="Show Level")
@commands.has_permissions(administrator=True)
async def view_thresholds(ctx):
    level_thresholds_string = "\n".join(f"Level {i}: {threshold}" for i, threshold in enumerate(level_thresholds, start=1))
    roles_thresholds_string = ""

    for level, role_id in roles_thresholds.items():
        if level == 1:
            role_name = "Newbie"
        elif level == 2:
            role_name = "Novice Adventurer"
        elif level == 3:
            role_name = "D Rank Adventurer"
        elif level == 4:
            role_name = "D+ Rank Adventurer"
        elif level == 5:
            role_name = "D++ Rank Adventurer"
        elif level == 6:
            role_name = "C Rank Adventurer"
        elif level == 7:
            role_name = "C+ Rank Adventurer"
        elif level == 8:
            role_name = "C++ Rank Adventurer"
        elif level == 9:
            role_name = "B Rank Adventurer"
        elif level == 10:
            role_name = "B+ Rank Adventurer"
        elif level == 11:
            role_name = "B++ Rank Adventurer"
        elif level == 12:
            role_name = "A Rank Adventurer"
        elif level == 13:
            role_name = "A+ Rank Adventurer"
        elif level == 14:
            role_name = "A++ Rank Adventurer"
        elif level == 15:
            role_name = "S Rank Adventurer"
        elif level == 16:
            role_name = "S+ Rank Adventurer"
        elif level == 17:
            role_name = "S++ Rank Adventurer"
        elif level == 18:
            role_name = "Mythical Adventurer"
        else:
            role = ctx.guild.get_role(role_id)
            role_name = role.name if role else "Role not found"

        roles_thresholds_string += f"Level {level}: {role_name}\n"

    embed = discord.Embed(title="Thresholds", color=discord.Color.blue())
    embed.add_field(name="Level Thresholds", value=level_thresholds_string, inline=False)
    embed.add_field(name="Roles Thresholds", value=roles_thresholds_string, inline=False)

    await ctx.send(embed=embed, ephemeral=True)


@add_coins.error
@delete_quest.error
@deduct_coins.error
@add_exp.error
@deduct_exp.error
@quest.error
@send_coins.error
@ticket.error
@show_emails.error
@confirm_salary.error
@confirmed_transactions.error
@pending_transactions.error
@send_email.error
async def admin_command_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    embed = discord.Embed(
      title="Not Allowed",
      description=
      "You don't have permission to use this command. Administrator permission is required.",
      color=discord.Color.red())
    await ctx.send(embed=embed, ephemeral=True)


keep_alive()
bot.run(os.environ['TOKEN'])
