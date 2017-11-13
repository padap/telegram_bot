# -*- coding: utf-8 -*-
import config
import telebot
from wiki_parser import wiki_parser, change_lang
from logs import log, page_cache
from interface import menu
# wikipedia.set_lang('ru')
from telebot import types
import re

bot = telebot.TeleBot(config.token)
show_n_history = 3
show_n_simmilar = 3

def main(message_chat_id, message_text):
    wiki_info = wiki_parser(message_text)
    logs = log(message_chat_id)
    logs.write(message_text)

    if wiki_info.status == 0:  # Can't find anything
        message_send = 'Не могу ничего найти про "'+message_text+'"'
        if wiki_info.suggestion != None :
            message_send = 'Возможно вы имели в виду: "'+wiki_info.suggestion+'?"'

        bot.send_message(message_chat_id, message_send)
        return

    if wiki_info.status == 1:  #
        last_article = page_cache(message_chat_id)
        links = list(filter(lambda x:len(x)<20, wiki_info.page.links))
        last_article.write(links)
        message_send = wiki_info.page.summary

        bot.send_message(message_chat_id, message_send+
                         "\n ["+wiki_info.page.url+"]")
        keyboard  = menu(single_page = '/main').info['reply_markup']
        bot.send_message(message_chat_id, 'Меню:', reply_markup = keyboard)
        return

    if wiki_info.status == 2:
        keyboard = types.InlineKeyboardMarkup()
        for temp in wiki_info.suggestion:
            ttemp = temp
            if len(temp) > 25:
                ttemp = temp.lower().replace("(", "").replace("(", "").replace(message_text,'')[:25]
            button = types.InlineKeyboardButton(text = ttemp, callback_data = "/search%"+ttemp)
            keyboard.add(button)

        button = types.InlineKeyboardButton(text = "Закрыть", callback_data = "/main")
        keyboard.add(button)

        bot.send_message(message_chat_id, message_text+" (значения)", reply_markup=keyboard)
        return
    return

@bot.message_handler(content_types=["text"])
def default_test(message):
    main(message.chat.id, message.text)
    return

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    buttons  = menu(call)       
    if buttons.success:
        bot.edit_message_text(**buttons.info)
        if len(buttons.search) != 0:
            main(call.message.chat.id, buttons.search)
        return

    if call.data == "/change_to_russian":
        change_lang("ru")
        menu_text = "Язык был поменян на русский"


    if call.data == "/change_to_english":
        change_lang("ru")
        menu_text = "Languqge was changed to english"

    return

if __name__ == '__main__':
     bot.polling(none_stop=True)