# -*- coding: utf-8 -*-
import wikipedia
import requests
from bs4 import BeautifulSoup

LANG = "ru"
wikipedia.set_lang(LANG)

# В библиотеке wikipedia не корректно
# отображаются страницы с несколькими значаниями


def get_suggested(q, lang):
    answer = []
    text = requests.get("https://"+lang+".wikipedia.org/wiki/"+q).content
    soup = BeautifulSoup(text, "html.parser")
    for line in soup.findAll('a'):
        if line.has_key('title'):
            if q.lower() in line.text.lower():
                if '(страница отсутствует)' not in line['title']:
                    answer.append(line['title'].replace(':', " "))
    return list(filter(lambda x:x.lower() != q.lower(), answer))


class wiki_parser:
    status = "na"
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
        if not self.parse_wikipedia(): 
            self.status = 0
            return False
        try:
            self.page = wikipedia.page(self.search[0])
        except wikipedia.exceptions.DisambiguationError as e:
            self.status = 2
            ## self.suggestion = e.options 
            ## Работает Не корректно на русском языке (Не выводит полное название статьи)
            self.suggestion = get_suggested(self.search[0], self.lang)
            return
        self.status = 1
        return True

    def __init__(self, query, lang=LANG):
        wikipedia.set_lang(lang)
        self.lang = lang
        self.query = query
        self.parse()
        return

