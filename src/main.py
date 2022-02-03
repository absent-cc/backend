# import subprocess 
from subprocess import Popen

api_path = "src/absentAPI.py"
listener_path = "src/absentListener.py"

subproccesses = {
    "api": api_path,
    "listener": listener_path
}

while True:
    for process in subproccesses:
        try:
            p = Popen(["python3", subproccesses[process]])
            p.wait()
        except subprocess.CalledProcessError as error:
            print('abSENT - {!r}; restarting process'.format(error))
        else:
            print('abSENT - Exited normally, bad process, restarting')