#Imported classes
import discord
import asyncio
import youtube_dl
from discord.ext import commands
import datetime

#Created classes
import config

description = """A practice bot to get familiar with Python, provide music for friends' discords,
and provide easier attendance recording for a BDO guild (Notorious)"""

#This class is the main controller for the entire bot

#This specifies what extensions to load on bot startup
startupExtensions = ["Attendance", "Administrative", "GoogleSheets"]

botVersion = "1.1.2 - 7/21/18" #Arbitrary bot version with date it was updated.

bot = commands.Bot(command_prefix = "`", owner_id = 74233077987024896, decription=description) #Command character
startTime = now = datetime.datetime.now()

@bot.command()
async def version(ctx):
    """Displays the version of the bot."""
    await ctx.send("BOOMBot version is: {}".format(botVersion))
    
@bot.command()
async def uptime(ctx):
    """Displays the version of the bot."""
    await ctx.send("```BOOMBot has been online since {} PST. Duration: {}```".format(startTime, datetime.datetime.now() - startTime))

@bot.event
async def on_ready():
    print("----------------------")
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("Description: ")
    print(description)
    print("----------------------")

@bot.command()
@commands.is_owner()
async def load(ctx, extensionName : str):
    """Loads an extension."""
    try:
        bot.load_extension(extensionName)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extensionName))

@bot.command()
@commands.is_owner()
async def unload(ctx, extensionName : str):
    """Unloads an extension."""
    bot.unload_extension(extensionName)
    await ctx.send("{} unloaded.".format(extensionName))
    print("{} unloaded.".format(extensionName))
    
@bot.event
async def on_command_error(ctx, exception):
    """On command error, prints info. to the user."""
    print("Ignored exception in command {} with the exception {}".format(ctx.command, exception))
    #ctx.send("Failed to command the great BOOMBot. Try using `help to find the correct command.")
    

for extension in startupExtensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))
    
bot.run(config.token) #Starts the bot with the given API code
