import workflows


def getState():
    return workflows.remove_dunders(globals())

def normalize(command):
    return command.lower()

current_category=None






def main():
    command = normalize(input("What would you like to do?"))
    if("new task" in command):
        category = input("Choose a name for the new type of task")
        workflows.WorkflowCategories.add_category(normalize(category))
    if("choose task" in command):
        print(workflows.WorkflowCategories.listCats())
        tsk= input("Choose a task:")
        if(normalize(tsk) in workflows.WorkflowCategories.categories.keys()):
            print("task chosen:", tsk)
            current_category= workflows.WorkflowCategories.categories[normalize(tsk)]




