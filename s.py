
# -*- coding: utf-8 -*-
import config
import telebot
from wiki_parser import wiki_parser, change_lang
from logs import log, page_cache
from interface import button_interface
# wikipedia.set_lang('ru')
from telebot import types
import re

bot = telebot.TeleBot(config.token)
show_n_history = 3
show_n_simmilar = 3


#Class change settings
#Class organic speach
page_main = [ 
                [ types.InlineKeyboardButton(text = "Настройки",      callback_data = "/settings")],
                [ types.InlineKeyboardButton(text = "История",        callback_data = "/history"),
                  types.InlineKeyboardButton(text = "Связанные статьи", callback_data = "/equal_pages")]
            ]

settings_page = [ 
                    [ types.InlineKeyboardButton(text = "Сменить язык", callback_data = "/lanquage_change")],
                    [ types.InlineKeyboardButton(text = "Назад",        callback_data = "/main")]
                ]
lanquage_change = [
                    [types.InlineKeyboardButton(text = "Русский",      callback_data = "/change_to_russian")],
                    [types.InlineKeyboardButton(text = "English",      callback_data = "/change_to_english")],
                    [types.InlineKeyboardButton(text = "Назад",        callback_data = "/settings")]
                  ]
#how to parse regexp fo go to page 7 for example
#recomended articles
#normal suggest and len of text 
scenario = {"/main": page_main,
            "/settings": settings_page,
            "/lanquage_change": lanquage_change
           }
def main(message_chat_id, message_text):
    wiki_info = wiki_parser(message_text)
    logs = log(message_chat_id)
    logs.write(message_text)

    # bot.send_message(message_chat_id, message_chat_id) #DEBUG STATUS
    bot.send_message(message_chat_id, "Loading ...") #DEBUG STATUS
    if wiki_info.status == 0:
        message_send = 'Не могу ничего найти про "'+message_text+'"'
        if wiki_info.suggestion != None :
            message_send = 'Возможно вы имели в виду: "'+wiki_info.suggestion+'?"'

        bot.send_message(message_chat_id, message_send)
        return

    if wiki_info.status == 1:
        last_article = page_cache(message_chat_id)
        links = list(filter(lambda x:len(x)<20, wiki_info.page.links))
        last_article.write(links)
        message_send = wiki_info.page.summary
        keyboard = types.InlineKeyboardMarkup()
        for button in page_main:
            keyboard.add(*button)

        bot.send_message(message_chat_id, message_send+
                         "\n ["+wiki_info.page.url+"]")
        bot.send_message(message_chat_id, 'Меню:', reply_markup=keyboard)
        return

    if wiki_info.status == 2:
        keyboard = types.InlineKeyboardMarkup()
        # ttemp = ['wikt тор', 'Тор (поверхность)',  'Тор (зенитный)']#, 'Тор (зенитный ракетный комплекс)']#, 'Тор (ракета)']#, 'Тор (вспомогательный крейсер)', 'Славянск', 'Тор (Португалия)', 'Тор (Шаранта Приморская)', 'Тор (Об)', 'Тор (река)', 'Тор (вулкан)', 'Тор (фильм)', 'Тор (Marvel Comics)'] 
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

def change_menu(chat_id, message_id,  keyboard, menu_text = "Menu:"):
    bot.edit_message_text(  chat_id=chat_id,
                            message_id=message_id,
                            text=menu_text,
                            parse_mode='Markdown',
                            reply_markup=keyboard
                         )
    return

@bot.message_handler(content_types=["text"])
def default_test(message):
    main(message.chat.id, message.text)
    return

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    menu_text = "\tMenu:"
    print(call.data)
    print(dir(call.message))
    print(call.message.text)

    keyboard = types.InlineKeyboardMarkup()
    for key, page in scenario.items():
        if key == call.data:
            for button in page:
                keyboard.add(*button)

    if call.data == "/change_to_russian":
        change_lang("ru")
        menu_text = "Язык был поменян на русский"


    if call.data == "/change_to_english":
        change_lang("ru")
        menu_text = "Languqge was changed to english"

    if re.match(r'/history(\%\d+)?', call.data) != None:
        pos = re.search(r'\d+',call.data)
        pos = int(pos.group(0)) if pos != None else 0
        # print(pos)
        logs = log(call.message.chat.id)   
        history_query = logs.read(n = show_n_history, pos = pos)
        for q in history_query:
            keyboard.add(types.InlineKeyboardButton(text = q, callback_data = "/search"+q))
        if pos - show_n_history>=0 and len(history_query) == show_n_history:
            keyboard.add(
                         types.InlineKeyboardButton(text = "предыдущие " + str(show_n_history), callback_data = "/history%"+str(pos + show_n_history)),
                         types.InlineKeyboardButton(text = "следующие "  + str(show_n_history), callback_data = "/history%"+str(max(0,pos - show_n_history)))
                         )
        elif len(history_query) == show_n_history:
            keyboard.add(types.InlineKeyboardButton(text = "предыдущие " + str(show_n_history), callback_data = "/history%"+str(pos + show_n_history)))
        elif pos - show_n_history>0:
            keyboard.add(types.InlineKeyboardButton(text = "следующие  " + str(show_n_history), callback_data = "/history%"+str(pos - show_n_history)))
        else:
            keyboard.add(types.InlineKeyboardButton(text = "Ваша история пуста" , callback_data = "/main"))

        keyboard.add(types.InlineKeyboardButton(text = "Назад",  callback_data = "/main"))
    
    if re.match(r'/equal_pages(\%*)?', call.data) != None:
        pos = re.search(r'\d+',call.data)
        pos = int(pos.group(0)) if pos != None else 0
        last_article = page_cache(call.message.chat.id). #Sort for word2vec distance
        simmilar = last_article.read(n = show_n_simmilar, pos = pos)
        for text in simmilar:
            keyboard.add(types.InlineKeyboardButton(text = text , callback_data = "/search%"+text))
        keyboard.add(
                        types.InlineKeyboardButton(text = "предыдущие " + str(show_n_simmilar), callback_data = "/equal_pages%"+str(pos + show_n_simmilar)),
                        types.InlineKeyboardButton(text = "следующие "  + str(show_n_simmilar), callback_data = "/equal_pages%"+str(max(0,pos - show_n_simmilar)))
                    )
        keyboard.add(types.InlineKeyboardButton(text = "Назад",  callback_data = "/main"))


    if re.match(r'/search(\%*)?', call.data) == None:
        bot.edit_message_text(  
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=menu_text,
            parse_mode='Markdown',
            reply_markup=keyboard)
    else:
            q = call.data[call.data.find("%")+1:]
            bot.edit_message_text(  
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Ищем "+q,
            )
            main(call.message.chat.id, q)
    # bot.send_message(call.message.chat.id, "New", reply_markup=keyboard)

    return

if __name__ == '__main__':
     bot.polling(none_stop=True)