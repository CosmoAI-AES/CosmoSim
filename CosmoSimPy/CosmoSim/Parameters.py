

class Parameters:
    def __init__(self,args):
        self._args = args
    def setRpw(self,row):
        self._row = row
    def get(self,key,default=None):
        try:
            r = self._args.key
        except AttributeError:
            r = default
        return self._row.get(key,r)
    def __getitem__(self,key):
        return get(key)


def makeSource(param):
    mode = param.get(sourcemode)
