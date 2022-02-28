# import subprocess 
from subprocess import Popen

api_path = "src.absentAPI"
listener_path = "src.absentListener"

subproccesses = {
    "api": api_path,
    "listener": listener_path
}

# p = Popen(["python", "-m", "src.absentAPI"])

while True:
    for process in subproccesses:
        print(f"Starting {process}")
        try:
            p = Popen(["python", "-m", subproccesses[process]])
            p.wait()
        except BaseException as error:
            print('abSENT - {!r}; restarting process'.format(error))
        else:
            print('abSENT - Exited normally, bad process, restarting')