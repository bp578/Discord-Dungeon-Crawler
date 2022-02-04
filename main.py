import os
from discord.ext import commands
import discord

bot = commands.Bot(
	command_prefix="!",
	case_insensitive=True
)

bot.author_id = 487258918465306634  # Change to your discord id!!!

async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def repeat(ctx, arg):
	await ctx.send(arg)
@bot.command()
async def help2(ctx):
	await ctx.send("I am unhelpful")
@bot.command()
async def message(ctx, message="Hello"):
  user = ctx.author
  await user.send(message)

token = "OTM4OTY5NDk3MTI0MDg1ODQx.YfyBfQ.smaJcZWXYUp8J5Dv82yH9sH2CUU"
bot.run(token)  # Starts the bot
