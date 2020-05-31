import socket
from .config import MIN_NUMBER_PORT, MAX_NUMBER_PORT, TIME_WAITING, HOME_PATH
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


def get_status_certificate():
    """
    Парсинг файла статуса сертификатов
    """  
    try:
        with open(HOME_PATH + '/openvpn-ca/keys/index.txt', 'r') as file:    
            result = []
            for line in file:
                spl = line.split('\t')
                i_s = spl[-1].find('/CN=') + 4
                i_e = spl[-1].find('/', i_s)
                name = spl[-1][i_s:i_e:1]
                result.append({'recalled': False if spl[0] == 'V' else True, 'name': name})
            return result    
    except:
        return [{'recalled': True, 'name': 'cliend1'}, {'recalled': False, 'name': 'cliend2'}]
    

def create_certificate(client_name):
    # создание ключей
    os.chdir(HOME_PATH + '/openvpn-ca')
    subprocess.call('./build-key --batch {}'.format(client_name))
    # создание сертификата
    os.chdir(HOME_PATH + '/client-configs')
    subprocess.call('./make_config.sh {}'.format(client_name))

def revocation_certificate(name):
    subprocess.call('./certificate_revocation.exe {}'.format(name))