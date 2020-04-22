from app import app
from flask import render_template
from sqlalchemy import func, and_
from flask import request
# from .models import loadSession, Sbc
from app import database as db
from .models import Sbc, Logs


@app.route("/")
@app.route("/<int:choice_sbc_id>")
def index(choice_sbc_id=4):
	# последнее подключение или отключени одноплатника 	
	last_connect = db.session.query(Logs.sbc_id, func.max(Logs.date).label('max_date')).group_by(Logs.sbc_id).subquery('last_connect')	
	query = db.session.query(Sbc, Logs).outerjoin(last_connect, Sbc.id == last_connect.c.sbc_id)
	res = query.outerjoin(Logs, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	currend_sbc = None

	for i in res:
		if i[0].id == choice_sbc_id:
			currend_sbc = i
		print(i[1])

	

	
	return render_template('base.html', list_sbc_status=res, currend_sbc=currend_sbc)
	# return render_template('base.html')

