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
bd = 'test'
charset = 'utf8'



# класс для конфигурации flask
class Config(object): 			
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset='.format(username, password, host, bd, charset)
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = 'flask project'
	

