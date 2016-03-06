class ObjectDict(dict):
    def __init__(self, *args, **kws):
        super(ObjectDict, self).__init__(*args, **kws)
        self.__dict__ = self