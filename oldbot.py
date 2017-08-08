#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import re
import time
import sqlite3 as sql3
from telebot import types

userStep = {}
knownUsers = []
conn = sql3.connect("oldbot.db")
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS grupos
             (id int, link text, fecha text, user text)''')
conn.commit()

with open("./old.TOKEN", "r") as TOKEN:
    bot = telebot.TeleBot(TOKEN.read().strip(),threaded=False)

# Detects new users
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print ("Nuevo usuario detectado")
        return 0

def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print (str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

# Create bot
bot.set_update_listener(listener)

# Handlers
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola! añádeme a un grupo y te avisaré cuando un enlace esté repetido!")

@bot.message_handler(content_types=['text'])
def new_link(message):
    print str(message.from_user.username)
    match = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
    if match is not None:
        link = match.group(0)
        chat_id = message.chat.id
        dentro = c.execute("SELECT link FROM grupos WHERE id = " + str(chat_id) + " AND link = \'" + link + "\'")
        if dentro.fetchone() is not None:
            fecha =  c.execute("SELECT fecha FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            fechaTexto = fecha.fetchone()[0]
            user =  c.execute("SELECT user FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            userTexto = user.fetchone()[0]
            bot.reply_to(message, u"Old... Este mensaje fue enviado el " + fechaTexto + " por " + userTexto)
        else:
            valor = [(chat_id,link,time.strftime("%d/%m/%Y a las %H:%M"),str(message.from_user.username)),]
            c.executemany("INSERT INTO grupos VALUES (?,?,?,?)", valor)
            conn.commit()

# Ignora mensajes antiguos
bot.skip_pending = True

# Ejecuta...
print("Running...")
bot.polling()
conn.close()
