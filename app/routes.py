from app import app
from flask import render_template, redirect, url_for
from sqlalchemy import func, and_
from flask import request
# from .models import loadSession, Sbc
from sqlalchemy.exc import IntegrityError
from app import database as db
from .models import Sbc, Ports, Logs
from .utils import search_free_port
from .forms import AddPortForm, DeletePortForm, OpenPortForm, ClosePortForm, OpenAllPortForm, CloseAllPortForm


@app.route("/")
@app.route("/<int:choice_sbc_id>")
def index(choice_sbc_id=4):
	# последнее подключение или отключени одноплатника 	
	last_connect = db.session.query(Logs.sbc_id, func.max(Logs.date).label('max_date')).group_by(Logs.sbc_id).subquery('last_connect')	
	query = db.session.query(Sbc, Logs).outerjoin(last_connect, Sbc.id == last_connect.c.sbc_id)
	res = query.outerjoin(Logs, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	currend_sbc = None

	# поиск currend_sbc
	for i in res:
		if i[0].id == choice_sbc_id:
			currend_sbc = i
		print(i[1])
	

	sbc_ports = Ports.query.filter_by(sbc_id=choice_sbc_id).all()
	print(sbc_ports)	

	
	return render_template('base.html', list_sbc_status=res, currend_sbc=currend_sbc, sbc_ports=sbc_ports)
	# return render_template('base.html')


@app.route("/settings/<int:choice_sbc_id>", methods=['GET','POST'])
def settings(choice_sbc_id):
	"""
	Обработка страницы управления портами 
	"""

	addPortForm = AddPortForm()		
	if addPortForm.validate_on_submit():		
		add_port(addPortForm.number_ap.data, choice_sbc_id)		
		return redirect(url_for('settings', choice_sbc_id=choice_sbc_id))

	deletePortForm = DeletePortForm()
	if deletePortForm.validate_on_submit():
		del_port(deletePortForm.number_dp.data)		
		return redirect(url_for('settings', choice_sbc_id=choice_sbc_id))

	openPortForm = OpenPortForm()
	if openPortForm.validate_on_submit():
		open_port(openPortForm.number_op.data)
		return redirect(url_for('settings', choice_sbc_id=choice_sbc_id))

	closePortForm = ClosePortForm()
	if closePortForm.validate_on_submit():
		close_port(openPortForm.number_cp.data)
		return redirect(url_for('settings', choice_sbc_id=choice_sbc_id))

	openAllPortForm = OpenAllPortForm()
	if openAllPortForm.validate_on_submit():
		open_all_port(openAllPortForm.number_oap.data)
		return redirect(url_for('settings', choice_sbc_id=choice_sbc_id))	

	closeAllPortForm = CloseAllPortForm()
	if closeAllPortForm.validate_on_submit():
		close_all_port(openAllPortForm.number_oap.data)
		return redirect(url_for('settings', choice_sbc_id=choice_sbc_id))	

			

	last_connect = db.session.query(Logs.sbc_id, func.max(Logs.date).label('max_date')).group_by(Logs.sbc_id).subquery('last_connect')	
	query = db.session.query(Sbc, Logs).outerjoin(last_connect, Sbc.id == last_connect.c.sbc_id)
	list_sbc_status = query.outerjoin(Logs, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	
	sbc_ports = Ports.query.filter_by(sbc_id=choice_sbc_id).all()

	
	forms = {
		'addPort': addPortForm,
		'deletePort': deletePortForm,
		'openPort': openPortForm,
		'closePort': closePortForm,
		'openAllPort': openAllPortForm,
		'closeAllPort': closeAllPortForm
	}

	return render_template('settings.html', currend_sbc=choice_sbc_id, list_sbc_status=list_sbc_status, sbc_ports=sbc_ports, forms=forms)


def add_port(port, sbc):
	"""
	Добавление номера порта к списку открываемых портов для sbc одноплатника
	"""	
	port = Ports(destination_port=port, sbc_id=sbc) # dedicated_port=None date_open="2020-05-22 12:30:00"
	db.session.add(port)
	try:
		db.session.commit()
	except IntegrityError:
		db.session.rollback()

def del_port(id):
	"""
	Удаление номера порта из списка открываемых портов одноплатника
	"""	
	Ports.query.filter_by(id=id).delete()
	try:
		db.session.commit()
	except IntegrityError:
		db.session.rollback()

def open_port(id):
	"""
	Открытие порта 
	"""	
	port = search_free_port()
	print("Найден порт номер: " + str(port))

def close_port(id):
	pass

def open_all_port():
	pass

def close_all_port():
	pass


	
		
		# new_port = request.form.get('add_port')	
		# add_port(new_port, choice_sbc_id)
	# print(request.form.get('add_port'))
	# Ports.query()

# def all_ports():
# 	pass
	# sbc = Sbc.query.get(choice_sbc_id)
	# sbc_ports = Ports.query.with_parent(sbc).all()
	# sbc_ports = Ports.query.filter_by(sbc_id=choice_sbc_id).all()
