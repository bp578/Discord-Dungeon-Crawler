import os
from discord.ext import commands
import discord

bot = commands.Bot(
	command_prefix="!",
	case_insensitive=True,
	help_command=None
)

bot.author_id = 487258918465306634  # Change to your discord id!!!

@bot.event
async def on_ready():  # When the bot is ready
	print("I'm in")
	print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def ping(ctx):
    await ctx.reply("pong!")
@bot.command()
async def repeat(ctx, arg):
	await ctx.send(arg)
@bot.command()
async def help(ctx, help_message="ng: Begin a new game eg: End current game stats: Display your current stats"):
	user = ctx.author
	await user.send(help_message)

token = "OTM4OTY5NDk3MTI0MDg1ODQx.YfyBfQ.smaJcZWXYUp8J5Dv82yH9sH2CUU"
bot.run(token)  # Starts the bot
