import main

import actions as act

def remove_dunder(vars):
    vars={}
    for k ,v in vars.items():
        if("__" not in k):
            vars[k]=v
    return vars
class Step():
    state={}
    log={}
    #contains a log of each variable and how it was changed in steps prior to and in this step
    #parameters={}
    action=None
    def __init__(self, action):
        self.action=action
    def update_log(self, action_str):
        pass

    def representation(self):
        tup=()
        tup+= self.action.name
        for k,v in self.action.parameters.items():
            tup += ((k,v),)
        return tup


class WorkflowCategories():
    categories={}
    @staticmethod
    def listCats():
        strr="These are the tasks currently defined:"
        n=1
        for k,v in WorkflowCategories.categories.items():
            strr+="\n" +str(n)+". : "+ k
            n+=1
        return strr
    @staticmethod
    def add_category(name):
        WorkflowCategories.categories[name]= []
    @staticmethod
    def add_workflow_to_category(cat, wf):
        if(cat in WorkflowCategories.categories):
            WorkflowCategories.categories[cat].append(wf)
        return wf


class Workflow():

    actions=[]
    inputs=None
    def __init__(self, inputs={}, actions=[]):

        #creates a new workflow
        self.inputs=act.Action("_input_", **inputs)
        self.actions=[self.inputs]+actions
    def add_step(self, action, state):
        s= Step(action, main.getState())



