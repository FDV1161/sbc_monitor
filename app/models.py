from app import database as db
# from sqlalchemy import create_engine, MetaData, Table, Integer, Text, String, Column
# from sqlalchemy.orm import mapper, sessionmaker

class Sbc(db.Model):
	__tablename__ = 'sbc'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	description = db.Column(db.Text)

class Logs(db.Model):
	__tablename__ = 'logs'
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime, nullable=False)
	type = db.Column(db.String(32), nullable=True)
	realAddress = db.Column(db.String(39), nullable=False)
	virtualAddress = db.Column(db.String(39), nullable=False)
	sbc_id = db.Column(db.Integer, db.ForeignKey('sbc.id'), nullable=False)
	sbc = db.relationship('Sbc', backref=db.backref('logs', lazy=True))




# class Sbc(object):
# 	pass
# def loadSession():
# 	engine = create_engine('mysql+pymysql://root:root@localhost:8080/test', echo=True)
# 	metadata = MetaData(engine)
# 	sbc_eng = Table('sbc', metadata, 
# 		Column('id', Integer, primary_key=True),
# 		Column('name', String(255)),
# 		Column('description', Text)    	
# 	)
# 	mapper(Sbc, sbc_eng)
# 	Session = sessionmaker(bind=engine)
# 	session = Session()	
# 	return session




# id = db.Column(db.Integer, primary_key=True)

