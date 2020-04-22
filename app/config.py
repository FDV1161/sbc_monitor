


# username = ''
# password = ''
# host = 'localhost:8080'
# bd = ''
# charset = 'utf8'
# 'mysql+pymysql://{}:{}@{}/{}?charset='.format(username, password, host, bd, charset)

class Config(object): 
	# SQLALCHEMY_DATABASE_URI = 'mysql://localhost:8080@root:root/tmp/test.db'	
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:8080/test?charset=utf8'
	# pass
	# host = '0.0.0.0'
	# debug = True
