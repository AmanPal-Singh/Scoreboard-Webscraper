"""
Aman Singh
NBA Command Line App
"""

from bs4 import BeautifulSoup
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
import time


def get_league():
	""" Get the league that the user seeks to look at """
	print ("What league would you like to see? \n 1. NBA")
	try:
		select = int(input())
		return select
	except:
		return ""

def cleanup(lst):	
	""" This function turns strings to UTF-8 as some strings appear as u'STR' """
	return [(x.encode("UTF-8")) for x in lst]


def show_games(lst):
	""" Prints all the games shown on the ESPN Scoreboard """
	print "Here are the games: \n"

	#For the amount of games today,
	for x in range(len(all_lists_cleaned[8])):
		#If the score is not avaliable, print without score.
		if home_teams_scores[x] == "NO SCORE":
			print(str(x+1) + ". {} ({}) vs {} ({}) {} \n".format(all_lists_cleaned[4][x], all_lists_cleaned[6][x], all_lists_cleaned[0][x], all_lists_cleaned[2][x], all_lists_cleaned[8][x]))
		#Otherwise, print with score
		else:
			print(str(x+1) + ". {} ({}) vs {} ({}) {} {} - {} \n".format(all_lists_cleaned[4][x], all_lists_cleaned[6][x], all_lists_cleaned[0][x], all_lists_cleaned[2][x], all_lists_cleaned[8][x], all_lists_cleaned[7][x], all_lists_cleaned[3][x]))


def get_selection():
	try:
		print("Please select a game by entering one of the game numbers")
		select = int(input())
		return select
	except:
		return ""

def show_selection(x):
	""" This outputs the selection details given x, the selection number """
	x = x - 1
	print("Selection: {} ({}) vs {} ({}) {} \n".format(all_lists_cleaned[4][x], all_lists_cleaned[6][x], all_lists_cleaned[0][x], all_lists_cleaned[2][x], all_lists_cleaned[8][x]))



def remove_newlines(x):
	""" This removes whitespace from all elements of list x"""
	new_lst = []
	for element in x:
		new_lst.append(" ".join(element.split()))
	return new_lst

links_dictionary = {
	1: 'https://www.espn.com/nba/scoreboard'
}

#Get scoreboard page source code
CHROMEDRIVER_PATH = '/Users/amansingh/Desktop/chromedriver'
chrome_options = Options()
chrome_options.add_argument("--headless")

league_selection = get_league()
browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
browser.get(links_dictionary.get(league_selection))  
page = browser.page_source  
browser.quit()

#Make a soup object using lxml parser
soup = BeautifulSoup(page, 'lxml')

#In the source code, all game data is contained within <article class_= "scoreboard ..."></article>
#so we will find all components with such stuff
games = soup.find_all("article", class_= "scoreboard")

#Initalizing lists
home_teams = []
home_teams_abbrev = []
home_teams_record = []
home_teams_scores = []
away_teams = []
away_teams_abbrev = []
away_teams_record = []
away_teams_scores = []
status_list = []
current_scores = []
gameids = []

#If there are no components, then the game is empty today
if not games:
	print "There are no games today!"
else:
	#For every game, do the following:
	for game in games:

		#Get the pair of teams as a list containing away and home,
		team_pair = game.find_all('span', attrs={'class': "sb-team-short"})
		home_teams.append(team_pair[1].text)
		away_teams.append(team_pair[0].text)
		team_abbrev_pair = game.find_all('span', attrs={'class': "sb-team-abbrev"})
		home_teams_abbrev.append(team_abbrev_pair[1].text)
		away_teams_abbrev.append(team_abbrev_pair[0].text)

		#Get the pair of team records as a list containing away and home
		record_pair = game.find_all('p', attrs={'class': "record overall"})
		home_teams_record.append(record_pair[1].text)
		away_teams_record.append(record_pair[0].text)

		#Because the sourcecode changes based on if a game is live/finsihed vs has yet to occur
		#we have a try except code below to handle the status of a game (end, live, tipoff time)
		try:
			status = game.find_all('span', attrs={'class': "time"})
			status_list.append(status[0].text)
		except: 
			status = game.find_all('th', attrs={'class': "date-time"})
			status_list.append(status[0].text)

		#In order to get the boxscore and other info, we need to go the to the gamepage for that game. 
		#This requires opening a new link that contains the gameid
		gameid = game.get('id')
		gameids.append(gameid)

		#If a game has yet to happen, this tag does not exist so it returns an empty list.
		#Since the list is empty we will append a string that we can use later to know if a 
		#game has no score avaliable. Otherwise we will append the two scores avaliable
		score_pair = game.find_all('td', attrs={'class': "total"})
		if not score_pair:
			home_teams_scores.append("NO SCORE")
			away_teams_scores.append("NO SCORE")
		else:
			home_teams_scores.append(score_pair[1].text)
			away_teams_scores.append(score_pair[0].text)
	

all_lists = [home_teams, home_teams_abbrev, home_teams_record, home_teams_scores, away_teams, away_teams_abbrev, away_teams_record, away_teams_scores, status_list, gameids]	
all_lists_cleaned = []
for lst in all_lists:
	all_lists_cleaned.append(cleanup(lst))

show_games(all_lists_cleaned)

#Get the selection for the game to get more detail about
#If the selection is not of type integer, or out of bounds of the number of games today, get another selection
selection = get_selection()
while not(isinstance(selection, int)) or selection < 1 or selection > len(all_lists_cleaned[8]):
	print ("Your selection is not valid, please try again: ")
	selection = get_selection()

#This gets additional details about a game, by going to the gamecast link and boxscore link using the gameID
browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
browser.get('http://www.espn.com/nba/game?gameId=' + all_lists_cleaned[9][selection-1])  
page = browser.page_source  
soup2 = BeautifulSoup(page, 'lxml')
browser.get('http://www.espn.com/nba/boxscore?gameId=' + all_lists_cleaned[9][selection-1])  
page = browser.page_source  
soup3 = BeautifulSoup(page, 'lxml')
browser.quit()

#Show the game chosen
show_selection(selection)

#If the selection
if home_teams_scores[selection-1] == "NO SCORE":
	print "What would you like to do \n 1. View boxscore \n 2. View matchup predictor \n 3. View injury report"
	selection_view = get_selection()
	while not(isinstance(selection_view, int)) or selection_view < 1 or selection_view > 3:
		print ("Your selection is not valid, please try again: ")
		selection_view = get_selection()
else:
	print ("What would you like to do \n 1. View boxscore")
	selection_view = get_selection() + 3
	while not(isinstance(selection_view, int)) or selection_view < 4 or selection_view > 7:
		print ("Your selection is not valid, please try again: ")
		selection_view = get_selection() + 3

if selection_view == 1:
	print ("No boxscore avaliable.")
elif selection_view == 2:
	temp_value = soup2.find("span", attrs={'class': 'value-home'})
	home_value = temp_value.text
	temp_value = soup2.find("span", attrs={'class': 'value-away'})
	away_value = temp_value.text
	temp_value = soup2.find_all("span", attrs={'class': 'abbrev'})
	home_team = temp_value[1].text
	away_team = temp_value[0].text
	print ("According to ESPN's Basketball Power Index, {} has a {} chance of winning and {} has a {} chance of winning".format(away_team, away_value, home_team, home_value))
elif selection_view == 3:
	temp_value = soup2.find_all("table")
	print ("INJURY REPORT \n")	
	print (temp_value[0].find("caption")).text
	players = temp_value[0].find_all("td", attrs={"class": "name"})
	for player in players:
		print player.text
	print (temp_value[1].find("caption")).text
	players = temp_value[1].find_all("td", attrs={"class": "name"})
	for player in players:
		print player.text



"""
elif selection_view == 4:
	temp_value = soup3.find_all("table", attrs={"class": "mod-data"})
	temp_value1 = temp_value[0].find_all("tr")
	player_list = []
	for value in temp_value1:
		player_list.append(value.text)
	player_list = cleanup(player_list)
	print player_list
	player_list = remove_newlines(player_list)
	print player_list
"""








