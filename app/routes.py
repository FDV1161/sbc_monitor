from app import app
from flask import render_template, redirect, url_for, flash
from sqlalchemy import func, and_
from flask import request
from sqlalchemy.exc import IntegrityError
from app import database as db
from datetime import datetime
from .models import Sbc, Forwarding, Logs
from .utils import search_free_port, start_port_forwarding, stop_port_forwarding
from .forms import AddPortForm, OpenAllPortForm, CloseAllPortForm, DescriptionForm
from .config import TIME_WAITING


@app.route("/", methods=['POST', 'GET'])
@app.route("/<int:sbc>", methods=['POST', 'GET'])
@app.route("/<int:sbc>/history/<int:page>", methods=['POST', 'GET'])		
def index(sbc=4, page=1):

	descriptionForm = DescriptionForm()
	if descriptionForm.validate_on_submit():
		update_description(sbc, descriptionForm.text.data)
		return redirect(url_for('index', sbc=sbc))
	 
	

	# последнее подключение или отключени одноплатника 	
	last_connect = db.session.query(Logs.sbc_id, func.max(Logs.date).label('max_date')).group_by(Logs.sbc_id).subquery('last_connect')	
	query = db.session.query(Sbc, Logs).outerjoin(last_connect, Sbc.id == last_connect.c.sbc_id)
	res = query.outerjoin(Logs, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	currend_sbc = None

	# поиск currend_sbc
	for i in res:
		if i[0].id == sbc:
			currend_sbc = i
			descriptionForm.text.data = i[0].description


	sbc_ports = Forwarding.query.filter_by(sbc_id=sbc).all()
	history = Logs.query.filter(Logs.sbc_id==sbc).limit(10 * page)		
	# количество логов 
	count_logs = Logs.query.filter(Logs.sbc_id==sbc).count() 	
	
	history = {
		'list': Logs.query.filter(and_(Logs.sbc_id==sbc, Logs.id >= 1)).limit(10 * page),
		'page': page + 1,
		'max_page': True if count_logs / (page * 10) > 0 else False
	}

	forms = {
		'description': descriptionForm,
	}
	
	return render_template('contents/main.html', list_sbc_status=res, currend_sbc=currend_sbc, currend_sbc_id=sbc, sbc_ports=sbc_ports, history=history, forms=forms)



def update_description(id, text):
	"""
	Обновление (добавление) описания у ок
	"""
	sbc = Sbc.query.get(id)
	sbc.description = text
	try:
		db.session.add(sbc)
		db.session.commit()		
	except IntegrityError:
		db.session.rollback()



@app.route("/settings/<int:sbc>", methods=['GET','POST'])
def settings(sbc):
	"""
	Обработка страницы управления портами 
	"""

	addPortForm = AddPortForm()		
	if addPortForm.validate_on_submit():		
		print("stac 1")
		add_port(addPortForm.number_ap.data, sbc)		
		return redirect(url_for('settings', sbc=sbc))
	
	
	openAllPortForm = OpenAllPortForm()
	if openAllPortForm.validate_on_submit():
		open_all_port(openAllPortForm.number_oap.data)
		return redirect(url_for('settings', sbc=sbc))	

	closeAllPortForm = CloseAllPortForm()
	if closeAllPortForm.validate_on_submit():
		close_all_port(openAllPortForm.number_oap.data)
		return redirect(url_for('settings', sbc=sbc))	

			

	last_connect = db.session.query(Logs.sbc_id, func.max(Logs.date).label('max_date')).group_by(Logs.sbc_id).subquery('last_connect')	
	query = db.session.query(Sbc, Logs).outerjoin(last_connect, Sbc.id == last_connect.c.sbc_id)
	list_sbc_status = query.outerjoin(Logs, and_(Logs.sbc_id == last_connect.c.sbc_id, Logs.date == last_connect.c.max_date))
	
	sbc_ports = Forwarding.query.filter_by(sbc_id=sbc).all()

	

	

	
	forms = {
		'addPort': addPortForm,		
		'openAllPort': openAllPortForm,
		'closeAllPort': closeAllPortForm
	}

	print(sbc)

	return render_template('contents/settings.html', currend_sbc_id=sbc, list_sbc_status=list_sbc_status, sbc_ports=sbc_ports, forms=forms)


@app.route("/delete_port/<int:sbc>/<int:port_id>")
def delete_port(sbc, port_id):	
	"""
	Удаление номера порта из списка открываемых портов одноплатника
	"""	
	forwarding = Forwarding.query.get(port_id)
	if forwarding.pid:
		stop_port_forwarding(forwarding.pid)	
	Forwarding.query.filter_by(id=port_id).delete()
	try:
		db.session.commit()		
	except IntegrityError:
		db.session.rollback()
		flash("Не удалось удалить порт")
	return redirect(url_for('settings', sbc=sbc))	


def add_port(port, sbc):
	"""
	Добавление номера порта к списку открываемых портов для sbc одноплатника
	"""	
	port = Forwarding(destination_port=port, sbc_id=sbc) # dedicated_port=None date_open="2020-05-22 12:30:00"
	db.session.add(port)
	try:
		db.session.commit()
	except IntegrityError:
		db.session.rollback()


@app.route("/open_port/<int:sbc>/<int:port_id>")
def open_port(sbc, port_id):
	"""
	Открытие порта 
	"""				
	# ищем порт назначения
	dest_port = Forwarding.query.get(port_id)
	# ищем адрес назначения
	last_date = db.session.query(func.max(Logs.date)).filter_by(sbc_id=sbc)
	dest_address = db.session.query(Logs.virtualAddress).filter_by(sbc_id=sbc, date=last_date).first()
	# выделяем порт 
	dedicated_port = search_free_port()
	if dest_address and dest_port and dedicated_port:		
		# запускаем переадресацию
		# process =  start_port_forwarding(virtual_address[0], dest_port.destination_port, dedicated_port)
		# обновляем записи в бд
		dest_port.date_open = datetime.now()
		dest_port.dedicated_port = dedicated_port		
		dest_port.time_live = TIME_WAITING
		dest_port.pid = 112
		try:
			db.session.add(dest_port)
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			# process.kill()
			flash('Не удалось открыть порт')			
	else:		
		if dedicated_port: 
			flash('Не удалось открыть порт')
		else: 
			flash('Не удалось открыть порт. Все порты заняты')
	return redirect(url_for('settings', sbc=sbc))	


@app.route("/open_all_ports/<int:sbc>")
def open_all_port(sbc):
	# ищем адрес назначения
	last_date = db.session.query(func.max(Logs.date)).filter_by(sbc_id=sbc)
	dest_address = db.session.query(Logs.virtualAddress).filter_by(sbc_id=sbc, date=last_date).first()
	# ищем порты для переадресации
	forwardings = Forwarding.query.filter_by(sbc_id=sbc).all()
	for forwarding in forwardings:
		# если уже открыт
		if forwarding.pid:
			continue
		# выделяем порт 
		dedicated_port = search_free_port()
		if dedicated_port :
			# process =  start_port_forwarding(dest_address[0], dest_port.destination_port, dedicated_port)
			forwarding.date_open = datetime.now()
			forwarding.dedicated_port = dedicated_port		
			forwarding.time_live = TIME_WAITING
			forwarding.pid = 112
			db.session.add(forwarding)
			try:			
				db.session.commit()
			except IntegrityError:
				db.session.rollback()
		else:
			flash('Не удалось открыть порт № {}'.format(forwarding.destination_port))
		

	return redirect(url_for('settings', sbc=sbc))

	
@app.route("/close_port/<int:sbc>/<int:port_id>")
def close_port(sbc, port_id):
	port = Forwarding.query.get(port_id)	
	if port:
		if stop_port_forwarding(port.pid):
			port.pid = None
			port.time_live = None
			port.dedicated_port = None
			port.date_open = None
			try:
				db.session.add(port)
				db.session.commit()
				return redirect(url_for('settings', sbc=sbc))
			except IntegrityError:
				db.session.rollback()	
	flash('Не удалось закрыть порт')
	return redirect(url_for('settings', sbc=sbc))


@app.route("/close_all_ports/<int:sbc>")
def close_all_port(sbc):
	# ищем переадресованые порты
	forwardings = Forwarding.query.filter_by(sbc_id=sbc).all()
	for forwarding in forwardings:
		if stop_port_forwarding(forwarding.pid):
			forwarding.pid = None
			forwarding.time_live = None
			forwarding.dedicated_port = None
			forwarding.date_open = None
			try:
				db.session.add(forwarding)
				db.session.commit()				
			except IntegrityError:
				db.session.rollback()
		else:
			flash('Не удалось закрыть порт')
	return redirect(url_for('settings', sbc=sbc))



	
		
		# new_port = request.form.get('add_port')	
		# add_port(new_port, choice_sbc_id)
	# print(request.form.get('add_port'))
	# Ports.query()

# def all_ports():
# 	pass
	# sbc = Sbc.query.get(choice_sbc_id)
	# sbc_ports = Ports.query.with_parent(sbc).all()
	# sbc_ports = Ports.query.filter_by(sbc_id=choice_sbc_id).all()
