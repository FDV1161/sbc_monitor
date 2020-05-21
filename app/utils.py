import socket
from .config import MIN_NUMBER_PORT, MAX_NUMBER_PORT, TIME_WAITING
import subprocess
from threading import Timer
import time


from random import randint


def search_free_port():
    """
    Поиск сводоного порта
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = MIN_NUMBER_PORT
    while port <= MAX_NUMBER_PORT:
        try:
            sock.bind(('', port))
            sock.close()            
            return randint(0, 4000)
        except OSError:
            port += 1
    # raise IOError('сould not find a free port')
    raise None


def start_port_forwarding(destination_address, destination_port, dedicated_port, timer_waiting=TIME_WAITING):
    """
    Запускает проброс порта
    """
    command = [
        "redir",
        "--lport={}".format(dedicated_port),
        "--cport={}".format(destination_port),
        "--caddr={}".format(destination_address)
    ]
    process = subprocess.Popen(command)

def stop_port_forwarding(pid):
    # os.kill(pid, 9)
    return True 



# Timer(timer_waiting, process.kill).start()
# return process
# def test():
#     db.query(Ports.pid).filter_by(now-Ports.date_open >= Ports.date_close)

# def do_something():
#     print("I am sleping")


# def thread_function():
#     while True:
#         do_something()
#         time.sleep(30)

# запуск
# остановки
# продления
# from app.utils import thread_function
# from threading import Thread
# Thread(target=thread_function, daemon=True).start()