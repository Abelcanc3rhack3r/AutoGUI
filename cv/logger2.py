LOGFIELD=[]

def set_logfield(field):
    global LOGFIELD
    LOGFIELD=field

def print_log(field, *args):
    if(field in LOGFIELD):
        print(*args)

