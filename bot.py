#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import sys
import requests
import json
import random
import urllib

TOKEN = '104896130:AAFqh4pgJQMxs5PP8bHssV0YMUTNTv45Me0'
bot = telebot.TeleBot(TOKEN)
ediciones_replies = []
wiki_replies = []
wiki_lang = {}
URLS = [
    ['Ì†ºÌ∑™Ì†ºÌ∑∏', 'https://es.wikipedia.org', 1],
    ['Ì†ºÌ∑≥Ì†ºÌ∑ø', 'https://en.wikipedia.org', 1],
    ['Ì†ºÌ∑πÌ†ºÌ∑∑', 'https://lad.wikipedia.org', 1],
    ['Ì†ΩÌ≥∑', 'https://commons.wikimedia.org', 1],
    ['Ì†ΩÌ∞∏', 'http://wikimedia.org.ve', 1]
]
IMAGES = ['001.jpg', '002.jpg', '003.jpg', '004.jpg', '005.jpg', '006.jpg', 
          '007.jpg', '008.jpg', '009.jpg', '010.jpg', '011.jpg', '012.jpg', 
          '013.jpg', '014.jpg', '015.jpg', '016.jpg']

def ediciones(chat_id, user):
    msg = 'Ediciones para el usuario ' + user + '\n'
    response = requests.post(
        'https://www.mediawiki.org/w/api.php',
        data={
            'action': 'query',
            'meta': 'globaluserinfo',
            'guiuser': user,
            'guiprop': 'editcount',
            'format': 'json'
        }
    )
    info = json.loads(response.text)
    if not 'editcount' in info['query']['globaluserinfo']:
        edit = 'No Existe'
    else:
        edit = str(info['query']['globaluserinfo']['editcount'])
    msg = msg + 'Ì†ºÌºé '.decode('utf-8') + edit + '\n'
    for icon, url, show in URLS:
        response = requests.post(
            url + '/w/api.php',
            data={
                'action': 'query',
                'list': 'users',
                'ususers': user,
                'usprop': 'editcount',
                'format': 'json'
            }
        )
        info = json.loads(response.text)
        if 'editcount' in info['query']['users'][0].keys():
            edit = info['query']['users'][0]['editcount']
        else:
            edit = 'No Existe'
        msg = msg + icon.decode('utf-8') + ' ' + str(edit) + '\n'
    bot.send_message(chat_id, msg)
    
def wiki(chat_id, search, lang):
    #print chat_id, search, lang
    ruta = 'https://' + lang + '.wikipedia.org'
    response = requests.post(
        url = ruta + '/w/api.php',
        data={
            'action': 'query',
            'list': 'search',
            'srlimit': 1,
            'srsearch': search,
            'format' : 'json'
        }
    )
    #print response.text.encode('utf-8')
    info = json.loads(response.text)
    if len(info['query']['search']) > 0:
        bot.send_message(chat_id, ruta + '/wiki/' + info['query']['search'][0]['title'].replace(' ', '_'))
    else:
        bot.send_message(chat_id, 'No se encontraron resultados')

def media(chat_id, search):
    #print chat_id, search, lang
    response = requests.post(
        url = 'https://commons.wikimedia.org/w/api.php',
        data={
            'action': 'query',
            'list': 'allimages',
            'aiprop': 'url',
            'ailimit': '100',
            'aifrom': search,
            'format' : 'json'
        }
    )
    #print response.text.encode('utf-8')
    info = json.loads(response.text)
    if len(info['query']['allimages']) > 0:
        allimages = info['query']['allimages']
        random.shuffle(allimages)
        url = allimages[0]['url'].decode('utf-8')
        title = allimages[0]['descriptionurl'].decode('utf-8')
        name = allimages[0]['name'].decode('utf-8')
        urllib.urlretrieve(url, "/tmp/" + name)
        photo = open("/tmp/" + name, 'rb')
        bot.send_photo(chat_id, photo, title)
    else:
        bot.send_message(chat_id, 'No se encontraron resultados')

# Handle /start and /help
@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    msg = 'Bot de Wikimedia Venezuela\nComandos:\n'
    msg = msg + '/ediciones <USUARIO>\n'
    msg = msg + '/wiki[:IDIOMA] <TERMINO DE BUSQUEDA>\n'
    msg = msg + '/media <TERMINO DE BUSQUEDA>\n'
    msg = msg + '/bajale2\n'
    bot.reply_to(message, msg)

# Handle /bajale2
@bot.message_handler(commands=['bajale2'])
def command_bajale2(message):
    random.shuffle(IMAGES)
    photo = open('bajale2/' + IMAGES[0], 'rb')
    bot.send_photo(message.chat.id, photo)


# Handle /ediciones
@bot.message_handler(commands=['ediciones'])
def command_media(message):
    if len(message.text.split(' ')) == 1:
        response = bot.reply_to(message, 'Debe escribir el comando de la siguiente manera\n/ediciones <Nombre de Usuario>\n\nPor ejemplo:\n/ediciones Jimbo_Wales')
        #TODO: Resolver lo de la pregunta para todos
        #markup = types.ForceReply()
        #response = bot.reply_to(message, "Indique el nombre de usuario", reply_markup=markup)
        #ediciones_replies.append(response.message_id)
    else:
        ediciones(message.chat.id, message.text.split(' ', 1)[1])

# Handle /media
@bot.message_handler(commands=['media'])
def command_ediciones(message):
    if len(message.text.split(' ')) == 1:
        response = bot.reply_to(message, 'Debe escribir el comando de la siguiente manera\n/media <TERMINO DE BUSQUEDA>\n\nPor ejemplo:\n/media Venezuela')
        #TODO: Resolver lo de la pregunta para todos
        #markup = types.ForceReply()
        #response = bot.reply_to(message, "Indique el nombre de usuario", reply_markup=markup)
        #media_replies.append(response.message_id)
    else:
        media(message.chat.id, message.text.split(' ', 1)[1])

# Handle /wiki
@bot.message_handler(func=lambda message: message.text[0:5]=='/wiki')
def command_wiki(message):
    lang = 'es'
    if len(message.text.split(' ')[0].split(':')) > 1:
        lang = message.text.split(' ')[0].split(':')[1]
    if len(message.text.split(' ')) == 1:
        response = bot.reply_to(message, 'Debe escribir el comando de la siguiente manera\n/wiki[:IDIOMA] <TERMINO DE BUSQUEDA>\n\nPor ejemplo:\n/wiki Venezuela\n/wiki:en Venezuela')
        #TODO: Resolver lo de la pregunta para todos
        #markup = types.ForceReply()
        #response = bot.reply_to(message, 'Indique el t√©rmino de b√∫squeda', reply_markup=markup)
        #wiki_replies.append(response.message_id)
        #wiki_lang[response.message_id] = lang
    else:
        search = message.text.split(' ', 1)[1]
        wiki(message.chat.id, search, lang)

# Default command handler. A lambda expression which always returns True is used for this purpose.
@bot.message_handler(func=lambda message: True, content_types=['text'])
def default_command(message):
    if message.reply_to_message_id in ediciones_replies:
        ediciones(message.chat.id, message.text)
        ediciones_replies.remove(message.reply_to_message_id)
    if message.reply_to_message_id in wiki_replies:
        wiki(message.chat.id, message.text, wiki_lang[message.reply_to_message_id])
        wiki_replies.remove(message.reply_to_message_id)
        del wiki_lang[message.reply_to_message_id]

bot.polling()

while True: # Don't let the main Thread end.
    pass