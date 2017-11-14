# -*- coding: utf-8 -*-
import os
import zlib, base64
import random
random.seed(42)

compress   = lambda s: base64.b64encode(zlib.compress(s.encode('utf-8'),9))
decompress = lambda s: zlib.decompress(base64.b64decode(s)).decode('utf-8')

class history:
    def __init__(self, user_id):
        self.filename = "db/"+str(user_id)
        if not os.path.isfile(self.filename):
            open(self.filename,'wb+').write(b'')
        return

    def write(self, q):
        print(q)
        open(self.filename,'ab+').write(compress(q)+b'\n')
        return

    def read(self, n = 3, pos=0):
        lines = open(self.filename,'rb').read().split(b'\n')[:-1]
        return [decompress(i) for i in lines[::-1][pos:n+pos]]
 


class settings:
    def __init__(self, user_id):
        self.filename = "db/settings/"+str(user_id)+".txt"
        if not os.path.isfile(self.filename):
            open(self.filename,'w+').write('ru')
        return


    def write(self, q):
        print(q)
        open(self.filename,'w+').write(q)
        return


    def read(self):
        return open(self.filename,'r').read()

 
class page_cache: #make oop
    def __init__(self, user_id):
        self.filename = "db/cache/"+str(user_id)+".txt"
        return


    def write(self, q):
        random.shuffle(q)
        open(self.filename,'wb+').write(b"\n".join([compress(i) for i in q])) # add fixed sort
        return


    def read(self, n = 3, pos = 0):
        lines = open(self.filename,'rb').read().split(b'\n')[:-1]
        return [decompress(i) for i in lines[pos:n+pos]]

def get_db(user_id, dtype = None):
    if dtype == "history":
        return history(user_id)
    if dtype == "page_cache":
        return page_cache(user_id)
    if dtype == "settings":
        return settings(user_id)
    return None

