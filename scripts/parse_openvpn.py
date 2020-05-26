# Скрипт для добавления в базу информации о подключенных оноплатниках

import pymysql
import os
from datetime import datetime
from config import username, password, host, port, db, charset


def query_get_sbc(name):
    """ Получаем id одноплатного компьютера (ОК) с указанным названием """
    return "SELECT id FROM sbc WHERE name='{}'".format(name)


def query_update_connected(connected, id):
    """ Обновлеине статуса ок """
    return "UPDATE sbc SET connected='{}' WHERE id='{}'".format(connected, id)


def query_insert_log(id, time, type, real_address, virtual_address):
    """ Вставка в log новой записи """
    return "insert into logs(sbc_id, date, type, realAddress, virtualAddress) values ('{}', '{}', '{}', '{}', '{}')".format(id, time, type, real_address, virtual_address)


def query_new_sbc(name, connected):
    """ Создание нового клиента """
    return "INSERT INTO sbc (name, connected) VALUES ('{}', '{}')".format(name, connected)


connect = pymysql.connect(
    host=host,
    user=username,
    password=password,
    db=db,
    charset=charset,
    port=int(port)
)

# собираем информацию о подключении одноплатного компьютера
connect_time = datetime.now()
common_name = os.getenv('common_name')
real_address = "{}:{}".format(os.getenv("trusted_ip"), os.getenv(
    "trusted_port") or '') if os.getenv("trusted_ip") else ''
virtual_address = os.getenv("ifconfig_pool_remote_ip") or ''
script_type = 'connect' if os.getenv(
    "script_type") == 'client-connect' else 'disconnect'

cur = connect.cursor()
cur.execute(query_get_sbc(common_name))
if cur.rowcount:
    # если запись найдена, заносим информацию в таблицу лог
    id = cur.fetchone()[0]
    connected = 1 if script_type == 'connect' else 0
    cur.execute(query_update_connected(connected, id))
    cur.execute(query_insert_log(id, connect_time,
                                 script_type, real_address, virtual_address))
    connect.commit()
else:
    connected = 1 if script_type == 'connect' else 0
    cur.execute(query_new_sbc(common_name, connected))
    # получаем id последней вставленной записи и заносим информацию в таблицу лог
    cur.execute('SELECT LAST_INSERT_ID()')
    id = cur.fetchone()[0]
    cur.execute(query_insert_log(id, connect_time,
                                 script_type, real_address, virtual_address))
    connect.commit()
connect.close()
