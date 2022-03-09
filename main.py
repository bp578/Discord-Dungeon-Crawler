import os
from dotenv import load_dotenv
load_dotenv()
from discord.ext import commands, tasks
import discord
import gamestate
from gamestate import GameState

bot = commands.Bot(
	command_prefix="!",
	case_insensitive=True,
	help_command=None
)
bot.author_id = 487258918465306634  # Change to your discord id!!!

state = GameState()

@bot.event
async def on_ready():
	print("I'm in")
	print(bot.user)  # Prints the bot's username and identifier

@bot.event
async def on_reaction_add(reaction, user):
	if user != bot.user:
		await state.handle_reaction(reaction, user)


@bot.command(profile=['user'])
async def profile(ctx,member : discord.Member):
    embed = discord.Embed(title = member.name, color = discord.Color.blue())
    embed.add_field(name = "ID", value = member.id, inline = True)
    embed.set_thumbnail(url = member.avatar_url)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
	await ctx.reply("pong!")

@bot.command()
async def help(ctx):
	text = """
ng: Begin a new game 
eg: End current game 
stats: Display your current stats
	"""
	user = ctx.author
	await user.send(text)

@bot.command()
async def ng(ctx):
  #beginGame is called once the player picks a class. 
  async def beginGame():
	  start_msg = await ctx.reply("A new adventure begins in a dark dungeon...")
	  # start encounter
	  encounter_msg = await ctx.send("You have come upon a savage beast...")
	  if not state.new_encounter(ctx.author, encounter_msg):
		  await start_msg.edit(content="You are already in an encounter....")
		  await encounter_msg.delete()

  classSelectContents = '''React to pick your class:
   1. Warrior ⚔️
   2. Mage ✨
   3. Rogue 🗡
   4. Tank 🛡️
   5. Marksman 🏹
  '''
  #classSelectMsg is the first thing sent upon starting a new game.
  classSelectMsg = await ctx.send(classSelectContents)
  await classSelectMsg.add_reaction("⚔️")
  await classSelectMsg.add_reaction("✨")
  await classSelectMsg.add_reaction("🗡")
  await classSelectMsg.add_reaction("🛡️")
  await classSelectMsg.add_reaction("🏹")

  #This function checks what emoji the player reacted with and changes their class accordingly
  async def check(reaction, user):
    if user == ctx.author and reaction.emoji in ["⚔️","✨","🗡","🛡️","🏹"]:
      if reaction.emoji == "⚔️":
        await ctx.send("You picked: Warrior")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Warrior"
      elif reaction.emoji == "✨":
        await ctx.send("You picked: Mage")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Mage"
      elif reaction.emoji == "🗡":
        await ctx.send("You picked: Rogue")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Rogue"
      elif reaction.emoji == "🛡️":
        await ctx.send("You picked: Tank")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Tank"
      elif reaction.emoji == "🏹":
        await ctx.send("You picked: Marksman")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Marksman"
  state.add_reaction_handler(classSelectMsg, check)

@bot.command()
async def eg(ctx):
	if state.close_encounter(ctx.author):
		await ctx.reply("You have cut your own life short. Better luck on your next adventure.")
	else:
		await ctx.reply("You are not currently in an encounter...")

data = {
  "HP:": 100,
  "ATK:": 5,
  "DEF:": 5,
  "SPD:": 5,
  "STR:": 5,
  "INT:": 0,
  "REG:": 0,
  "RMP:": 0,
}

@bot.command()
async def delete_register(ctx):
    if str(ctx.author.id) in state.players:
        state.delete_player_data(ctx.author)
        await ctx.reply("Data successfully deleted")
    else:
        await ctx.reply("You didn't register yet!")

@bot.command()
async def register(ctx):
    if str(ctx.author.id) in state.players:
        await ctx.reply("You already registered before")
    else:
        state.change_player_data(ctx.author, data)
        await ctx.reply("You successfully registered")

@bot.command()
async def stats(ctx):
	# check if player has registered
    if str(ctx.author.id) in state.players:
		# get data
        data = state.get_player_data(ctx.author)
		# format data into string
        string = ""
        for key, val in data.items():
            string += key + str(val) + "\n"
        await ctx.reply(string)
    else:
        await ctx.reply("You need to register with `!register` first")

@state.run_updates.before_loop
async def before_updates(self):
	await bot.wait_until_ready()

state.run_updates.start()
token = os.getenv("TOKEN")
bot.run(token)
