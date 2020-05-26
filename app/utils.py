import socket
from .config import MIN_NUMBER_PORT, MAX_NUMBER_PORT, TIME_WAITING
import subprocess
import signal
import os
import psutil
import datetime


def sum_date_with_minutes(date, min):
    return date + datetime.timedelta(minutes=min)


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
            return port
        except OSError:
            port += 1
    raise None


def start_port_forwarding(destination_address, destination_port, dedicated_port, timer_waiting=TIME_WAITING):
    """
    Запускает проброс порта
    """
    command = [
        "redir",
        "--lport={}".format(dedicated_port),
        "--cport={}".format(destination_port),
        "--caddr={}".format(destination_address),
        "--timeout=60"
    ]
    process = subprocess.Popen(command)
    return process


def stop_port_forwarding(pid):
    """
    Остановка проброс порта
    """
    try:
        process = psutil.Process(pid)
        if process.name().lower() == 'redir':
            process.terminate()
    except:
        pass
