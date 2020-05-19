import socket
from .config import MIN_NUMBER_PORT, MAX_NUMBER_PORT, TIME_WAITING
import subprocess
from threading import Timer


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
            print(port)
            return port
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
    Timer(TIME_WAITING, process.kill).start()
    return process
