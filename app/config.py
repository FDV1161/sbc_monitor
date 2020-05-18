# константы ограничивающие поиск свободного порта
MIN_NUMBER_PORT = 4000
MAX_NUMBER_PORT = 4999
# время ожидание перед закрытием порта в секундах
TIME_WAITING = 30  

# username = ''
# password = ''
# host = 'localhost:8080'
# bd = ''
# charset = 'utf8'
# 'mysql+pymysql://{}:{}@{}/{}?charset='.format(username, password, host, bd, charset)

# класс для конфигурации flask
class Config(object): 
	# SQLALCHEMY_DATABASE_URI = 'mysql://localhost:8080@root:root/tmp/test.db'	
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:8080/test?charset=utf8'
	SECRET_KEY = 'flask project'
	# pass
	# host = '0.0.0.0'
	# debug = True

