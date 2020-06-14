# константы ограничивающие поиск свободного порта
MIN_NUMBER_PORT = 4000
MAX_NUMBER_PORT = 4999
# время ожидание перед закрытием порта в секундах
TIME_WAITING = 60
# конфигурация базы данных
username = 'root'
password = 'root'
host = 'localhost'
port = '8080'
bd = 'test3'
charset = 'utf8mb4'


class Path:
    # пути до папок
    OPENVPNCA = '/home/dmitriy/openvpn-ca'  # до папки openvpn-ca
    CLIENTCONFIGS = '/home/dmitriy/client-configs'  # до папки client-configs
    # до папки со скриптом copy_crlpen.bin
    COPYCRLPEN = '/var/www/sbc_monitor'
	# до файла со списком серификатов
    CERTLIST = '/openvpn-ca/keys/index.txt'


# класс для конфигурации flask
class Config(object):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset='.format(
        username, password, host, port, bd, charset)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'flask project'
