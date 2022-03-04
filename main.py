import os
from dotenv import load_dotenv
load_dotenv()
from discord.ext import commands, tasks
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
		await state.handle_reaction(reaction, user)

<<<<<<< HEAD
@bot.command(profile=['user'])
async def profile(ctx,member : discord.Member):
    embed = discord.Embed(title = member.name, color = discord.Color.blue())
    embed.add_field(name = "ID", value = member.id, inline = True)
    embed.set_thumbnail(url = member.avatar_url)
    await ctx.send(embed=embed)

=======
@bot.command(profile=['user']}
async def profile(ctx,member : discord.Member):
    embed = discord.Embed(title = member.name, color = discord.Color.blue())
    embed.add_field(name = "ID", value = member.id, inline = true)
    embed.set_thumbnail(url = member.avatar_url)
    await ctx.send(embed=embed)
	
>>>>>>> 1522adf0f01947c442bf0e34d5e8e9a16f20b549
@bot.command()
async def selectClass(ctx):
	classSelectContents = '''Enter a number to pick your class:
	1. Warrior :crossed_swords:
	2. Mage :sparkles:
	3. Rogue :dagger:
	4. Tank :shield:
	5. Marksman :bow_and_arrow:
	'''
	classSelectMsg = await ctx.send(classSelectContents)
	async def check(reaction, user):
		if user == ctx.author and reaction.emoji in ["⚔️","✨","🗡️","🛡️","🏹"]:
			if reaction.emoji == "⚔️":
				await ctx.send("You picked: Warrior")
				gamestate.PLAYER_CLASS = "Warrior"
			elif reaction.emoji == "✨":
				await ctx.send("You picked: Mage")
				gamestate.PLAYER_CLASS = "Mage"
			elif reaction.emoji == "🗡️":
				await ctx.send("You picked: Rogue")
				gamestate.PLAYER_CLASS = "Rogue"
			elif reaction.emoji == "🛡️ ":
				await ctx.send("You picked: Tank")
				gamestate.PLAYER_CLASS = "Tank"
			elif reaction.emoji == "🏹":
				await ctx.send("You picked: Marksman")
				gamestate.PLAYER_CLASS = "Marksman"
	state.add_reaction_handler(classSelectMsg, check)
	
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
	start_msg = await ctx.reply("A new adventure begins in a dark dungeon...")
	# start encounter
	encounter_msg = await ctx.send("You have come upon a savage beast...")
	if not state.new_encounter(ctx.author, encounter_msg):
		await start_msg.edit(content="You are already in an encounter....")
		await encounter_msg.delete()

@bot.command()
async def eg(ctx):
	if state.close_encounter(ctx.author):
		await ctx.reply("You have cut your own life short. Better luck on your next adventure.")
	else:
		await ctx.reply("You are not currently in an encounter...")

@bot.command()
async def stats(ctx):
	text = """
HP: 100  
ATK: 5
DEF: 5
SPD: 5
	"""
	await ctx.reply(text)

@state.run_updates.before_loop
async def before_updates(self):
	await bot.wait_until_ready()

state.run_updates.start()
token = os.getenv("TOKEN")
bot.run(token)

