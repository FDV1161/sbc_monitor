from app import app
from flask import render_template
from sqlalchemy import func, and_
# from .models import loadSession, Sbc
from app import database as db
from .models import Sbc, Logs

@app.route("/")
def index():
	# session = loadSession()
	# res = session.query(Sbc).all()
	# print(res)
	# print(res[0].name)

	# Sbc.query.all()

	# db.query(Sbc, logs)
	# print(db.session.query(Logs.sbc_id, Logs.type, func.max(Logs.date)).group_by(Logs.sbc_id, Logs.type).all())

	# последнее подключение или отключени одноплатника 	
	last_connect = db.session.query(Logs.sbc_id, func.max(Logs.date).label('max_date')).group_by(Logs.sbc_id).subquery('last_connect')	
	# query = db.session.query(Logs, Sbc).join(last_connect, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	# res = query.join(Sbc, isouter=True)

	query = db.session.query(Sbc, Logs).outerjoin(last_connect, Sbc.id == last_connect.c.sbc_id)
	res = query.outerjoin(Logs, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	print(res)


	# query = db.session.query(Logs).join(last_connect, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))

	# query = db.session.query(Sbc, Logs).outerjoin(Logs).outerjoin(last_connect, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))


	# query = db.session.query(Logs, Sbc).join(last_connect, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))

	# query = db.session.query(Logs, Sbc).join(last_connect, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))

	# res = db.session.query(Sbc).outerjoin(query, Sbc.id==Logs.sbc_id)

	# res = Sbc.query().join(query, Sbc.id==Logs.sbc_id)
	# res = query.join(Sbc, Sbc.id==Logs.sbc_id)

	# res = db.session.query(Sbc).select_entity_from(query).join(Sbc, isouter=True)

	# res = db.session.query(Sbc).join(query, isouter=True)


	# res = db.session.query(Sbc).outerjoin(query)
	

	# res = db.session.query(Sbc).join(query, full=True)
	# res = Sbc.query().join(query, isouter=True)


	# res = db.session.query(Sbc, query)

	# for i in res :
	# 	print(i[0].date)

	# res = db.session.query(Sbc).join(query, Sbc.id == query.sbc_id)

	# print(res)








	# print(db.session.query(Logs.id, Logs.sbc_id, func.max(Logs.date)).group_by(Logs.sbc_id).all())


	# print(Logs.query(Logs.id, func.max(Logs.date).label('maxdate')).group_by(Logs.id).all())

	# id | name | 	id | sbc | type | date | ra | va 
	# 				select  from t group_by hover 
	

	# subq = session.query(
	# 	    Table.identifier,
	# 	    func.max(Table.date).label('maxdate')
	# 	).group_by(Table.identifier).subquery('t2')

	# res = Sbc.query.all()
	# for i in res:
	# 	print(i.name + " " + str(i.id))
	# 	print(dir(i.logs))
	# 	print(i.logs.sort())
		# for q in i.logs:
		# 	print(q.realAddress + " " + q.virtualAddress)
		
	
	# db.session.add(Sbc(name="test2"))
	# db.session.commit()
	
	# 
	# for i in res:
	# 	print(i.logs.first())

	# obj = Sbc.query.order_by(Sbc.logs.id.desc()).first()
	# print(obj)
	
	# return render_template('base.html', list_sbc=res)
	return render_template('base.html')
#    return "Hello World"    
