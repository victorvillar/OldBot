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
             (id int, link text, fechaPrimero text, fechaUltimo text,
              userPrimero text, userUltimo text, contador int)''')
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
            print (str(m.from_user.username) + " [" + str(m.chat.id) + "]: " + m.text)

# Create bot
bot.set_update_listener(listener)

# Handlers
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola! añádeme a un grupo y te avisaré cuando un enlace esté repetido!")

@bot.message_handler(content_types=['text'])
def new_link(message):
    match = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
    if match is not None:
        link = match.group(0)
        chat_id = message.chat.id
        dentro = c.execute("SELECT link FROM grupos WHERE id = " + str(chat_id) + " AND link = \'" + link + "\'")
        if dentro.fetchone() is not None:
            fechaPrimero =  c.execute("SELECT fechaPrimero FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            fechaPrimeroTexto = fechaPrimero.fetchone()[0]
            userPrimero =  c.execute("SELECT userPrimero FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            userPrimeroTexto = userPrimero.fetchone()[0]
            fechaUltimo =  c.execute("SELECT fechaUltimo FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            fechaUltimoTexto = fechaUltimo.fetchone()[0]
            userUltimo =  c.execute("SELECT userUltimo FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            userUltimoTexto = userUltimo.fetchone()[0]
            contador =  c.execute("SELECT contador FROM grupos WHERE id = " + str(chat_id) + " AND link = \"" + link + "\"")
            contadorTexto = contador.fetchone()[0]
            print contadorTexto
            if contadorTexto == 1:
                bot.reply_to(message, u"OOOLD... \nEste mensaje fue enviado originalmente el " + fechaPrimeroTexto + " por @" + userPrimeroTexto +
                             ". \nSe ha enviado un total de " + str(contadorTexto) + " vez.")
            else:
                bot.reply_to(message, u"OOOLD... \nEste mensaje fue enviado originalmente el " + fechaPrimeroTexto + " por @" + userPrimeroTexto +
                             " y por ultima vez  el " + fechaUltimoTexto + " por @" + userUltimoTexto + 
                             ". \nSe ha enviado un total de " + str(contadorTexto) + " veces.")
            cnt = int(contadorTexto) + 1    
            datos = [(str(cnt) , str(message.from_user.username) , time.strftime("%d/%m/%Y a las %H:%M") , str(chat_id)),]
            c.executemany("UPDATE grupos SET contador = ? , userUltimo = ? , fechaUltimo = ? WHERE id = ?", datos)
            conn.commit()
        else:
            valor = [(chat_id,link,time.strftime("%d/%m/%Y a las %H:%M"),time.strftime("%d/%m/%Y a las %H:%M"), str(message.from_user.username), str(message.from_user.username), "1"),]
            c.executemany("INSERT INTO grupos VALUES (?,?,?,?,?,?,?)", valor)
            conn.commit()

# Ignora mensajes antiguos
bot.skip_pending = True

# Ejecuta...
print("Running...")
bot.polling()
conn.close()
