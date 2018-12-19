import asyncio
import discord
from discord.ext import commands
import os
import datetime
import json
from GoogleSheets import GoogleSheets

filePathAtt = "data/attendance.json"
filePathFam = "data/familynames.json"
directoryAtt = os.path.dirname(filePathAtt)
directoryFam = os.path.dirname(filePathFam)

class Attendance:
    """Built to record the members of a discord channel and add to a json file."""
        
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.familyData = {}
        self.testData = []
        
    @commands.command()
    @commands.is_owner()
    async def test(self, ctx):
        """Just used for testing purposes. Owner only!"""
        
        now = datetime.datetime.now()
        weekNum = now.isocalendar()[1]
        
        requester = ctx.message.author
        members = requester.voice.channel.members#Grab the members in the requester's channel
        info = self.ParseChannelMembers(members, now)#Parse member data
        
        self.PopulateData(info, now, weekNum)
        await ctx.send(GoogleSheets.PopulateSheet(data=self.data))
        
        
    #Need the following roles have access to this command: Council, Spreadsheet, Community Head
    @commands.command()
    async def takeattendance(self, ctx):#Possibly have an argument being 'new' for new week or not
        """Grabs the users' information in the channel that the requester is in and stores
        their info in the database. ```Requires the requester to be in a voicechannel```"""
        
        now = datetime.datetime.now()
        weekNum = now.isocalendar()[1]
        requester = ctx.message.author
        
        if (requester.id == 131989444461985803):
            await ctx.send("```Sorry Chimi, you need adult super vision.```")
            return
        if(self.CheckRoles(requester)):#Has correct permission
            if ((now.hour >= 18 and now.hour <= 20 and now.weekday() != 5) or (now.hour >= 18 and now.hour <= 22 and now.weekday() == 5) or (requester.id == 74233077987024896)):
                if (requester.voice is not None):#Grab Channel of requester
                    members = requester.voice.channel.members#Grab the members in the requester's channel
                    info = self.ParseChannelMembers(members, now)#Parse member data
                    returnString = "```"
                    returnString += self.LoadJSON(filePathFam, directoryFam)#Populates class's data{} which we'll append to
                    returnString += "\n"
                    returnString += self.LoadJSON(filePathAtt, directoryAtt)#Populates class's data{} which we'll append to
                    returnString += "\n"
                    returnString += self.PopulateData(info, now, weekNum)#Populates class's data{} with members
                    returnString += "\n"
                    returnString += self.SaveJSON(self.data, filePathAtt, directoryAtt)#Saves class's data{} to file
                    returnString += "\n"
                    #returnString += GoogleSheets.PopulateSheet(self.data)
                    returnString += "```"
                    await ctx.send("{}".format(returnString))
                    #await ctx.send("You are in the '{}' channel. Here are the members in the channel:\n```{}```".format(requester.voice.channel, info))
                else:
                    await ctx.send("You are not in a channel.")
            else:
                await ctx.send("It is not node war time.")
        else:
            await ctx.send("Nanananana, you can't do that.")
            
    @commands.command()
    async def getattendance(self, ctx, weekNum = datetime.datetime.now().isocalendar()[1]):
        """*WARNING* Spams the channel with all the members that attended nodewar in the same week
        a list of users and how many wars they attended in the same week.
        (Requires to be done before Sunday @ 11:59pm PST as the week resets Monday)"""
        #Grab the latest or the given week's attendance.
        
        returnString = "```"
        returnString += self.LoadJSON(filePathAtt, directoryAtt)
        returnString += "```"
            
        attendanceList = self.AttendanceFormat(weekNum)
        i = 0
        for string in attendanceList:
            await ctx.send("{}".format(attendanceList[i]))
            i += 1
            
    @commands.command()
    async def setfamilyname(self, ctx, *args):
        """Allows a person to give their familyname to be stored in the database.
        ```Takes only 1 argument which is the familyname that you want to store.```"""
        
        now = datetime.datetime.now()
        weekNum = now.isocalendar()[1]
        requester = ctx.message.author
        returnString = ""
        
        if (len(args) > 1):
            returnString += ("You entered too many arguments. Took the first one after: '`setfamily'\n")
        if (len(args) != 0):
            returnString += "```"#For appearance
            returnString += self.LoadJSON(filePathFam, directoryFam)
            returnString += "\n"
            returnString += self.ChangeFamilyName(requester.id, args[0])
            returnString += "\n"
            returnString += self.SaveJSON(self.familyData, filePathFam, directoryFam)
            returnString += "```"
            await ctx.send("{}".format(returnString))
        else:
            await ctx.send("You must give your family name and don't have to give anything else.")
            
    def AttendanceFormat(self, weekNum):
        """Grabs information about the recent week's attendance and returns a neatly 
        organized string."""
        
        returnString = []
        counter = 0
        returnString.append("```Total amount of people attending this week's wars are: [")
        returnString[counter] += str(len(self.data["week{}".format(weekNum)]))
        returnString[counter] += "]\nDays attendance was taken are: "
        returnString[counter] += str(self.data["week{}".format(weekNum)]["days"])
        returnString[counter] += "```"
        counter += 1
        for key, value in self.data["week{}".format(weekNum)].items():#For each member in the week
            if key != "days":
                returnString.append(str(self.data["week{}".format(weekNum)][key]["name"]))
                returnString[counter] += ": Attended ["
                returnString[counter] += str(len(self.data["week{}".format(weekNum)][key]["dates"]))
                returnString[counter] += "] days, and ["
                returnString[counter] += str(self.data["week{}".format(weekNum)][key]["siege"])
                returnString[counter] += "] siege, familyName: "
                returnString[counter] += self.data["week{}".format(weekNum)][key]["familyName"]
                returnString[counter] += "\n"
                counter += 1
        self.testData = returnString
        return returnString#aproximately double the total amount of text to send
            
    def ParseChannelMembers(self, members, now):
        """Only grabs important information from a list of members."""
        
        info = {}
        for member in members:
            memberInfo = {}#Change to a dictionary
            if(member.bot == False):
                memberInfo['name'] = ("{}#{}".format(member.name, member.discriminator))
                memberInfo['dates'] = ["{}".format(now.date())]#----------------------------------CHANGED THIS--------------------------------------------
                memberInfo['familyName'] = ""
                info["{}".format(member.id)] = memberInfo
        return info
            
    def PopulateData(self, memberInfo, now, weekNum):
        """Stores parsed memberInfo into the data."""
        
        now = datetime.datetime.now()
        try:#Filling data if the week exists with info
            if (self.data["week{}".format(weekNum)]):#Week exists with info
                for key, value in memberInfo.items():
                    if (value["dates"][0] not in self.data["week{}".format(weekNum)]["days"]):#New day
                        self.data["week{}".format(weekNum)]["days"].append(value["dates"][0])
                    else:
                        pass
                for key, value in memberInfo.items():
                    if (key not in self.data["week{}".format(weekNum)]):#Member id isnt in dict
                        self.data["week{}".format(weekNum)]["{}".format(key)] = value
                    else:#The member already attended once this week
                        #Check if the date being added is already in there (ie. called twice in one )
                        if (value["dates"][0] in self.data["week{}".format(weekNum)]["{}".format(key)]["dates"]):
                            print("Date already exists, skiping person.")
                        else:
                            self.data["week{}".format(weekNum)]["{}".format(key)]["dates"].append(value["dates"][0])
                    if (now.weekday() == 5):#Checks if the day is a Saturday
                        self.data["week{}".format(weekNum)]["{}".format(key)]["siege"] = 1
                    else:
                        self.data["week{}".format(weekNum)]["{}".format(key)]["siege"] = 0
                    try:
                        self.data["week{}".format(weekNum)]["{}".format(key)]["familyName"] = self.familyData["{}".format(key)]
                    except:
                        pass
                return "Successfully populated attendance data."
        except:
            pass
        try:#Creating and filling data if the week DOES NOT exist
            self.data["week{}".format(weekNum)] = {}#Create FIRST and ONCE
            for key, value in memberInfo.items():
                self.data["week{}".format(weekNum)]["days"] = []
                self.data["week{}".format(weekNum)]["days"].append(value["dates"][0])#Only should happen once
                break#Only once
            for key, value in memberInfo.items():
                self.data["week{}".format(weekNum)]["{}".format(key)] = value
                if (now.weekday() == 5):#Checks if the day is a Saturday
                    self.data["week{}".format(weekNum)]["{}".format(key)]["siege"] = 1
                else:
                    self.data["week{}".format(weekNum)]["{}".format(key)]["siege"] = 0
                try:
                    self.data["week{}".format(weekNum)]["{}".format(key)]["familyName"] = self.familyData["{}".format(key)]
                except:
                    pass
            return "Successfully populated attendance data."
        except:
            print("Something went wrong populating software data. Contact KaBOOM with: [Error: PopulateData() Line 202]")
            pass
        return "Something went wrong populating software data. Contact KaBOOM with: [Error: PopulateData()]"
        
    def ChangeFamilyName(self, id, name):
        """Compares name and id given to the database's information and updates accordingly."""
        
        try:#Adding/changing name is id exists
            self.familyData["{}".format(id)] = "{}".format(name)
            print("Updated '{}' to '{}'".format(id, name))
            return "Successfully populated family name data."
        except:
            pass
        return "Something went wrong populating software data. Contact KaBOOM with: [Error: ChangeFamilyName()]"
        
    def CheckRoles(self, requester):
        """Makes sure that the correct people can take attendance."""
        
        role = discord.Role
        wanted = ["Community Head", "Council", "Spreadsheet", "Admin"]#Required Permissions
        #role = discord.Role.name
        for roleName in wanted:
            for role in requester.roles:
                if role.name == roleName:
                    return True
        return False
        
    def CheckFile(self, filePath, directory):
        """Checks the filepath to see if the file exists, if not creates it blank."""
        
        try:
            if not os.path.exists(directory):#Check if folder and file paths exists
                os.makedirs(directory)#Makes folder(s)
                print("Directory didn't exist. Created new directory ({})".format(directory))
            if not os.path.exists(filePath):
                with open(filePath, 'w') as file:
                    #Creates file and initializes the file with data (should be empty)
                    json.dump(self.data, file)
                    print("File didn't exist. Created new file ({})".format(filePath))
            else:
                print("File found. Loaded data ({}).".format(filePath))
        except OSError as e:
            print("Error: {} [Error from: CheckFile()]".format(e))
        
    def SaveJSON(self, dataToSave : {}, filepath, dir):
        """Saves the dataToSave into the filepath and directory."""
        
        #Append to file
        try:
            if os.path.exists(dir):
                with open(filepath, 'w') as file:
                    json.dump(dataToSave, file)
                    return "Successfully wrote to file."
            else:
                print("Problem finding the file to write to. [Error from: SaveJSON()]")
                return "Problem finding the file to write to. Contact KaBOOM with [Error from: SaveJSON()]"
        except:
            print("Problem writing to file. [Error from: SaveJSON()]")
            return "Problem finding the file to write to. Contact KaBOOM with [Error from: SaveJSON()]"
        
    def LoadJSON(self, filepath, dir):
        """Loads the data from the filepath and directory."""
        
        #Load from file to dictionary
        if os.path.exists(dir):
            #with open(filepath, 'r') as file:
            dataStore = json.load(open(filepath))
            #file.close()
            if (not dataStore):#Nothing is in the file
                return "No existing file. Created new file."
            else:
                if (filepath == filePathAtt):
                    self.data = dataStore
                elif (filepath == filePathFam):
                    self.familyData = dataStore
                return "Successfully found and loaded file."
        else:
            print("Problem finding the file to read from. [Error from: LoadJSON()]")
            return "Problem finding the file to read from. Contact KaBOOM with [Error from: LoadJSON()]"
            
def setup(bot):
    a = Attendance(bot)
    bot.add_cog(a)
    a.CheckFile(filePathAtt, directoryAtt)
    a.CheckFile(filePathFam, directoryFam)
    print("Attendance extension is loaded")