# скрипт для отслеживания и закрытия не используемых перенаправленных портов
import pymysql
import psutil
import os
import signal
from datetime import datetime
from config import username, password, host, port, db, charset


def stop_port_forwarding(pid):
    """
    Остановка проброс порта
    """
    try:
        process = psutil.Process(pid)
        if process.name().lower() == 'redir':
            os.kill(pid, signal.SIGKILL)
    except:
        pass
    return True


def query_track_forwarding():
    """
    Получаем все переадресации, время которых вышло
    """
    return "SELECT id, pid FROM forwarding WHERE TIMESTAMPDIFF(MINUTE, date_open, '{}') > time_live;".format(datetime.now())


def query_stop_port(id):
    """
    обнуляем информацию в базе у остоновленных переадресаций
    """
    return "UPDATE forwarding SET dedicated_port=NULL, time_live=NULL, date_open=NULL, pid=NULL where id='{}'".format(id)


connection = pymysql.connect(
    host=host,
    user=username,
    password=password,
    db=db,
    charset=charset,
    cursorclass=pymysql.cursors.DictCursor,
    port=int(port)
)

try:
    cursor = connection.cursor()
    cursor.execute(query_track_forwarding())
    list_stop = cursor.fetchall()
    for forwarding in list_stop:
        stop_port_forwarding(forwarding['pid'])
        cursor.execute(query_stop_port(forwarding['id']))
    connection.commit()
finally:
    connection.close()
