'''
TODO:
None

KNOWN BUGS:
None

FEATURES I WANT BUT PROBABLY WON'T HAVE TIME TO ADD:
replays
rule presets
cpu difficulty
custom player names
random settings option

The rest of this multi-line comment below are just notes
I typed down in the planning stage when I first started,
so they may not be accurate to the final product.

started on: Nov. 13, 2023
ended on: Nov. 29, 2023

for i in range(42): print("="*104)

https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
https://www.geeksforgeeks.org/print-colors-python-terminal/#
print("\033[94m"+"Hello"+"\033[0m")

options:
number of players (2-16)
number of decks (1-8)
number of colors (2-8)
turn time limit (1sec-10min)
jump in time limit (1sec-10sec)
special cards (skip, reverse, +4, etc.)
jump in
+2 +4 stacking
7 0
force play
no bluffing on wild cards
draw until exact match
challenge

stats:
score
time

score:
playing a card gives points
having enemies draw cards gives you +1 per card (+2 if it's because of you)

points per card:
regular = +1
special = +2
plus 4 = +4

can fit 104x42 characters
─ - u2500
│ - u2502
┌ - u250C
┐ - u2510
└ - u2514
┘ - u2518
├ - u251C
┤ - u2524
┬ - u252C
┴ - u2534
┼ - u253C
╭ - u256D
╮ - u256E
╯ - u256F
╰ - u2570

╭─╮╭─╮╭─╮
│R││+││S│
│4││4││K│
╰─╯╰─╯╰─╯

┌──────────────────────────────────────────────────┐
│                                                  │
│                                                  │
│                                                  │
└──────────────────────────────────────────────────┘

                    Cards   Score
				    Left
		    ╭─────┬───────┬─────────────┬
> Player 1: │ P1  │ 5     │ 000,000,000 │ Played a red 4
  Player 2: │ CPU │ 407   │ 000,000,000 │ Played a skip "UNO!"
            ╰─────┴───────┴─────────────┴
  Time: 2:00:00

 Options:
 0  1  2  3

 D    ╭─╮╭─╮
 R  < │+││R│
 A  < │4││S│
 W    ╰─╯╰─╯

Cards:
Blue/Red/Green/Yellow/Purple/Orange/Black/White | B-/R-/G-/Y-/P-/O-/K-/W-
0-9 | -0...-9
skip | -S
reverse | -R
+2 | -2
+4 | +4
wild | WD
'''

import os
import time
import math
import random

#for testing:
import sys
import traceback
#except Exception: print(traceback.format_exc())

pi = 3.1415926
soundOn = True
messageWaitTime = 3

#debug constants
sortByPlayability = False #sort the player's hand so that your playable cards show up first
timed = False
jumpInTimed = False
canPlayAnyCard = False
showAllCards = False #show other players' cards
debugCardHand = False #sets the cards instead of randomly giving them out
debugText = False #debug messages

#ai constants
unoCallRate = 90 #how often the ai will remember to call uno as a percentage (0 - 100)
unoReportRate = 90 #how often the ai will remember to report that a player has not called uno as a percentage (0 - 100)

#text constants
welcomeText = [ "Welcome to UNO", "Type numbers 1 - 4 to get started.", "", "1 - Play using the classic UNO settings", "2 - Play using the modern UNO settings", "3 - Play with custom settings", "4 - Exit"]
unknownCommand = ["Unknown or invalid command. Please try again"]
commandInfo = [
["Info","","The amount of players in the match."],
["Info","","The amount of decks of cards that will be put in the draw pile."],
["Info","","The amount of different colors a card can be."],
["Info","","The amount of seconds you have to complete your turn."],
["Info","","The amount of seconds you have to jump-in."],
["Info","","Whether or not special cards will be available.","E.g. skip, reverse, wild, +2, +4"],
["Info","","Whether or not players will be able to jump in.","If you have the exact same card as the card that has just been played,","You will be able to play that card regardless of which player's turn it is."],
["Info","","Whether or not +2 and +4 cards can stack.","If you are about to be affected by a +2 or +4 card and have that same card,","you can avoid having to draw cards and increase the amount of cards the next player will have to draw."],
["Info","","Whether or not 0/7 swaping will be enabled.","If a 7 card is played, the person that played it can swap cards with any player of their choosing.","If a 0 card is played, everyone's hands swap according to the turn order."],
["Info","","Whether or not force play is enabled.","You are only allowed to draw if you have to draw."],
["Info","","Whether or not bluffing is enabled.","When choosing a color after playing a wild or +4 card,","you are only allowed to choose colors that you have."],
["Info","","Whether or not draw to match is enabled.","If you need to draw a card, you have to keep drawing cards","until you get a playable card."],
["Info","","Whether or not challenges are enabled.","If you are affected by a +4 card, you can challenge it.","If the player that played the card was able to play a card other than the +4,,","you win and the cards that have to be drawn are split between the challenger and challengee.","If the player that played the card could not,","you lose and have to draw 2 extra cards."],
["Info","","The amount of cards everybody starts with."],
["Info","","The amount of actual human players that will be playing.","A value of 0 means that all players are CPU players and the game will play itself."],
["Info","","The amount of teams there are.","A value of 0 means there are no teams and it's a free-for-all."]
]

valueYes = ["Yes","yes","Y","y","True","true","T","t"]
valueNo = ["No","no","N","n","False","false","F","f"]
nums = ["0","1","2","3","4","5","6","7","8","9"]
numsAndSpace = ["0","1","2","3","4","5","6","7","8","9"," "]
colors = ["Blue","Red","Green","Yellow","Purple","Orange","Black","White"]
colorLetters = ["B","R","G","Y","P","O","K","W"]
jumpInLetters = [chr(65+x) for x in range(26)] #letters A-Z

#settings
playerCount = 0
deckCount = 0
colorCount = 0
turnLimit = 0
jumpInLimit = 0
specialCards = False
jumpIn = False
stacking = False
swaping = False #7/0
forcePlay = False
noBluffing = False
drawToMatch = False
challenge = False
startingCardCount = 0
realPlayerCount = 0
teamCount = 0

#stats
score = [] #1 for each player
startTime = 0 #time game started
turnStartTime = 0 #time turn started

#player parallel arrays (probably should have made a class for players)
hand = [] #2d array, cards for each player
lastAction = [] #player's last action
playerType = [] #true=player,false=cpu
calledUno = [] #true=called uno
teamAssignment = [] #which players are in which teams

#other
message = [] #message to be displayed above the gui
deck = [] #cards in deck
cardInPlay = 0 #card last placed down
playerTurn = 0 #who's turn it is (0-7)
cardPage = 0 #card page view
colorInPlay = 0 #the color of cardInPlay (0-7)
reverseTurnOrder = False #turn order. true=up,false=down
plusCardCombo = 0 #how many cards the next player will draw (mainly used for stacking)
previousCard = 0 #the previous cardInPlay (only used for challenging)

#card constructor:
#card(CARD_TYPE, CARD_COLOR_ID, CARD_NUMBER)
class card:
	def __init__(self, type, color="", number=""):
		self.type = type #N=Normal, W=Wild, S=Skip, R=Reverse, 2=+2, 4=+4
		self.color = color #0,1,2,3...
		self.number = number #0,1,2,3...
	
	#get 2 digit name of card (R5, BT, YR, etc.)
	def getName(self):
		name = "NONE"
		
		if self.type == "N":
			name = colorLetters[self.color]+str(self.number)
		elif self.type == "S":
			name = colorLetters[self.color]+"S"
		elif self.type == "R":
			name = colorLetters[self.color]+"R"
		elif self.type == "2":
			name = colorLetters[self.color]+"T"
		elif self.type == "4":
			name = "+4"
		elif self.type == "W":
			name = "WD"
		
		return name
	
	#get full name of card (red skip, blue 7, etc.)
	def getFullName(self, capitalize):
		name = "NONE"
		
		if self.type == "N":
			name = colors[self.color]+" "+str(self.number)
		elif self.type == "S":
			name = colors[self.color]+" skip"
		elif self.type == "R":
			name = colors[self.color]+" reverse"
		elif self.type == "2":
			name = colors[self.color]+" +2"
		elif self.type == "4":
			name = "+4"
		elif self.type == "W":
			name = "Wild"
		
		if capitalize: return name
		else: return name.lower()
	
	#check if cards are same
	def matches(self, cardCompare):
		if self.type == "N":
			return (cardCompare.type == "N" and self.color == cardCompare.color and self.number == cardCompare.number)
		elif self.type in ["S","R","2"]:
			return (cardCompare.type == self.type and self.color == cardCompare.color)
		elif self.type in ["W","4"]:
			return (self.type == cardCompare.type)

#====================================================================================
#=== MISC. FUNCTIONS ================================================================
#====================================================================================

#for debugging
def log(text):
	if debugText:
		input(text)

#set settings according to preset
def setSettingPreset(setting):
	global playerCount,deckCount,colorCount,turnLimit,jumpInLimit,specialCards,jumpIn,stacking,swaping,forcePlay,noBluffing,drawToMatch,challenge,startingCardCount,realPlayerCount,teamCount
	
	if setting == "classic":
		playerCount = 4
		deckCount = 1
		colorCount = 4
		turnLimit = 10
		jumpInLimit = 2
		specialCards = True
		jumpIn = False
		stacking = False
		swaping = False
		forcePlay = False
		noBluffing = False
		drawToMatch = False
		challenge = False
		startingCardCount = 7
		realPlayerCount = 1
		teamCount = 0
	elif setting == "modern":
		playerCount = 4
		deckCount = 1
		colorCount = 4
		turnLimit = 10
		jumpInLimit = 2
		specialCards = True
		jumpIn = True
		stacking = True
		swaping = True
		forcePlay = True
		noBluffing = False
		drawToMatch = True
		challenge = True
		startingCardCount = 7
		realPlayerCount = 1
		teamCount = 0

#get current time since last epoch in seconds
def getTime():
	return int(round(time.time()))

#play a sound to get the player's attention
#plays when: jump in is possible, someone wins, someone declares uno
def alert():
	if soundOn:
		print("\a")

#clears the screen
def clearScreen():
	os.system("cls")

#convert seconds into a printable time format (returns a string)
#example: formatTime(75) == "00:01:15"
def formatTime(sec):
	hour = 0
	min = 0
	while sec >= 60*60: hour += 1; sec -= 60*60
	while sec >= 60: min += 1; sec -= 60
	text = str(hour).rjust(2,"0")+":"+str(min).rjust(2,"0")+":"+str(sec).rjust(2,"0")
	return text

#calculate which player is next to go
#takes reverse turn order into consideration
def nextPlayer(amount=1):
	global playerTurn
	
	turn = playerTurn
	if reverseTurnOrder: turn -= amount
	else: turn += amount
	
	#adjust if it goes out of bounds
	while turn < 0: turn += playerCount
	while turn >= playerCount: turn -= playerCount
	
	log("Next turn amount: "+str(amount)+" to player "+str(turn+1))
	return turn

#advances the turn number by an amount of turns
def advanceTurn(amount=1):
	global playerTurn
	playerTurn = nextPlayer(amount)
	log("Advanced turn to player: "+str(playerTurn+1))

#prints text with a box around it
#curved - boolean value, makes the textbox have rounded corners
#text - array of strings to print, each array item is a new line
def printTextbox(curved, text):
	if text != [""] and text != []:
		textLength = len(max(text,key=len)) #length of longest string in text
		charFeed = ""
		
		#print top line
		if (curved): charFeed += "\u256D"
		else: charFeed += "\u250C"
		charFeed += ("\u2500"*textLength)
		if (curved): charFeed += "\u256E"
		else: charFeed += "\u2510"
		print(charFeed)
		
		#center text
		for i in text:
			charFeed = ""
			lineLength = len(i) #length of line text (excluding border)
			extraSpace = textLength-lineLength #how many spaces need to be added
			charFeed += "\u2502"
			charFeed += i
			charFeed += (" "*extraSpace)
			charFeed += "\u2502"
			print(charFeed)
		
		#print bottom line
		charFeed = ""
		if (curved): charFeed += "\u2570"
		else: charFeed += "\u2514"
		charFeed += ("\u2500"*textLength)
		if (curved): charFeed += "\u256F"
		else: charFeed += "\u2518"
		print(charFeed)
	#log("Printed textbox: "+("\n".join(text)))

#print main game interface
def printInterface(showCards=True,options=[]):
	teamsOn = (teamCount != 0)
	
	#top of interface (time, turn order, top of player textbox)
	text = []
	if teamsOn: text.append("Time: "+formatTime(getTime()-startTime)+"                Cards   Score         Last")
	else: text.append("Time: "+formatTime(getTime()-startTime)+"      Cards   Score         Last")
	turnOrderText = "DOWN"
	if reverseTurnOrder: turnOrderText = "UP"
	if teamsOn:
		text.append("Turn order: "+turnOrderText.ljust(4," ")+"              Left                  Action")
		text.append("            \u256D"+("\u2500"*5)+"\u252C"+("\u2500"*9)+"\u252C"+("\u2500"*7)+"\u252C"+("\u2500"*13)+"\u252C"+("\u2500"*(2+max(list(map(len,lastAction)))))+"\u256E")
	else:
		text.append("Turn order: "+turnOrderText.ljust(4," ")+"    Left                  Action")
		text.append("            \u256D"+("\u2500"*5)+"\u252C"+("\u2500"*7)+"\u252C"+("\u2500"*13)+"\u252C"+("\u2500"*(2+max(list(map(len,lastAction)))))+"\u256E")
	
	#player lines
	realPlayerNumber = 0
	for i in range(playerCount):
		charFeed = ""
		if i == playerTurn: charFeed = "> Player "
		else: charFeed = "  Player "
		charFeed += str(i+1).ljust(2," ")
		charFeed += " \u2502 "
		if playerType[i]:
			charFeed += ("P"+str(realPlayerNumber+1)).ljust(3," ")
			realPlayerNumber += 1
		else: charFeed += "CPU"
		if teamsOn:
			charFeed += " \u2502 Team "
			charFeed += str(teamAssignment[i]+1).ljust(2," ")
		charFeed += " \u2502 "
		charFeed += str(len(hand[i])).ljust(5," ")
		charFeed += " \u2502 "
		charFeed += str(score[i]).rjust(11," ")
		charFeed += " \u2502 "
		charFeed += lastAction[i].ljust(max([len(x) for x in lastAction]), " ")
		charFeed += " \u2502"
		text.append(charFeed)
	
	#bottom of player textbox
	if teamsOn: text.append("            \u2570"+("\u2500"*5)+"\u2534"+("\u2500"*9)+"\u2534"+("\u2500"*7)+"\u2534"+("\u2500"*13)+"\u2534"+("\u2500"*(2+max(list(map(len,lastAction)))))+"\u256F")
	else: text.append("            \u2570"+("\u2500"*5)+"\u2534"+("\u2500"*7)+"\u2534"+("\u2500"*13)+"\u2534"+("\u2500"*(2+max(list(map(len,lastAction)))))+"\u256F")
	text.append("")
	text.append("Current color: "+colors[colorInPlay])
	text.append("Card on pile: "+cardInPlay.getFullName(True))
	text.append("")
	text.append("Options:                        Card chart:")
	
	#show list of options available
	charFeed = ""
	for i in range(10):
		num = (i+1)%10
		if str(num) in options: charFeed += " "+str(num)+" "
		else: charFeed += "   "
	charFeed = charFeed[:-1] #trim off last space
	charFeed += " \u2502 Wild card = WD, +4 card = +4"
	text.append(charFeed)
	
	#start the bottom of the interface
	text.append("                              \u2502 Except for the 2 above, the first letter indicates color.")
	text.append(" U  D    "+("\u256D\u2500\u256E")*6+"   \u2502 E.g. Red = R, Blue = B, Green = G, Yellow = Y")
	
	#show top half of cards
	charFeed = " N  R  < "
	for i in range(6):
		if cardPage*6+i < len(hand[playerTurn]) and showCards: charFeed += "\u2502"+hand[playerTurn][cardPage*6+i].getName()[0]+"\u2502"
		else: charFeed += "\u2502 \u2502"
	charFeed += " > \u2502 And the second letter indicates number or special card type."
	text.append(charFeed)
	
	#show bottom half of cards
	charFeed = " O  A  < "
	for i in range(6):
		if cardPage*6+i < len(hand[playerTurn]) and showCards: charFeed += "\u2502"+hand[playerTurn][cardPage*6+i].getName()[1]+"\u2502"
		else: charFeed += "\u2502 \u2502"
	charFeed += " > \u2502 Skip = S, Reverse = R, +2 card = T"
	text.append(charFeed)
	
	text.append(" !  W    "+("\u2570\u2500\u256F")*6+"   \u2502 Examples: Red skip = RS, Blue 5 = B5, Green +2 = GT")
	
	printTextbox(False, text)
	printTextbox(False, message)
	
	#if debug, show all player's cards
	if showAllCards:
		text = ["Debug:"]
		for i in range(playerCount):
			charFeed = ""
			for j in hand[i]:
				charFeed += j.getName()+" "
			charFeed = charFeed[:-1]
			text.append("Player "+str(i+1)+": "+charFeed)
		printTextbox(False, text)

def refreshInterface():
	clearScreen()
	printInterface(False)
	time.sleep(messageWaitTime)

#====================================================================================
#=== CARD FUNCTIONS =================================================================
#====================================================================================

#whether or not the card you are trying to place can be placed
#returns a boolean value, true means it can be placed
def canPlaceCard(cardPlacing, cardPlaced=-1):
	global cardInPlay,colorInPlay
	
	if cardPlaced == -1:
		cardPlaced = cardInPlay
	
	if playerType[playerTurn] and canPlayAnyCard:
		return True
	else:
		if cardPlacing.type == "N":
			return ((cardPlacing.number == cardPlaced.number) or (cardPlacing.color == colorInPlay))
		elif cardPlacing.type in ["W","4"]:
			return True
		elif cardPlacing.type in ["S","R","2"]:
			return ((cardPlacing.type == cardPlaced.type) or (cardPlacing.color == colorInPlay))
		else:
			return False

#place a card and preforms the actions of that card
def placeCard(cardPlaced):
	global colorInPlay,message,reverseTurnOrder,playerTurn,cardInPlay,colorCount,previousCard
	
	gameEndExit = False
	log("Placing card: "+cardPlaced.getFullName(True))
	message.append("Player "+str(playerTurn+1)+" played a "+cardPlaced.getFullName(False))
	
	if cardPlaced.type == "N": #if number card
		score[playerTurn] += 1
		colorInPlay = cardPlaced.color
		if swaping:
			if cardPlaced.number == 0:
				#0 card swap (rotate hands)
				log("Hand switch (0)")
				message.append("Your hands have been switched.")
				tempHand = []
				if reverseTurnOrder:
					tempHand = hand[0].copy()
					for i in range(playerCount-1):
						hand[i] = hand[i+1].copy()
					hand[playerCount-1] = tempHand.copy()
				else:
					tempHand = hand[playerCount-1].copy()
					for i in reversed(range(playerCount-1)):
						hand[i+1] = hand[i].copy()
					hand[0] = tempHand.copy()
			elif cardPlaced.number == 7:
				#7 card swap (switch hands)
				swapPlayer = 0
				if playerType[playerTurn]:
					swapPlayer = askForSwapPlayer(playerTurn)
				else:
					swapPlayer = askAiForSwapPlayer(playerTurn)
				log("Hand switch (7) with player: "+str(swapPlayer+1))
				message.append("Player "+str(playerTurn+1)+" swapped cards with player "+str(swapPlayer+1)+".")
				tempHand = hand[playerTurn].copy()
				hand[playerTurn] = hand[swapPlayer].copy()
				hand[swapPlayer] = tempHand.copy()
		advanceTurn()
	elif cardPlaced.type == "S": #if skip
		score[playerTurn] += 2
		colorInPlay = cardPlaced.color
		advanceTurn(2) #skip next player
	elif cardPlaced.type == "R": #if reverse
		score[playerTurn] += 2
		colorInPlay = cardPlaced.color
		reverseTurnOrder = (not reverseTurnOrder) #reverse order
		advanceTurn()
	elif cardPlaced.type == "W": #if wild
		score[playerTurn] += 2
		if playerType[playerTurn]:
			colorInPlay = askForColor()
		else:
			colorInPlay = askAiForColor()
		log("New color: "+str(colorInPlay))
		advanceTurn()
	elif cardPlaced.type in ["2","4"]: #if +2 or +4
		if cardPlaced.type == "2":
			#if +2
			score[playerTurn] += 2
			colorInPlay = cardPlaced.color
		else:
			#if +4
			score[playerTurn] += 4
			if playerType[playerTurn]:
				colorInPlay = askForColor()
			else:
				colorInPlay = askAiForColor()
			log("New color: "+str(colorInPlay))
		
		#check to make sure everybody has at least 1 card
		#if not, abandon the rest of the function
		if len(hand[playerTurn]) == 0:
			gameEndExit = True
		
		drawValue = int(cardPlaced.type)
		plusCardCombo = drawValue
		stackingInProgress = True
		advanceTurn()
		
		#stacking handler
		orgPlayerTurn = playerTurn
		if stacking and not gameEndExit:
			while stackingInProgress and any([x.type == cardPlaced.type for x in hand[playerTurn]]) and not gameEndExit: #while the next player has a stackable card
				#this makes sure that if someone plays their last card, the game ends instead of continuing
				if min(list(map(len, hand))) == 0:
					gameEndExit = True
					continue
				
				log("Next player ("+str(playerTurn+1)+") can stack")
				ans = ""
				if playerType[playerTurn]: ans = askOption(True) #ask player
				else: ans = askAiOption(True) #ask ai
				
				if ans == "2":
					#stack refused
					stackingInProgress = False
				else:
					#stack success
					message.append("Player "+str(playerTurn+1)+" stacked.")
					plusCardCombo += int(cardInPlay.type)
					if cardInPlay.type == "4":
						if playerType[playerTurn]: colorInPlay = askForColor()
						else: colorInPlay = askAiForColor()
				
				if stackingInProgress:
					advanceTurn()
			log("Stacking ended")
		
		#challenge handler
		if challenge and cardPlaced.type == "4" and not gameEndExit:
			log("Requesting challenge")
			
			if playerType[playerTurn]: ans = askChallenge()
			else: ans = askAiChallenge()
			
			log("Challenge response: "+str(ans))
			
			if ans: #accept challenge
				colorAmount = sum([sum(y.type == x for y in hand[nextPlayer(-1)]) for x in range(colorCount)]) #how many color cards they have
				couldPlay = any([(canPlaceCard(x,previousCard) and (not x.type in ["W","4"])) for x in hand[nextPlayer(-1)]]) #could have played
				if couldPlay or (colorAmount == 0):
					log("Challenge fail")
					#challenge failiure
					drawCard(playerTurn, plusCardCombo+2)
					score[nextPlayer(-1)] += plusCardCombo//2
					message.append("The challenge failed!")
				else:
					log("Challenge success")
					#challenge success
					enemyId = nextPlayer(-1)
					enemyDraw = plusCardCombo//2
					playerDraw = plusCardCombo-enemyDraw
					drawCard(enemyId, enemyDraw)
					drawCard(playerTurn, playerDraw)
					score[playerTurn] += enemyDraw
					message.append("The challenge was successful!")
			else:
				drawCard(playerTurn, plusCardCombo) #no challenge. give cards normally
		else:
			drawCard(playerTurn, plusCardCombo) #normal draw
		
		advanceTurn()
	
	#jump-in handler
	if jumpIn and not gameEndExit:
		jumpInPossible = False
		jumpInPlayer = 0
		for i in range(playerCount):
			if any([cardInPlay.matches(x) for x in hand[i]]):
				jumpInPossible = True
				jumpInPlayer = i
		if jumpInPossible:
			log("Jump-in possible for player "+str(jumpInPlayer+1))
			ans = "-1"
			if playerType[jumpInPlayer]:
				ans = askJumpIn(jumpInPlayer)
			else:
				ans = askAiJumpIn(jumpInPlayer)
			log("Jump-in response: "+str(ans))
			if ans != "-1":
				alert()
				score[jumpInPlayer] += 1
				placedCard = hand[jumpInPlayer].pop(int(ans)) #remove card from hand
				deck.append(cardInPlay)
				previousCard = cardInPlay
				cardInPlay = placedCard
				playerTurn = jumpInPlayer
				if not len(hand[playerTurn]) == 0:
					placeCard(cardInPlay)

#sort a player's hand
#colors are sorted by color id, colorless cards come last
#then, cards are sorted by number, special cards are last in the order of reverse skip +2
#if sortByPlayability is true, it shows you your playable cards first
def sortCards(player):
	numberSort = list(map(str,range(10)))+["R","S","2"] #defines number/specialtype priority
	cardColors = [[] for _ in range(colorCount)] #an array of cards per color
	cardColorless = [] #for colorless cards
	sortedHand = [] #sorted hand
	
	#sort by color
	for i in hand[player]:
		if i.type in ["W","4"]:
			cardColorless.append(i)
		else:
			cardColors[i.color].append(i)
	
	for i in range(len(cardColors)): #for each color
		for j in range(len(numberSort)): #for each number and type
			if j > 9: #for type other than number
				while any(x.type == numberSort[j] for x in cardColors[i]): #while it exists in cardColors[i]
					ind = [ x.type for x in cardColors[i] ].index(numberSort[j]) #find its index
					sortedHand.append(cardColors[i][ind])
					cardColors[i].pop(ind)
			else: #for numbers
				while any(x.number == int(numberSort[j]) for x in cardColors[i]): #while it exists in cardColors[i]
					ind = [ x.number for x in cardColors[i] ].index(int(numberSort[j])) #find its index
					sortedHand.append(cardColors[i][ind])
					cardColors[i].pop(ind)
	
	#sort colorless cards
	while any(x.type == "W" for x in cardColorless):
		ind = [ x.type for x in cardColorless ].index("W")
		sortedHand.append(cardColorless[ind])
		cardColorless.pop(ind)
	while any(x.type == "4" for x in cardColorless):
		ind = [ x.type for x in cardColorless ].index("4")
		sortedHand.append(cardColorless[ind])
		cardColorless.pop(ind)
	
	#sort by playability if enabled
	if sortByPlayability:
		i = 0
		resortedValues = 0
		while i < len(sortedHand):
			if canPlaceCard(sortedHand[i]):
				sortedHand.insert(resortedValues, sortedHand.pop(i))
				resortedValues += 1
				i += 1
			else: i += 1
	
	#overwrite player hand with sorted hand
	for i in range(len(sortedHand)):
		hand[player][i] = sortedHand[i]

#have a player draw 1 or more cards
def drawCard(player, amount=1):
	global message,drawToMatch
	
	log("Player "+str(player+1)+" will draw "+str(amount)+" card(s)")
	
	cardsDrawn = 0
	cardsDrawnFromMatch = 0
	deckRanOut = False
	cardMatch = False
	
	#draw cards
	for i in range(amount):
		if len(deck) > 0:
			drawnCard = deck.pop(0)
			hand[player].append(drawnCard)
			if canPlaceCard(drawnCard):
				cardMatch = True
			cardsDrawn += 1
		else:
			deckRanOut = True
	
	#if draw to match and a playable card has not yet been drawn
	if drawToMatch and not cardMatch:
		while not cardMatch:
			if len(deck) > 0:
				drawnCard = deck.pop(0)
				hand[player].append(drawnCard)
				if canPlaceCard(drawnCard):
					cardMatch = True
				cardsDrawnFromMatch += 1
			else:
				deckRanOut = True
	
	if deckRanOut:
		log("Deck ran out. Drew "+str(cardsDrawn+cardsDrawnFromMatch)+" instead")
		message.append("Player "+str(player+1)+" drew "+str(cardsDrawn+cardsDrawnFromMatch)+" card(s), but the deck ran out of cards.")
	else:
		message.append("Player "+str(player+1)+" drew "+str(cardsDrawn+cardsDrawnFromMatch)+" card(s).")
	
	if len(hand[player]) > 1:
		calledUno[player] = False

#====================================================================================
#=== PLAYER ASK FUNCTIONS ===========================================================
#====================================================================================

#ask user for color
#returns color id
def askForColor():
	global message
	
	message = ["Choose a color.",""]
	for i in range(colorCount): message.append(str(i+1)+" - "+colors[i])
	ans = ""
	hasAns = False #if the player has the color requested
	firstLoop = True
	#ask for color (if no bluffing is on, it checks that too)
	colorAnsRange = list(map(str, range(1,colorCount+1))) #list of accepted answers: ["1", "2", "3", ... "colorCount"]
	while ( not ans in colorAnsRange ) and ( not hasAns ):
		hasAns = False
		clearScreen()
		if not firstLoop:
			printTextbox(False, unknownCommand)
		printInterface()
		ans = input()
		
		if ans in colorAnsRange:
			if noBluffing:
				#check if player has color
				hasAnyColor = False
				for j in hand[playerTurn]:
					if not j.type in ["W","4"]:
						hasAnyColor = True
						if j.color == int(ans)-1:
							hasAns = True
				#if player has only wilds or +4s, it allows the play
				if not hasAnyColor:
					hasAns = True
			else:
				hasAns = True
		firstLoop = False
	message = [""]
	return int(ans)-1

#ask for player id to swap hands with
#returns player id
def askForSwapPlayer(player):
	global message
	
	message = ["Choose a player to swap hands with:",""]
	for i in range(playerCount):
		if i != player: message.append(str(i+1)+" - Player "+str(i+1))
	ans = ""
	firstLoop = True
	acceptedAns = [str(x+1) for x in range(playerCount) if x != player]
	while not ans in acceptedAns:
		clearScreen()
		if not firstLoop:
			printTextbox(False, unknownCommand)
		printInterface()
		ans = input()
		firstLoop = False
	message = []
	return int(ans)-1

def askOption(stackingInProgress=False, jumpInChance=False, player=-1):
	global playerTurn,cardInPlay,cardPage,message,previousCard

	if player == -1: player = playerTurn
	jumpInKey = jumpInLetters[random.randint(0,len(jumpInLetters)-1)] #which key you need to press for jump in

	if stackingInProgress:
		message = ["You are able to stack a +2 or +4 card."]
	if jumpInChance:
		message = ["You can jump in! Enter ["+jumpInKey+"]!"]
	
	ans = ""
	turnStartTime = getTime()
	timerExit = False #triggered when time runs out
	jumpInExit = False #triggered when jump-in
	cardPage = 0
	
	while (not ans in ["2","4","5","6","7","8","9"]) and (not timerExit) and (not jumpInExit):
		ans = ""
		firstLoop = True
		
		#find out which options are available (bottom left of gui)
		acceptedOptions = []
		#if card count is 2 and you have a playable card, or a player did not call uno
		handLen2 = (len(hand[player]) == 2)
		handPlayable = any([canPlaceCard(i) for i in hand[player]])
		playerNoUno = any([((not calledUno[i]) and (len(hand[i])==1) and (not i == player)) for i in range(playerCount)]) #list comprehension for the win
		if (handLen2 and handPlayable) or playerNoUno: acceptedOptions.append("1")
		#check if you have to draw. if forcePlay is off, the option is enabled anyways
		if not jumpInChance:
			if not (forcePlay and (any([canPlaceCard(i) for i in hand[player]]))):
				acceptedOptions.append("2")
			if cardPage > 0: acceptedOptions.append("3")
			if (cardPage+1)*6 < len(hand[player]): acceptedOptions.append("0")
			for i in range(6): #for each card option
				if cardPage*6+i < len(hand[player]): #make sure the option has a card associated with it
					if canPlaceCard(hand[player][cardPage*6+i]): #make sure you can play the card
						if (not stackingInProgress) or (hand[player][cardPage*6+i].type == cardInPlay.type): #if stacking, it must match card type
							acceptedOptions.append(str(i+4))
		
		if jumpInChance:
			acceptedOptions.append(jumpInKey)
			acceptedOptions.append(jumpInKey.lower())
		
		#ask for action until a valid one is used
		while not ans in acceptedOptions:
			clearScreen()
			if not firstLoop:
				printTextbox(False, unknownCommand)
			printInterface(True,acceptedOptions)
			
			ans = input()
			firstLoop = False
		turnTime = (getTime()-turnStartTime) #time it took to choose a valid option
		
		#options:
		#1 uno, 2 draw, 3 <, 0 >, 4-9 card 1-6
		#from here on out it is assumed that the option they have selected is perfectly valid
		#the code before the while loop above already does that so no more error checking needs to be done
		
		timeLimit = turnLimit
		if jumpInChance: timeLimit = jumpInLimit
		
		if (turnTime < timeLimit) or (not timed):
			if ans == "1": #if calling uno
				message = []
				alert()
				if playerNoUno: #if a player was caught not calling uno
					noUnoList = [((not calledUno[i]) and (len(hand[i])==1) and (not i == player)) for i in range(playerCount)] #list of players that did not call uno
					for i in range(len(noUnoList)):
						if noUnoList[i]:
							message.append("Player "+str(player+1)+" caught player "+str(i+1)+" not calling UNO!")
							drawCard(i,2)
							calledUno[i] = True
				if handLen2 and handPlayable:
					message.append("Player "+str(player+1)+" called UNO!")
					calledUno[player] = True
			elif ans == "2": #if drawing
				if not stackingInProgress:
					drawCard(player)
					advanceTurn()
			elif ans == "3": cardPage -= 1 #card page left
			elif ans == "0": cardPage += 1 #card page right
			elif ans in ["4","5","6","7","8","9"]: #if card option
				if not jumpInChance:
					placedCard = hand[player].pop(cardPage*6+(int(ans)-4)) #remove card from hand
					deck.append(cardInPlay)
					previousCard = cardInPlay
					cardInPlay = placedCard
					lastAction[player] = "Played a "+placedCard.getFullName(False)+"."
					if not stackingInProgress:
						placeCard(placedCard)
			elif (ans == jumpInKey) or (ans == jumpInKey.lower()): #if jumping in
				ans = str([x.matches(cardInPlay) for x in hand[player]].index(True))
				jumpInExit = True
			else: pass
		else:
			#turn took too long
			timerExit = True
			if not jumpInChance:
				message = ["You ran out of time for your turn."]
			else:
				message = ["Jump in unsuccessful."]
			if (not stackingInProgress) and (not jumpInChance):
				drawCard(player)
				advanceTurn()
			if jumpInChance: ans = "-1"
			else: ans = "2"
	
	return ans

#ask player if it will challenge
def askChallenge():
	global message
	
	message = ["You are being hit with a +4.","Would you like to challenge it?","","1 - Yes","2 - No"]
	ans = ""
	firstLoop = True
	
	while not ans in ["1","2"]:
		clearScreen()
		if not firstLoop:
			printTextbox(False, unknownCommand)
		printInterface()
		ans = input()
	
	message = []
	return (ans == "1")

def askJumpIn(player):
	ans = askOption(False, True, player)
	return ans

#====================================================================================
#=== AI ASK FUNCTIONS ===============================================================
#====================================================================================

def askAiForColor():
	global playerTurn,colorCount
	
	#how many of each color the ai has has
	colorAmounts = [sum([y.color == x for y in hand[playerTurn]]) for x in range(colorCount)]
	
	#return the color that they have the most of
	color = colorAmounts.index(max(colorAmounts))
	log("AI color response: "+str(color))
	return color

def askAiForSwapPlayer(player):
	minCards = -1
	minPlayer = -1
	
	#choose the player with the least amount of cards
	for i in range(playerCount):
		if i != player:
			if len(hand[i]) < minCards or minCards == -1:
				minCards = len(hand[i])
				minPlayer = i
	return minPlayer

def askAiOption(stackingInProgress=False):
	global playerTurn,cardInPlay,cardPage,previousCard
	
	player = playerTurn
	
	ans = ""
	cardPage = 0
	
	canPlay = any([canPlaceCard(i) for i in hand[player]])
	canCallUno = (len(hand[player]) == 2) and canPlay
	canReportUno = any([((not calledUno[i]) and (len(hand[i])==1) and (not i == player)) for i in range(playerCount)])
	
	clearScreen()
	printInterface(False)
	time.sleep(messageWaitTime)
	
	message = []
	if canReportUno and (random.randrange(100) < unoReportRate): #if the ai can and remembers to report uno
		alert()
		noUnoList = [((not calledUno[i]) and (len(hand[i])==1) and (not i == player)) for i in range(playerCount)] #list of players that did not call uno
		for i in range(len(noUnoList)):
			if noUnoList[i]:
				log("AI caught player "+str(player+1)+" not calling UNO")
				message.append("Player "+str(player+1)+" caught player "+str(i+1)+" not calling UNO!")
				drawCard(i,2)
				calledUno[i] = True
	if canCallUno and (random.randrange(100) < unoCallRate): #if the ai can and remembers to call uno
		log("AI called UNO")
		alert()
		message.append("Player "+str(player+1)+" called UNO!")
		calledUno[player] = True
	
	#if stacking
	if stackingInProgress:
		stackableCards = [x for x in range(len(hand[player])) if (hand[player][x].type == cardInPlay.type)]
		if len(stackableCards) > 0:
			cardStacking = stackableCards[random.randint(0,len(stackableCards)-1)]
			cardPage = cardStacking//6
			ans = str((cardStacking%6)+4)
			placedCard = hand[player].pop(cardPage*6+(int(ans)-4)) #remove card from hand
			deck.append(cardInPlay)
			previousCard = cardInPlay
			cardInPlay = placedCard
			lastAction[player] = "Played a "+placedCard.getFullName(False)+"."
		else:
			ans = "2"
	else: #if not stacking
		if canPlay:
			playableCards = []
			for i in range(len(hand[player])):
				if canPlaceCard(hand[player][i]):
					playableCards.append(i)
			cardChosen = playableCards[random.randint(0,len(playableCards)-1)] #choose random card to play
			cardPage = cardChosen//6
			ans = str((cardChosen%6)+4)
			placedCard = hand[player].pop(cardPage*6+(int(ans)-4)) #remove card from hand
			deck.append(cardInPlay)
			previousCard = cardInPlay
			cardInPlay = placedCard
			lastAction[player] = "Played a "+placedCard.getFullName(False)+"."
			placeCard(placedCard)
		else:
			ans = "2"
			drawCard(player)
			advanceTurn()
	return ans

def askAiChallenge():
	#the chances of the ai choosing to challenge depends on card count
	#more cards means a greater chance of challenging
	#however, if the player has very few cards, it is more likely to challenge
	
	#ceil(5*(sin((pi/2)*sqrt(x/4))^8)+1), if x < 16
	#1, if x >= 16
	#where x is the number of cards
	
	challengeValue = 0
	cardCount = len(hand[nextPlayer(-1)])
	if cardCount >= 16: challengeValue = 1
	else: challengeValue = math.ceil(5*(math.sin((pi/2)*((cardCount/4)**(1/2)))**8)+1)
	return (random.randint(0,challengeValue) == 1)

def askAiJumpIn(player):
	global cardInPlay
	
	#ai always jumps in
	for i in range(len(hand[player])):
		if cardInPlay.matches(hand[player][i]):
			return str(i)
	return "-1"

#====================================================================================
#=== PROGRAM START ==================================================================
#====================================================================================

setSettingPreset("classic")

while True:
	#welcome screen
	ans = ""
	while not ans in ["1","2","3","4"]:
		clearScreen()
		printTextbox(False, ["For instructions on how to play, refer to manual.odt"])
		printTextbox(False, welcomeText)
		ans = input()

	clearScreen()
	if ans == "1":
		setSettingPreset("classic")
	elif ans == "2":
		setSettingPreset("modern")
	elif ans == "3":
		#custom settings menu
		ans = ""
		com = "" #current command (val, done, info, unknown, etc.)
		comArg = "" #command argument (01, 02, 03, etc.)
		while not ans in ["Done","done","\"Done\"","\"done\""]:
			currentValGap = 16 #how much to ljust current values
			settingsText = [
			"Custom settings",
			"Type the setting number, then the setting you want to set it to",
			"Type the setting number by itself to set it to its default value",
			"if you want to know more about a setting, type its number, and then \"Info\"",
			"When you're done, type \"Done\".",
			"",
			"     Setting              Current value   Acceptable values",
			"01 - Player count         "+str(playerCount).ljust(currentValGap," ")+"2 - 16",
			"02 - Deck count           "+str(deckCount).ljust(currentValGap," ")+"1 - 8",
			"03 - Color count          "+str(colorCount).ljust(currentValGap," ")+"2 - 8",
			"04 - Turn time limit      "+str(turnLimit).ljust(currentValGap," ")+"1 - 600 (seconds)",
			"05 - Jump-in time limit   "+str(jumpInLimit).ljust(currentValGap," ")+"1 - 10  (seconds)",
			"06 - Special cards        "+str(specialCards).ljust(currentValGap," ")+"True/False",
			"07 - Jump-in              "+str(jumpIn).ljust(currentValGap," ")+"True/False",
			"08 - Stacking             "+str(stacking).ljust(currentValGap," ")+"True/False",
			"09 - 0/7 swaping          "+str(swaping).ljust(currentValGap," ")+"True/False",
			"10 - Force play           "+str(forcePlay).ljust(currentValGap," ")+"True/False",
			"11 - No bluffing          "+str(noBluffing).ljust(currentValGap," ")+"True/False",
			"12 - Draw to match        "+str(drawToMatch).ljust(currentValGap," ")+"True/False",
			"13 - Challenge            "+str(challenge).ljust(currentValGap," ")+"True/False",
			"14 - Starting card count  "+str(startingCardCount).ljust(currentValGap," ")+"1 - 30",
			"15 - Real player count    "+str(realPlayerCount).ljust(currentValGap," ")+"0 - "+str(playerCount),
			"16 - Team count           "+str(teamCount).ljust(currentValGap," ")+"0 - "+str(playerCount)
			]
			
			if com == "unknown":
				printTextbox(False, unknownCommand)
			elif com == "info":
				printTextbox(False, commandInfo[comArg-1])
			printTextbox(False, settingsText)
			ans = input()
			
			com = ""
			comArg = ""
			
			#find out what command is being executed
			if len(ans) == 2:
				if ans[0] in numsAndSpace and ans[1] in nums:
					comArg = int(ans)
				com = "default"
			elif len(ans) == 1:
				if ans[0] in nums:
					comArg = int(ans)
				com = "default"
			elif len(ans) > 2:
				if ans[0] in numsAndSpace and ans[1] in nums:
					comArg = int(ans[:2])
					ans = ans[2:]
				
				com = ans.replace(" ", "")
				if com in ["Info","info","\"Info\"","\"info\""]: com = "info"
				elif com in valueYes: com = "True"
				elif com in valueNo: com = "False"
				else: #check if entering a value
					validVal = True
					for i in com:
						if not i in nums:
							validVal = False
					if validVal == True:
						com = int(com)
					else:
						com = "unknown"
			
			#make sure the command argument is valid
			if comArg != "":
				if comArg < 1 or comArg > 16:
					com = "unknown"
					comArg = ""
			
			#execute command
			if com == "default":
				if comArg == 1: playerCount = 4
				elif comArg == 2: deckCount = 1
				elif comArg == 3: colorCount = 4
				elif comArg == 4: turnLimit = 10
				elif comArg == 5: jumpInLimit = 2
				elif comArg == 6: specialCards = True
				elif comArg == 7: jumpIn = False
				elif comArg == 8: stacking = False
				elif comArg == 9: swaping = False
				elif comArg == 10: forcePlay = False
				elif comArg == 11: noBluffing = False
				elif comArg == 12: drawToMatch = False
				elif comArg == 13: challenge = False
				elif comArg == 14: startingCardCount = 7
				elif comArg == 15: realPlayerCount = 1
				elif comArg == 16: teamCount = 0
			elif not com in ["","info","unknown"]:
				if comArg == 1:
					if int(com) >= 2 and int(com) <= 18: playerCount = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 2:
					if int(com) >= 1 and int(com) <= 8: deckCount = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 3:
					if int(com) >= 2 and int(com) <= 8: colorCount = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 4:
					if int(com) >= 1 and int(com) <= 600: turnLimit = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 5:
					if int(com) >= 1 and int(com) <= 10: jumpInLimit = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 6:
					if com == "True": specialCards = True
					elif com == "False": specialCards = False
					else: com = "unknown"; comArg = ""
				elif comArg == 7:
					if com == "True": jumpIn = True
					elif com == "False": jumpIn = False
					else: com = "unknown"; comArg = ""
				elif comArg == 8:
					if com == "True": stacking = True
					elif com == "False": stacking = False
					else: com = "unknown"; comArg = ""
				elif comArg == 9:
					if com == "True": swaping = True
					elif com == "False": swaping = False
					else: com = "unknown"; comArg = ""
				elif comArg == 10:
					if com == "True": forcePlay = True
					elif com == "False": forcePlay = False
					else: com = "unknown"; comArg = ""
				elif comArg == 11:
					if com == "True": noBluffing = True
					elif com == "False": noBluffing = False
					else: com = "unknown"; comArg = ""
				elif comArg == 12:
					if com == "True": drawToMatch = True
					elif com == "False": drawToMatch = False
					else: com = "unknown"; comArg = ""
				elif comArg == 13:
					if com == "True": challenge = True
					elif com == "False": challenge = False
					else: com = "unknown"; comArg = ""
				elif comArg == 14:
					if int(com) >= 1 and int(com) <= 30: startingCardCount = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 15:
					if int(com) >= 0 and int(com) <= playerCount: realPlayerCount = int(com)
					else: com = "unknown"; comArg = ""
				elif comArg == 16:
					if int(com) >= 0 and int(com) <= playerCount: teamCount = int(com)
					else: com = "unknown"; comArg = ""
			
			if realPlayerCount > playerCount:
				realPlayerCount = playerCount
			if teamCount > playerCount:
				teamCount = playerCount
			
			clearScreen()
	else:
		#if option 4 is chosen
		sys.exit(0)

	#====================================================================================
	#=== INITIALIZE GAME ================================================================
	#====================================================================================

	#generate cards
	cardQ = []
	for i in range(deckCount):
		for j in range(colorCount):
			for k in range(9): #add 2 of each number
				cardQ.append(card("N",j,k+1))
				cardQ.append(card("N",j,k+1))
			cardQ.append(card("N",j,0)) #add 0
			if specialCards:
				cardQ.append(card("S",j)) #add skips
				cardQ.append(card("S",j))
				cardQ.append(card("R",j)) #add reverses
				cardQ.append(card("R",j))
				cardQ.append(card("2",j)) #add +2s
				cardQ.append(card("2",j))
		if specialCards:
			for j in range(4): cardQ.append(card("W")) #add wilds
			for j in range(4): cardQ.append(card("4")) #add +4s

	#randomly add cards to deck
	for i in range(len(cardQ)):
		cardNum = random.randint(0,len(cardQ)-1)
		deck.append(cardQ[cardNum])
		cardQ.pop(cardNum)

	#give cards to players
	hand = [[] for _ in range(playerCount)]
	for i in range(startingCardCount):
		for j in range(playerCount):
			#make sure there is at least 1 card left to put down first card
			if len(deck) > 1:
				hand[j].append(deck[0])
				deck.pop(0)

	#if debug card set is on, give 1 of each color +2 and a +4
	if debugCardHand:
		for i in range(playerCount):
			if len(hand[i]) > colorCount:
				hand[i][0] = card("4")
				for j in range(colorCount):
					hand[i][j+1] = card("2",j)
			#for j in range(len(hand[i])):
			#	hand[i][j] = card("4")

	#init other stuff
	score = [0]*playerCount
	lastAction = [""]*playerCount
	calledUno = [False]*playerCount
	startTime = getTime()
	sessionTime = 0
	turnStartTime = 0
	playerTurn = random.randint(0,playerCount-1)
	cardPage = 0

	#figure out which players are cpus
	playerType = [False]*playerCount
	for i in range(realPlayerCount):
		cpuPlayerList = [x for x in range(playerCount) if not playerType[x]]
		playerType[cpuPlayerList[random.randint(0,len(cpuPlayerList)-1)]] = True

	#do team assignment
	teamAssignment = [-1]*playerCount
	playersNotAssigned = playerCount
	teamsNotAssigned = teamCount
	while teamsNotAssigned > 0:
		playersInTeam = 0
		if teamsNotAssigned == 1: playersInTeam = playersNotAssigned
		else: playersInTeam = playersNotAssigned//teamsNotAssigned
		
		for i in range(playersInTeam):
			teamlessPlayerList = [x for x in range(playerCount) if teamAssignment[x] == -1]
			teamAssignment[teamlessPlayerList[random.randint(0,len(teamlessPlayerList)-1)]] = teamCount-teamsNotAssigned
			playersNotAssigned -= 1
		teamsNotAssigned -= 1

	#put down first card
	cardInPlay = deck[0]
	deck.pop(0)
	
	clearScreen()
	printInterface(False)
	time.sleep(messageWaitTime)
	
	placeCard(cardInPlay)

	#hand[0][0] = card("N",0,7) #DEBUG

	#====================================================================================
	#=== START GAME =====================================================================
	#====================================================================================

	#main loop
	try:
		while min(list(map(len, hand))) > 0: #while everyone has at least 1 card
			log("Player "+str(playerTurn+1)+" begin")
			message = []
			for i in range(playerCount):
				sortCards(i)
			if playerType[playerTurn]: #if the current turn is of a player instead of an ai
				if realPlayerCount > 1:
					#if there are multiple real players, announce that it is this player's turn
					#this makes sure other players have time to look away so that they don't look at this player's hand
					clearScreen()
					printTextbox(False, ["Player "+str(playerTurn+1)+" start!"])
					time.sleep(messageWaitTime)
				askOption()
				refreshInterface()
			else:
				askAiOption()
				refreshInterface()
	except Exception:
		clearScreen()
		print("Uh oh! There seems to have been an error!\n")
		print(traceback.format_exc()) #show error
		input() #i don't use an ide that has a built-in terminal, so if i don't put this here it only shows me the error for a nanosecond
		sys.exit(-1)

	#====================================================================================
	#=== POST-GAME ======================================================================
	#====================================================================================

	clearScreen()

	#figure out who won
	winner = 0
	for i in range(playerCount):
		if len(hand[i]) == 0:
			winner = i

	if teamCount == 0: printTextbox(False, ["Player "+str(winner+1)+" wins!","","Total game time: "+formatTime(getTime()-startTime)])
	else: printTextbox(False, ["Team "+str(teamAssignment[winner]+1)+" wins!","","Total game time: "+formatTime(getTime()-startTime)])

	#print stats for each player
	cardLimit = 10
	statText = []
	if teamCount == 0: #if teams are not enabled
		statText.append("\u250C"+("\u2500"*12)+"\u252C"+("\u2500"*20)+"\u252C"+("\u2500"*(13+3*cardLimit))+"\u2510")
		for i in range(playerCount):
			playerStats = "\u2502 Player: "+(str(i+1).rjust(2," "))+" \u2502 "
			playerStats += "Score: "+(str(score[i]).rjust(11," "))+" \u2502 Cards left: "
			if len(hand[i]) > cardLimit:
				for j in range(cardLimit-1):
					playerStats += hand[i][j].getName()+" "
				playerStats += "..."
			else:
				for j in range(cardLimit):
					if j < len(hand[i]): playerStats += hand[i][j].getName()+" "
					else: playerStats += "   "
			playerStats += "\u2502"
			statText.append(playerStats)
		statText.append("\u2514"+("\u2500"*12)+"\u2534"+("\u2500"*20)+"\u2534"+("\u2500"*(13+3*cardLimit))+"\u2518")
		for i in statText: print(i)
	else: #if teams are enabled
		for i in range(teamCount):
			statText = []
			
			statText.append("\u250C"+("\u2500"*77)+"\u2510")
			statText.append("\u2502 TEAM "+str(i+1).ljust(2," ")+(" "*69)+"\u2502")
			statText.append("\u251C"+("\u2500"*12)+"\u252C"+("\u2500"*20)+"\u252C"+("\u2500"*43)+"\u2524")
			
			for j in range(len(teamAssignment)):
				if teamAssignment[j] == i:
					#i is team number
					#j is player number
					playerStats = "\u2502 Player: "+(str(j+1).rjust(2," "))+" \u2502 "
					playerStats += "Score: "+(str(score[j]).rjust(11," "))+" \u2502 Cards left: "
					if len(hand[j]) > cardLimit:
						for k in range(cardLimit-1):
							playerStats += hand[j][k].getName()+" "
						playerStats += "..."
					else:
						for k in range(cardLimit):
							if k < len(hand[j]): playerStats += hand[j][k].getName()+" "
							else: playerStats += "   "
					playerStats += "\u2502"
					statText.append(playerStats)
			
			statText.append("\u2514"+("\u2500"*12)+"\u2534"+("\u2500"*20)+"\u2534"+("\u2500"*(13+3*cardLimit))+"\u2518")
			for i in statText: print(i)
	
	alert()
	input()