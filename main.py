from sqlite3.dbapi2 import connect
import requests
from langdetect import detect
import time
import sqlite3
import json
from bs4 import BeautifulSoup

connection = sqlite3.connect('questTranslation.db')
cur = connection.cursor()

with open('quest_IDs.json', 'r') as quest_id_list:
  quest_ids = quest_id_list.read()


ids = json.loads(quest_ids)
url =  'https://classic.wowhead.com/quest='

# Add variables in place of the name and line break
def formatQuestText(quest: str, language: str):
  quest = quest.replace('<name>', '$N')
  quest = quest.replace('<Name>', '$N')
  quest = quest.replace('. ', '.')
  quest = quest.replace('.', '. ')
  quest = quest.replace(' $B', ' $B')
 
  if language.lower() == 'english':
    quest = quest.replace('<class>', '$C')
    quest = quest.replace('<race>', '$R')
  elif language.lower() == 'german':
    quest = quest.replace('<Klasse>', '$C')
    quest = quest.replace('<Volk>', '$R')
  elif language.lower() == 'french':
    quest = quest.replace('<classe>', '$C')
    quest = quest.replace('<nom>', '$N' )
    quest = quest.replace('<race>', '$R')
  return quest

# Replace the classname in the wowhead text into the $C variable the game can use
# def replaceClassName(text, language):
#   if language.lower() == 'english':
#     classList = {'druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior'}
#   elif language.lower() == 'german':
#     classList = {'druide','jäger','magier','paladin','priester','schurke','schamane','hexenmeister','krieger'}
#   splitText = text.split()
#   for index, x in enumerate(splitText):
#     if x.lower() in classList:
#       splitText[index] = '$C'
#   return(' '.join(splitText))

def getQuest(questID: str, language: str):
  progress_text = ''
  completion_text = ''
  language = language.lower()
  if language == 'english':
    url =  'https://classic.wowhead.com/quest='
  elif language == 'german':
    url = 'https://de.classic.wowhead.com/quest='
  elif language == 'french':
    url = 'https://fr.classic.wowhead.com/quest='

  response = requests.get(url + questID)
  soup = BeautifulSoup(response.text, 'lxml')
  try:
    progress_text_raw =  BeautifulSoup(str(soup.select('div[id="lknlksndgg-progress"]')[0]).replace('<br/>', '$B '), 'lxml').get_text()
    if detect(progress_text_raw) != 'en':
      progress_text = formatQuestText(progress_text_raw, language)
  except Exception as e:
    pass
  try:
    completion_text_raw = BeautifulSoup(str(soup.select('div[id="lknlksndgg-completion"]')[0]).replace('<br/>', '$B '), 'lxml').get_text()
    if detect(completion_text_raw) != 'en':
      completion_text = formatQuestText(completion_text_raw, language)
  except Exception as e:
    pass
  return {'progressText': progress_text, 'completionText': completion_text}

for x in ids['quest_ids']:
  questID = str(x['entry'])
  time.sleep(4)
  questReturn = getQuest(questID, 'french')
  print(questID)
  print(questReturn['progressText'])
  print(questReturn['completionText'])
  print("-------------------------------------------------------------------------------------------------------------------------------")
  try: 
    cur.execute("UPDATE locales_quest SET RequestItemsText_loc2 = ?, OfferRewardText_loc2 = ? where questID = ?", (questReturn['progressText'],questReturn['completionText'], questID))
  except Exception as e:
    print (e)
    pass
  # cur.execute("INSERT INTO locales_quest (questID,RequestItemsText_loc2,OfferRewardText_loc2) VALUES(?,?,?)", (questID, questReturn['progressText'], questReturn['completionText']))
  # cur.execute("UPDATE locales_quest SET RequestItemsText_loc3 = ?, OfferRewardText_loc3 = ? where questID = ?", (questReturn['progressText'],questReturn['completionText'], questID))
  connection.commit()
connection.commit()
connection.close()

## OfferRewardText = Completion
## RequestItemsText = Progress


## French = loc2
## German = loc3