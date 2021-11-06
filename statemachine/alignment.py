import copy

from actions import Action
from variables import Variable
from workflows import Workflow, Step


class Matrix(object):
    pass

def invert(dick):
    newdict= {}
    for k,v in dick.items():
        newdict[v]=k
    return newdict

def encode_category(all_workflows):
    steps_hash = {}
    def encode_params():
        action_param_names={}
        all_actions={}
        for workflow in all_workflows:
            for st in workflow.actions:
                rep = st.representation()
                action = rep[0]
                if(action not in all_actions):
                    all_actions[action]= "a"+str(len(all_actions))
                entry=set()
                param_values = rep[1:]
                param_names= [t[0] for t in param_values]
                for p in param_names:
                    if p not in entry:
                        entry.add(p)
                if (action not in action_param_names):
                    action_param_names[action]=entry
                else:
                    action_param_names[action] .update( entry)
        ap_out={}
        for a,action in action_param_names.items():
            print("a:",a)
            ap_out[a]= list(sorted(list(action_param_names[a])))
        return action_param_names, all_actions

    def encode_values():
        value_names = {}
        for workflow in all_workflows:
            for st in workflow.actions:
                rep = st.representation()
                action = rep[0]
                param_values = rep[1:]
                # sort the param values pairs in alphabetical order of param name to get a standardized param encoding if kw params are used
                sorte = sorted(param_values, key=lambda t: t[0])
                values = [t[1] for t in sorte]
                for v in values:
                    if v not in value_names:
                        value_names[v]= "v"+str(len(value_names))
        return value_names
    param_hash,action_hash = encode_params()
    values_hash=encode_values()
    encodings=[]
    for workflow in all_workflows:
        encoding, step_hash=encode_workflow(workflow,action_hash, param_hash, values_hash)
        encodings.append(encoding)
        steps_hash.update(step_hash)

    return encodings, invert(steps_hash)




def encode_workflow(workflow:Workflow, action_hash, param_hash, values_hash):
    steps_hash={}
    #action_hash={}
    #values_hash={}
    encoding=[]

    # get the list of all possible param names for each action


    apn= param_hash#get_action_param_names()
    for st in workflow.actions:
        rep= st.representation()
        action = rep[0]
        param_values= rep[1:]
        # sort the param values pairs in alphabetical order of param name to get a standardized param encoding if kw params are used
        sorte= sorted( param_values, key = lambda t: t[0])
        pns = [t[0] for t in sorte]
        vls= [t[1] for t in sorte]
        ap = apn[action]
        v_rep= []

        #encode the values
        for i,pn in enumerate(ap):
            if(pn in pns):
                va= vls[pns.index(pn)]
                v_rep.append(values_hash[va])
                #print(va, f"encoded as {values_hash[va]}")
            else:
                v_rep.append("vNaN")
                #print(va, f"encoded as vNaN")
        # encode the actions

        ah= action_hash[action]

        enc_v_rep= (ah,)+ tuple(v_rep)

        encoding.append(enc_v_rep)
        steps_hash[enc_v_rep]= st
        print(st, "encoded as ", enc_v_rep)

    return encoding, steps_hash




def create_state(workflow_encoding:list, values_hash):
#creates a state for every variable in the workflow
    variables_dict={}
    for i,enc_step in enumerate(workflow_encoding):
        values = enc_step[1:]
        act= enc_step[0]
        for vns in values:
            if(vns!="vNaN"):
                if(vns not in variables_dict):
                    variables_dict[vns]= Variable(name= vns)
                v=variables_dict[vns]
                v.append_log(i,act)
    kd=list(variables_dict.keys())
    #matrix =[]
    #for j in range(0, len(workflow_encoding)):
       # matrix.append([])
        #for i, k in enumerate(kd):
            #matrix[j].append([1])
    def fmt2(matrix):

        s = [[str(e) for e in row] for row in matrix]
        print(s)
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        return '\n'.join(table)
    def fmt(mat):
        strr=""
        for row in mat:
            strr+="\n"+str(row)
        return strr
    #print("matrix:", fmt2(matrix))
    state=[]
    for i, k in enumerate(kd):
        state.append([])
    matrix=[]
    for j in range(0, len(workflow_encoding)):
        state= copy.deepcopy(state)
        step= workflow_encoding[j]
        for i,k  in enumerate(kd):
            v = variables_dict[k]
            ac= v.get_log_at_step(j)
            if(ac is not None):
                state[i].append(ac)

        matrix.append((state, step))

    print("matrix2:\n",fmt2(matrix))




    return matrix
def create_all_states(workflow_encodings):
    all_states=[]
    for w in workflow_encodings:
        all_states.extend(create_state(w))
    return all_states





def test_encoding():
    init={}
    init["Name"]= "John"
    init["Age"]=3
    init['Sex']="M"

    cn= Action("click",target="Name")
    en= Action("type", words="John")
    ca = Action("click", target="Age")
    ea = Action("type", words="3", bold="bold")
    cs = Action("click", target="Sex")
    es = Action("type", words="M")
    w = Workflow(init, [cn,en,ca,ea,cs,es])
    w2 = Workflow(init, [ea])
    t,sh=encode_category([w])
    print(t)
    print("variables:",create_variables(t[0],sh))
    return

#test_encoding()






