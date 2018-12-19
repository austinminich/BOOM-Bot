#import asyncio
#import discord
import datetime
from discord.ext import commands
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

#Memory of spreadsheet
sheetStore = file.Storage('data/spreadsheet.txt')
sheetStore._create_file_if_needed()

#Setup API with read and write permissions
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('data/token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('data/credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

class GoogleSheets:
    """Built to integrate the bot to be able to put the attendance information into a Google Spreadsheet."""

    def __init__(self, bot):
        self.bot = bot
        f = open('data/spreadsheet.txt', 'r')
        self.master_ss = f.read()
        f.close()
        
    @commands.command()
    @commands.is_owner()
    async def writetosheet(self, ctx, cells = "A1", contents = []):
        """Writes to the designated cell, the contents of the message into the google sheet named 'BOOM-Bot Attendance'.
        Default cell is A1, default contents is '' (empty)."""
        
        values = contents
        
        #Check if sheet exists first
        if (self.DoesSheetExist()):
            valueBody = {
                "range": "BOOM-Bot Attendance!{}".format(cells),
                "values": values
            }
            result = service.spreadsheets().values().update(spreadsheetId = self.master_ss, range = "BOOM-Bot Attendance!{}".format(cells), valueInputOption = "USER_ENTERED", body = valueBody).execute()
            print("Updated cell.")
            await ctx.send("Wrote contents of the message to the set spreadsheet.")
        else:
            await ctx.send("The 'BOOM-Bot Attendance' sheet does not exist in the set spreadsheet. Refer to 'spreadsheet' command.")
        
    @commands.command()
    @commands.is_owner()
    async def readsheet(self, ctx, cells = "A1"):
        """Reads the contents of designated cell from the google sheet named 'BOOM-Bot Attendance'.
        Default cell is A1."""
        
        #Check if sheet exists first
        if (self.DoesSheetExist()):
            result = service.spreadsheets().values().get(spreadsheetId=self.master_ss, range="BOOM-Bot Attendance!{}".format(cells)).execute()
            values = result.get('values', [])
            for cell in values:#Values is an array of lists
                print("Read cell.")
                for data in cell:#cell is actually a list
                    await ctx.send("Cell '{}' contains: '{}'".format(cells, data))
        else:
            ctx.send("The 'BOOM-Bot Attendance' sheet does not exist in the set spreadsheet. Refer to 'spreadsheet' command.")
        
    @commands.command()
    @commands.is_owner()
    async def attendanceSheet(self, ctx):
        """Writes the attendance taken to the google sheet named 'BOOM-Bot Attendance'"""
        
        #
        
    @commands.command()
    @commands.is_owner()
    async def spreadsheet(self, ctx, spreadsheet_link = None):
        """Connects the bot to the spreadsheet and stores it into memory so you don't have to do it everytime."""
        
        #Just stores spreadsheet_id into txt file and connects
        if(spreadsheet_link == None):#Wasn't given
            await ctx.send("You never gave a spreadsheet to connect to. Current connected spreadsheet is: {}".format(self.master_ss))
        else:#spreadsheet
            try:
                #Grab spreadsheet_id
                spreadsheet_link = spreadsheet_link.strip('https://')
                spreadsheet_link = spreadsheet_link.strip('docs.google.com/spreadsheets/d/')
                spreadsheet_link = spreadsheet_link.split('/')
                
                if(spreadsheet_link[0] != self.master_ss):#Different/new Spreadsheet
                    #open file and write new spreadsheet_id to file
                    file = open("data/spreadsheet.txt", "w")
                    file.write(spreadsheet_link[0])
                    self.master_ss = spreadsheet_link[0]
                    file.close()
                    print("Saved new spreadsheet as master.")
                    await ctx.send("Entered a new spreadsheet. The given spreadsheet is now the saved spreadsheet.")
                    
                else:#Same spreadsheet
                    await ctx.send("Entered previous spreadsheet. Nothing changed.")
                    
                #Check to see if sheet is created already
                if(self.DoesSheetExist()):#Returns true/false
                    await ctx.send("Sheet exists in spreadsheet. Not creating new sheet.")
                    print("Sheet exists in spreadsheet. Not creating new sheet.")
                    return#Don't create another sheet if the sheet already exists
                self.CreateNewSheet("BOOM-Bot Attendance")#Set to have sheet name be "BOOM-Bot Attendance"
                await ctx.send("Created new sheet in spreadsheet.")
                print("Created new sheet in spreadsheet.")
                self.InitializeSheet("BOOM-Bot Attendance")#Set up the sheet for taking attendance
                await ctx.send("Initialized new sheet in spreadsheet.")
                print("Initialized new sheet in spreadsheet.")
            except:
                await ctx.send("Failed to create new sheet in spreadsheet.")
                print("Failed to created new sheet in spreadsheet.")
    
    def DoesSheetExist(self):
        """Checks to see if the default sheet is a part of the spreadsheet."""
        
        #Get all the spreadsheet sheets' data
        result = service.spreadsheets().get(spreadsheetId = self.master_ss, ranges = [], includeGridData = False).execute()
        for sheet in result["sheets"]:#Check all titles = our name
            if sheet["properties"]["title"] == 'BOOM-Bot Attendance':
                return True
        return False
    
    def CreateNewSheet(self, sheetName = None):
        """Creates new sheet called the given name on a Google spreadsheet to then use to write and read to."""
        
        try:
            createBody = {
                'requests': [
                    {
                        "addSheet": {
                            "properties": {
                                "title": "{}".format(sheetName),
                                "gridProperties": {
                                    "rowCount": 4,
                                    "columnCount": 5
                                }
                            }
                        }
                    }
                ]
            }
            #Create the page
            result = service.spreadsheets().batchUpdate(spreadsheetId = self.master_ss, body = createBody).execute()
            
        except:
            print('ERROR in CreateNewSheet method')
    def InitializeSheet(self, sheetName = None):
        """Writes the first row of cells so that it's setup to write and read to and from."""
        #Enter the default values for the categories
        requestBody = {
            "data": [
                {
                    "majorDimension": "COLUMNS",
                    "range": "{}!A1:E1".format(sheetName),
                    "values": [
                        ["Discord ID"],
                        ["Discord Name"],
                        ["Family Name"],
                        ["Character Name"],
                        ["DATE LINE"]
                    ]
                }
            ],
          "valueInputOption": "RAW"
        }
        result = service.spreadsheets().values().batchUpdate(spreadsheetId = self.master_ss, body = requestBody).execute()
        print("Initialized new sheet with format")
    
    def PopulateSheet(data = {}):
        """Updates the sheet to include all persons given."""
        #{'days': ['7/27/2018'], '74233077987024896': 
            #{'name': 'KaBOOM#7402', 'dates': ['7/27/2018'], 'familyName': '', 'siege': 0}}
        f = open('data/spreadsheet.txt', 'r')
        master_ss = f.read()
        f.close()
        
        try:
            #if(gs.DoesSheetExist() == True):
                #print("there")
                #gs.CreateNewSheet("BOOM-Bot Attendance")
                #gs.InitializeSheet("BOOM-Bot Attendance")
            ranges = [
                "BOOM-Bot Attendance!E1:1",
                "BOOM-Bot Attendance!A:A"
            ]
            result = service.spreadsheets().values().batchGet(spreadsheetId = master_ss, ranges=ranges).execute()
            #Result
            # {
                # 'spreadsheetId': '1ciOgMDpeDWtkFHUQrfCEgqyU-yCqVb2dHYTZx3spTXE',
                # 'valueRanges': [
                    # {
                        # 'range': "'BOOM-Bot Attendance'!E1",
                        # 'majorDimension': 'ROWS',
                        # 'values': [
                            # ['DATE LINE']
                        # ]
                    # },
                    # {
                        # 'range': "'BOOM-Bot Attendance'!A1:A5",
                        # 'majorDimension': 'ROWS',
                        # 'values': [
                            # ['Discord ID'],
                            # ['dsa'],
                            # ['asd'],
                            # ['123']
                        # ]
                    # }
                # ]
            # }
            
            dates = result["valueRanges"][0]["values"]#List of lists
            discordNums = result["valueRanges"][1]["values"]#List of lists
            
            newDate = True
            #Parse thru dates (result['values']) and add new column if today's date is a new one
            #   print("{}".format(dates[len(dates) - 1][0])) weird formatting
            
            
            weekNum = datetime.datetime.now().isocalendar()[1]
            #["week{}".format(weekNum)]
            today = datetime.datetime.now().date()
            lastDay = dates[0][len(dates[0]) - 1]
            result = service.spreadsheets().get(spreadsheetId=master_ss, ranges="BOOM-Bot Attendance!A1").execute()
            master_ss_id = result["sheets"][0]["properties"]["sheetId"]
            print(data)
            print("----------------------------------")
            
            if "week{}".format(weekNum) != "{}".format(lastDay):#If today's date matches
            
                #Create new column with date
                #print(result["sheets"][0]["properties"]["sheetId"]) Sheet id of sheet called BOOM-Bot Attendance
                requestBody = {
                    "requests": [
                        {
                            "appendDimension": {
                                "sheetId": master_ss_id,
                                "dimension": "COLUMNS",
                                "length": 1
                            }
                        },
                        {
                            "autoResizeDimensions": {
                                "dimensions": {
                                    "sheetId": master_ss_id,
                                    "dimension": "COLUMNS",
                                    "startIndex": 0
                                }
                            }
                        }
                    ]
                }
                result = service.spreadsheets().batchUpdate(spreadsheetId = master_ss, body=requestBody).execute()
                
                #Update first cell of new column to include current date.
                valueBody = {
                    "range": "BOOM-Bot Attendance!{}1".format(chr(len(dates) + 69)),
                    "values": [
                        [
                            "week{}".format(weekNum)#Did contain the physical date of the date it was taken
                        ]
                    ]
                }
                result = service.spreadsheets().values().update(spreadsheetId = master_ss, range = "BOOM-Bot Attendance!{}1".format(chr(len(dates) + 69)), valueInputOption = "USER_ENTERED", body = valueBody).execute()
                print("New date. Added column and new date to sheet.")
                ###End of if statement for date already existing
               
            peopleToAdd = list(data["week{}".format(weekNum)].keys())
            peopleToAdd.remove("days")#Contains now only the members to compare to
            #Find Discord # in sheet and 
            for key, value in data["week{}".format(weekNum)].items():
                if str(key) != "days":
                    for person in discordNums:
                        if person[0] == key:
                            #Update attended days cell
                            peopleToAdd.remove(key)
                            #print(data["week{}".format(weekNum)]["{}".format(key)]["dates"])
                            valueBody = {#Update discord name (overwrites even if it's the same)
                                "valueInputOption": "USER_ENTERED",
                                "data": [
                                    {
                                        "majorDimension": "COLUMNS",
                                        "range": "BOOM-Bot Attendance!B{}".format(discordNums.index(person) + 1),
                                        "values": [
                                            [
                                                "{}".format(data["week{}".format(weekNum)]["{}".format(key)]["name"])
                                            ]
                                        ]
                                    },
                                    {
                                        "majorDimension": "COLUMNS",
                                        "range": "BOOM-Bot Attendance!{}{}".format(chr(len(dates) + 69), discordNums.index(person) + 1),
                                        "values": [
                                            [
                                                "{} / Siege: {}".format(data["week{}".format(weekNum)]["{}".format(key)]["dates"], data["week{}".format(weekNum)]["{}".format(key)]["siege"])
                                            ]
                                        ]
                                    }
                                ]
                            }
                            result = service.spreadsheets().values().batchUpdate(spreadsheetId = master_ss, body = valueBody).execute()
                            print("Updated existing user in spreadsheet.")
                            
            if len(peopleToAdd) > 0:#Need to add members to sheet
                #Add right amount of rows to sheet
                requestBody = {
                    "requests": [
                        {
                            "appendDimension": {
                                "sheetId": master_ss_id,
                                "dimension": "ROWS",
                                "length": len(peopleToAdd)
                            }
                        }
                    ]
                }
                result = service.spreadsheets().batchUpdate(spreadsheetId = master_ss, body=requestBody).execute()
                
                i = 0
                startIndex = len(discordNums)
                #while((len(peopleToAdd) > 0) and (i < len(peopleToAdd))):
                
                #Add information for the newly added rows corresponding to how many people need to be added
                print(discordNums)#len(discordNums)
                print(peopleToAdd)
                #print(data)
                print(data["week{}".format(weekNum)])
                print("Person: {}".format(i))
                for person in peopleToAdd:
                    i += 1
                    requestBody = {
                        "valueInputOption": "USER_ENTERED",
                        "data": [
                            {
                                "majorDimension": "COLUMNS",
                                "range": "BOOM-Bot Attendance!A{}:B{}".format(startIndex + 1, startIndex + 1),
                                "values": [
                                    [
                                        "{}".format(person)
                                    ],
                                    [
                                        "{}".format(data["week{}".format(weekNum)]["{}".format(person)]["name"])
                                    ]
                                ]
                            },
                            {
                                "majorDimension": "COLUMNS",
                                "range": "BOOM-Bot Attendance!{}{}".format(chr(len(dates) + 69), startIndex + 1),
                                "values": [
                                    [
                                        "{} / Siege: {}".format(data["week{}".format(weekNum)]["{}".format(person)]["dates"], data["week{}".format(weekNum)]["{}".format(person)]["siege"])
                                    ]
                                ]
                            }
                        ]
                    }
                    startIndex += 1
                    result = service.spreadsheets().values().batchUpdate(spreadsheetId = master_ss, body=requestBody).execute()
                
                print("{} new names added to the sheet.".format(len(peopleToAdd)))
                
            #Update the column width
            requestBody = {
                "requests": [
                    {
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": master_ss_id,
                                "dimension": "COLUMNS",
                                "startIndex": 0
                            }
                        }
                    }
                ]
            }
            result = service.spreadsheets().batchUpdate(spreadsheetId = master_ss, body=requestBody).execute()
            print("Updated column width in spreadsheet.")
            
            return "Successfully updated Google sheet with attendance."
        except:
            print("Problem updating Google sheet while taking attendance. [Error from: GoogleSheets.PopulateSheet()]")
            return("Problem updating Google sheet while taking attendance. Make sure the spreadsheet has the sheet 'BOOM-Bot Attendance' if not, use `spreadsheet command.")
    
def setup(bot):
    a = GoogleSheets(bot)
    bot.add_cog(a)
    
    print("GoogleSheets extension is loaded")