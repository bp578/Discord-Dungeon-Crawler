import os
from discord.ext import commands
import discord
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
		state.handle_reaction(reaction)


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
	await ctx.reply("A new adventure begins in a dark dungeon...")
	# start encounter
	encounter_msg = await ctx.send("You encounter a savage goblin")
	state.new_encounter(ctx.author, encounter_msg)

@bot.command()
async def eg(ctx):
	await ctx.reply("You have cut your own life short. Better luck on your next adventure.")
	state.close_encounter(ctx.author)

@bot.command()
async def stats(ctx):
	text = """
HP: 100  
ATK: 5
DEF: 5
SPD: 5
	"""
	await ctx.reply(text)

token = "OTM4OTY5NDk3MTI0MDg1ODQx.YfyBfQ.smaJcZWXYUp8J5Dv82yH9sH2CUU"
bot.run(token)
