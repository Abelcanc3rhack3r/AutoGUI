class Variable():
    log = {}
    name=""
    def append_log(self, stepnum, action):
        self.log[stepnum]= action
    def get_log_at_step(self,stepnum):
        return self.log.get(stepnum,None)
    def __init__(self,name):
        self.name=name
        self.log={}
        pass
    def repr_log(self, values_hash, actions_hash):
        tups= [t for t in self.log.items()]
        tups.sort()
        strr=""
        for t in tups:
            strr+= " "+ actions_hash
        return strr


