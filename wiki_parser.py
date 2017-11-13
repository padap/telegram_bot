import wikipedia
import requests
from bs4 import BeautifulSoup

LANG = "ru"
wikipedia.set_lang(LANG)

def change_lang(s):        #Not work, use bd
    wikipedia.set_lang(s)
    return

def get_suggested(q): # В библиотеке wikipedia не корректно отображаются страницы с несколькими значаниями
    answer = []
    text = requests.get("https://"+LANG+".wikipedia.org/wiki/"+q).content
    soup = BeautifulSoup(text, "html.parser")
    for i in soup.findAll('a'):
        if i.has_key('title'):
            if q.lower() in i.text.lower():
                if  not '(страница отсутствует)' in i['title']: 
                    answer.append(i['title'].replace(':', " "))
    print(answer)
    return answer

class wiki_parser:
    status = 0
    # 0 - not correct query
    # 1 - correct query
    # 2 - not correct, have a suggestion
    # ...

    def parse_wikipedia(self):
        search = wikipedia.search(self.query)
        if len(search) == 0:
            self.suggestion = wikipedia.suggest(self.query)
            return False
        self.search = search
        return True


    def parse(self):
        if  not self.parse_wikipedia(): 
            return False
        try:
            self.page = wikipedia.page(self.search[0])
        except wikipedia.exceptions.DisambiguationError as e:
            self.status = 2
            self.suggestion = e.options # Не корректно, на английском языке все работает, на русском не всегда
            self.suggestion = get_suggested(self.search[0])
            return
        self.status = 1
        return True
#   logging

    def __init__(self, query):
        print('new_object')
        self.query = query
        self.parse()
        return