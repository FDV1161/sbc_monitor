# Деплой

## Установка зависимостей

В папке проекта необходимо создать и активировать виртуальное окружение. Используется виртуальное окружение `virtualenv` :

``` text
python3 -m pip install --upgrade pip # обновление pip
pip3 install virtualenv # установка virtualenv
virtualenv -p python3 venv # создание виртуального окружения
source venv/bin/activate # активация виртуального окружения
```

**Note:** Расширение mod_wsgi для работы apache использует в качестве виртуального окружения модуль virtualenv.

После активации виртуального окружения необходимо установить дополнительные утилиты Ubuntu и зависимости python:

``` text
sudo apt install redir # утилита переадресации порторв
sudo apt-get install gcc python3-dev # установка модуля для работы psutil
pip3 install -r requirements.txt # установка зависимостей
```

## Создание базы данных

Необходимо создать базу данных:  

``` text
create database test default character set utf8 default collate utf8_general_ci;
```

и отредактировать файл `app/cofig.py` и `scripts/cofig.py` в которых указываются настройки подключения к базе  
Находясь в папке проекта с активным виртуальным окружением запустить консоль python3 и выполнить следующие команды:

``` text
from app import database
database.create_all()
database.session.commit()
```

## Добавление пользователя

Для добавления пользователя необходимо зайти в консоль python3 и выполнить команды: 

``` text
from app import database as db
from app.models import User
user = User(username="name")
user.set_password("password")
db.session.add(user)
db.session.commit()
```

## Настройка openvpn

Для работы сторонних скриптов необходимо в файле конфигурации openvpn `(/etc/openvpn/server.conf)` установить тип защиты равный 2:

``` text
script-security 2
```

Пути к скриптам запускаемым при подключении (отключении) клиента прописываются в командах `client-connect (client-disconnect)` :

``` text
client-disconnect "project/venv/bin/python3" "project/scripts/parse_openvpn.py"
client-connect "project/venv/bin/python3" "project/scripts/parse_openvpn.py"
```

Перезапустить сервис: `service openvpn restart` 

## Настройка apache и mod_wsgi

Для работы с apache используется модель mod_wsgi. Для его установки используется команда:

``` text
sudo apt-get install libapache2-mod-wsgi-py3
```

Возможно потребуется включить модуль, для этого можно воспользоваться следующей командой 
````text
sudo a2enmod wsgi
````

После его установки необходимо настроить виртуальный хост apache. Для этого в папке `/etc/apache2/sites-available/` необходимо создать файл `sbc_monitor.conf` со следующим содержанием:

``` text
Listen 80
<VirtualHost *:80>
    ServerName 192.168.31.198
    WSGIDaemonProcess sbc_monitor user=dmitriy group=dmitriy threads=5
    WSGIScriptAlias / /var/www/sbc_monitor/sbc_monitor.wsgi
    <Directory /var/www/sbc_monitor>
        WSGIProcessGroup sbc_monitor
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
        Require all granted
    </Directory>
    ErrorLog /var/www/sbc_monitor/error.log
</VirtualHost>

```

В файле sbc_monitor.wsgi уставить путь до папки проекта и до интерпритатора python3: 

``` text
#! /var/www/sbc_monitor/venv/bin/python3
project_folder = '/var/www/sbc_monitor'
```

После чего необходимо включить виртуальный хост:

``` text
sudo a2ensite sbc_monitor.conf
```

Переконфигурировать и перезапустить apache:

``` text
service apache2 reload
service apache2 restart
```

**Note:** Для работы с mod_wsgi необходимо закоментировать в файле `sbc.py` строку `app.run(host="0.0.0.0", debug=True)`.

## Открытие портов

Для работы приложения необходимо в файле конфигурации `app/cofig.py` указать диапазон портов, с которыми оно будет работать и открыть их:

``` text
sudo iptables -I INPUT -p tcp --dport MIN_VALUE_PORT:MAX_VALUE_PORT -j ACCEPT
или
ufw allow MIN_VALUE_PORT:MAX_VALUE_PORT/tcp
```
Вместо MIN_VALUE_PORT:MAX_VALUE_PORT можно указать один порт

## Переадресация

Для закрытия переадресации по времени необходимо в планировщик cron добавить: 

``` text
*/10 * * * * /var/www/sbc_monitor/venv/bin/python3 /var/www/sbc_monitor/scripts/track_process.py
```
