import os
class log:
    def __init__(self, user_id):
        self.filename = "db/"+str(user_id)+".txt"
        if not os.path.isfile(self.filename):
            print('here')
            open(self.filename,'w+').write('')
        return


    def write(self, q):
        open(self.filename,'a+').write(q+'\n')
        return


    def read(self, n = 3, pos = 0):
        lines = open(self.filename,'r').read().split('\n')[:-1]
        return lines[::-1][pos:n+pos]
 
class page_cache: #make oop
    def __init__(self, user_id):
        self.filename = "db/cache/"+str(user_id)+".txt"
        return


    def write(self, q):
        open(self.filename,'w+').write("\n".join(q)) # add fixed sort
        return


    def read(self, n = 3, pos = 0):
        lines = open(self.filename,'r').read().split('\n')[:-1]
        return lines[pos:n+pos]
