# import subprocess 
from subprocess import Popen

api_path = "src/absentAPI.py"
listener_path = "src/absentListener.py"

subproccesses = {
    "api": api_path,
    "listener": listener_path
}

def processWrapper(func):
    def wrapper():
        while True:
            try:
                func()
            except BaseException as error:
                print('abSENT - {!r}; restarting process'.format(error))
            else:
                print('abSENT - Exited normally, bad process, restarting')
            print("RESTARTING PROCESS")
    return wrapper

while True:
    for process in subproccesses:
        print("RESTARTING PROCESS:", process)
        p = Popen(["python3", subproccesses[process]])
        p.wait()