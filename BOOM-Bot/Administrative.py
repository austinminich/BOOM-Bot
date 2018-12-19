import json
import asyncio
import discord
from discord.ext import commands
import os
import datetime

class Administrative:
    """asd"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def moveall(self, ctx, channelTo, channelFrom=None):
        """Moves all people in current or specific channel to the specified channel."""
        
        requester = ctx.message.author
        guildChannels = ctx.message.guild.channels
        
        if requester.voice != None:#channelFrom is not specified AND requester is not in a channel
            if channelFrom == None:
                channelFrom = requester.voice.channel
            channelFrom = discord.utils.find(lambda x: x.name == "{}".format(channelFrom), guildChannels)
            channelTo = discord.utils.find(lambda x: x.name == "{}".format(channelTo), guildChannels)
            if channelTo != None and channelFrom != None:
                members = channelFrom.members
                if len(members) != 0:
                    await ctx.send("Moving members from '{}' to '{}'".format(channelFrom, channelTo))
                    for member in members:
                        await member.move_to(channelTo)
                    return
                else:
                    await ctx.send("There are no members in '{}'.".format(channelFrom))
                    return
            else:
                await ctx.send("At least one of the specified channels doesn't exist in this Discord.")
                return
        else:
            await ctx.send("You're not in a voice channel and left out which channel to move members from.")
            return
    
    @commands.command()
    async def datetime(self, ctx):
        """Prints what the date including the week number to grab the weekNum from attendance database. The week starts on Sunday and ends Saturday"""
        datetime.datetime.now().isocalendar()[1]
        now = datetime.datetime.now()
        await ctx.send("The current date is {}, current week number for attendance database is {}".format(datetime.datetime.now().isocalendar()[0], datetime.datetime.now().isocalendar()[1]))
        
def setup(bot):
    a = Administrative(bot)
    bot.add_cog(a)
    print("Administrative extension is loaded")