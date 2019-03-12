from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from os import environ
from load_data import load_data, format_menu, get_indv_menus, format_date
from mongodb_helper import returnToday
import datetime as dt
import json


import pymongo
from pprint import pprint


bot = TeleBot(environ['TELEGRAM_TOKEN'])
bf_menu, dinz_menu = load_data()

text_messages = {
    'welcome':
        u'Hello there! I am your new Eusoff Meal Bot.'
        u' This is a test hello',

    'info':
        u'Hello there!\n'
        u'Please go to @eusoff_bot instead. This bot is our testing ground.\n',

    'wrong_chat':
        u'Hi there!\nThanks for trying me out!\n'
        u'We hope you find this useful. \n For any feedback/comments, please message @... \n'
        u'https://t.me/breadtest_bot',
      'feedback':
        u'Feel free to leave down any suggestions/opinions at https://goo.gl/forms/zaOOUhiJhH8RzlZx2 \n'
        u'We appreciate all kinds of feedback!',
    'calendar':
      u'hello calendar'
}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(message, text_messages['welcome'])
    
@bot.message_handler(commands=['info'])
def on_info(message):
  bot.reply_to(message, text_messages['info'])

@bot.message_handler(commands=['feedback'])
def on_feedback(message):
  bot.reply_to(message, text_messages['feedback'])
  
@bot.message_handler(commands=['calendar'])
def get_calendar(message):
  today = dt.datetime.fromtimestamp(message.date)
  result = returnToday(today)
  print(result)
  bot.reply_to(message, result)

def menu_markup():
  markup = InlineKeyboardMarkup()
  markup.row_width = 2
  markup.add(InlineKeyboardButton("MENU", callback_data="get_menu"))
  return markup

def gen_markup():
  markup = InlineKeyboardMarkup()
  markup.row_width = 2
  markup.add(InlineKeyboardButton("Tdy's Bf 🍞", callback_data="cb_tdy_bf"), \
             InlineKeyboardButton("Tdy's Dinz 🍱", callback_data="cb_tdy_din"), \
             InlineKeyboardButton("Tmr's Bf 🍞", callback_data="cb_tmr_bf"), \
             InlineKeyboardButton("Tmr's Dinz 🍱", callback_data="cb_tmr_din"))
  return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  date = dt.datetime.fromtimestamp(call.message.date)
  entry = {
    'date': date,
    'button': call.data,
    'username': call.message.chat.username,
    'type': 'callbackquery'
  }
  db.testing.insert_one(entry)
  if call.data=="get_menu":
    bot.send_message(call.message.chat.id, 'Select one:', parse_mode='Markdown',reply_markup=gen_markup())
  if call.data == "cb_tdy_bf":
    #menu=tdy_bf_m
    menu = get_indv_menus('Breakfast', date)
    bot.send_message(call.message.chat.id, menu, parse_mode='Markdown',reply_markup=menu_markup())
  if call.data == "cb_tdy_din": 
    #menu=tdy_din_m
    menu = get_indv_menus('Dinner', date)
    bot.send_message(call.message.chat.id, menu, parse_mode='Markdown',reply_markup=menu_markup())
  elif call.data == "cb_tmr_bf":
    #menu=tmr_bf_m
    menu = get_indv_menus('Breakfast', date + dt.timedelta(days=1))
    bot.send_message(call.message.chat.id, menu, parse_mode='Markdown',reply_markup=menu_markup())
  elif call.data == "cb_tmr_din":
    #menu=tdy_din_m
    menu = get_indv_menus('Dinner', date + dt.timedelta(days=1))
    bot.send_message(call.message.chat.id, menu, parse_mode='Markdown',reply_markup=menu_markup())

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.send_message(message.chat.id, "Hungz???", reply_markup=gen_markup())

  
@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, "Sorry, I do not understand. Try /start /help /info")

def listener(messages):  
    for m in messages:
        print(str(m))

        date = m.date
        text = m.json['text']
        username = m.json['from']['username']

        log = {
          'date': date,
          'text': text,
          'username': username,
          'type': 'message'
        }
        
        #db.testing.insert_one(log)
        #print('inserted to mongo db')


user =  environ['MONGO_USERNAME']
password =  environ['MONGO_PASSWORD']
database =  environ['MONGO_DB_NAME']

client = pymongo.MongoClient("mongodb://" + user + ":" + password + "@brenda test-shard-00-00-vfsiq.mongodb.net:27017,brendatest-shard-00-01-vfsiq.mongodb.net:27017,brendatest-shard-00-02-vfsiq.mongodb.net:27017/test?ssl=true&replicaSet=brendatest-shard-0&authSource=admin&retryWrites=true")
db = client[database]
pprint(client.list_database_names())


## testing facilities management
client = pymongo
        
bot.set_update_listener(listener)
bot.set_webhook("https://{}.glitch.me/{}".format(environ['PROJECT_NAME'], environ['TELEGRAM_TOKEN']))