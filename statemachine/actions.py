from workflows import Workflow, Step


class Action():

    #parameters={}
    name=""
    def __init__(self,name, *params,**kwparams):
        self.parameters={}
        self.name=name

        if(params is not None):
            for i,k in enumerate(params):
                self.parameters[str(i)]= k
        if(kwparams is not  None):
                for k,v in kwparams.items():
                    self.parameters[k]=v

    def execute(self):
        print(self, "executed!")
    def __str__(self):
        return self.name+"("+ ",".join([(str(tup[0])+"="+str(tup[1])) for tup in self.parameters.items()])+")"

    def representation(self):
        tup=()
        tup+= (self.name,)
        for k,v in self.parameters.items():
            tup += ((k,v),)
        return tup

a= Action("foo",1,2)
print(a)
b = Action("bar",a="a", b="b")
print(b)
c=Action("baz", 1,a="a")

print(c)

