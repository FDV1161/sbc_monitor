# скрипт для отслеживания и закрытия не используемых перенаправленных портов 

import pymysql

connect = pymysql.connect(
    host="localhost",
    user="root",
    password="252800",
    db="sbc_monitor",
    charset="utf8",
)

cursor = connect.cursor()
# получаем все переадресации, время которых вышло
cursor.execute("SELECT id, pid FROM forwarding WHERE TIMESTAMPDIFF(MINUTE, date_open, now()) > time_live;")
list_stop = cursor.fetchall()
for forwarding in list_stop:
    forwarding['pid']

# SELECT id, pid FROM forwarding WHERE TIMESTAMPDIFF(MINUTE, date_open, now()) > time_live;
# DATEDIFF("2017-06-25 09:34:21", date_open);
 
