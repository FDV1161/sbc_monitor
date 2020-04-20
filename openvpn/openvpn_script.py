# Скрипт для добавления в базу информации о подключенных оноплатниках

import pymysql
import os
from datetime import datetime

# собираем информацию о подключении одноплатного компьютера
connect_time = datetime.now()
common_name = os.getenv('common_name')
real_address = "{}:{}".format(os.getenv("trusted_ip"), os.getenv("trusted_port") or '') if os.getenv("trusted_ip") else ''
virtual_address = os.getenv("ifconfig_pool_remote_ip") or ''
script_type = 'connect' if os.getenv("script_type") == 'client-connect' else 'disconnect'

connect = pymysql.connect(
    host="localhost",
    user="root",
    password="252800",
    db="sbc_monitor",
    charset="utf8",
)

cur = connect.cursor()

# получаем id одноплатного компьютера (ОК) с указанным названием
cur.execute("SELECT id FROM sbc WHERE name='{}'".format(common_name))
if cur.rowcount:
        # если запись найдена, заносим информацию в таблицу лог
        id = cur.fetchone()[0]
        cur.execute("insert into logs(sbc, date, type, realAddress, virtualAddress) \
                        values('{}', '{}', '{}', '{}', '{}')".format(id, connect_time, script_type, real_address, virtual_address))
        connect.commit()
else:
        # создаем запись о новом ОК
        cur.execute("INSERT INTO sbc (name) VALUES ('{}')".format(common_name))
        # получаем id последней вставленной записи и заносим информацию в таблицу лог
        cur.execute('SELECT LAST_INSERT_ID()')
        id = cur.fetchone()[0]
        cur.execute("INSERT INTO logs(sbc, date, type, realAddress, virtualAddress) \
                        VALUES('{}', '{}', '{}', '{}', '{}')".format(id, connect_time, script_type, real_address, virtual_address))
        connect.commit()
cur.close()

