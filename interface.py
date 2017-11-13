import telebot
from telebot import types
import re
from logs import log, page_cache

show_n_history = 3
show_n_simmilar = 3
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
                    [types.InlineKeyboardButton(text  = "Русский",      callback_data = "/change_to_russian")],
                    [types.InlineKeyboardButton(text  = "English",      callback_data = "/change_to_english")],
                    [types.InlineKeyboardButton(text  = "Назад",        callback_data = "/settings")]
                  ]

def buttons_prev_next(pos, q_len, ref = "/search%"): # Buttons prev next
        res = []
        if pos - show_n_history>=0 and q_len == show_n_history:
            res=[types.InlineKeyboardButton(text = "предыдущие " + str(show_n_history), callback_data = ref+str(pos       + show_n_history)),
                 types.InlineKeyboardButton(text = "следующие "  + str(show_n_history), callback_data = ref+str(max(0,pos - show_n_history)))
                ]
        elif q_len == show_n_history:
            res = [types.InlineKeyboardButton(text  = "предыдущие " + str(show_n_history), callback_data = ref+str(pos + show_n_history))]
        elif pos - show_n_history>0:
            res = [types.InlineKeyboardButton(text = "следующие  " + str(show_n_history), callback_data = ref+str(pos - show_n_history))]
        return res

fixed_scenario = {
            r"/main":            page_main,
            r"/settings":        settings_page,
            r"/lanquage_change": lanquage_change
            }

history_scenario = r'/history'
equal_scenario   = r'/equal'
search_scenario  = r'/search'
class menu():

    def fixed_page(self,q, chat_id = None, message_id = None):
        keyboard = types.InlineKeyboardMarkup()
        for button in fixed_scenario[q]:
            keyboard.add(*button)

        self.info = {"chat_id":chat_id,
                     "message_id":message_id,
                     "text": "Меню:",
                     "parse_mode":'Markdown',
                     "reply_markup":keyboard
                    }     
                       
        self.success = True
        return


    def history_pages(self, call):
        keyboard = types.InlineKeyboardMarkup()
        pos = re.search(r'\d+',call.data)
        pos = int(pos.group(0)) if pos != None else 0
        logs = log(call.message.chat.id)
        history_query = logs.read(n = show_n_history, pos = pos)

        for text in history_query:
            keyboard.add( types.InlineKeyboardButton(text = text , callback_data = "/search%"+text) )
        keyboard.add(*buttons_prev_next(pos, len(history_query), ref = "/history%"))
        keyboard.add(types.InlineKeyboardButton(text = "Назад",  callback_data = "/main"))

        self.info = {"chat_id":call.message.chat.id,
                     "message_id":call.message.message_id,
                     "text": "История:",
                     "parse_mode":'Markdown',
                     "reply_markup":keyboard
                    }

        self.success = True
        return


    def equal_pages(self, call):
        q = call.data

        keyboard = types.InlineKeyboardMarkup()
        pos = re.search(r'\d+',call.data)
        pos = int(pos.group(0)) if pos != None else 0
        last_article = page_cache(call.message.chat.id)
        simmilar_query = last_article.read(n = show_n_simmilar, pos = pos)

        for text in simmilar_query:
            keyboard.add(types.InlineKeyboardButton(text = text , callback_data = "/search%"+text))

        keyboard.add(*buttons_prev_next(pos, len(simmilar_query), ref = "/equal%"))
        keyboard.add(types.InlineKeyboardButton(text = "Назад",  callback_data = "/main"))

        self.info = {"chat_id":call.message.chat.id,
                     "message_id":call.message.message_id,
                     "text": "Связанные статьи:",
                     "parse_mode":'Markdown',
                     "reply_markup":keyboard
                    }

        self.success = True

        pass

    def __init__(self, call=None, single_page=False):
        if single_page: # Interface for not inline function
            self.fixed_page(chat_id = -1, q = single_page, message_id = single_page)
            return

        self.success = False
        self.search = ""
        for sc in fixed_scenario:
            if re.match(sc, call.data) != None:
                self.fixed_page(q = call.data, chat_id = call.message.chat.id, message_id = call.message.message_id)
        if self.success: return

        if re.match(history_scenario, call.data) != None:
            self.history_pages(call)

        if re.match(equal_scenario, call.data) != None:
            self.equal_pages(call)

        if re.match(search_scenario, call.data) != None:
            print("ok")
            q = call.data[call.data.find("%")+1:]
            self.info = {
                        "chat_id":call.message.chat.id,
                        "message_id":call.message.message_id,
                        "text":"Ищем "+q,
                        }
            self.success = True
            self.search = q
            print(q)

        return