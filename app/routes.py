from app import app, login_manager, database as db
from flask import render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from sqlalchemy import func, and_, or_

from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .models import Sbc, Forwarding, Logs, User
from .utils import search_free_port, start_port_forwarding, stop_port_forwarding, sum_date_with_minutes, get_status_certificate, create_certificate, revocation_certificate
from .forms import *
from .config import TIME_WAITING, MIN_NUMBER_PORT, MAX_NUMBER_PORT

login_manager.login_view = 'login'

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@login_manager.user_loader
def load_user(user_id):
    """
    Вызывается с каждым запросом к серверу, загружает пользователя из идентификатора пользователя в куки сессии
    """
    return db.session.query(User).get(user_id)


@app.route('/login', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(
            User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main'))
        flash("Неверный логин или пароль.", 'error')
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/", methods=['POST', 'GET'])
@login_required
def main():    
    if current_user.redirect_to:        
        if current_user.forwarding.dedicated_port:        
            return redirect('http://{}:{}'.format(request.host.split(':')[0], current_user.forwarding.dedicated_port))
        open_port = open_port_f(current_user.forwarding)
        if open_port:
            return redirect('http://{}:{}'.format(request.host.split(':')[0], open_port))
        flash('Не удалось открыть порт', 'error')        
    list_sbc_status = sidebar_content()    
    client = {
        'list_not_active': list_notactive_client(),     
        'count': len(list_sbc_status),
        'count_active': len([s for s in list_sbc_status if s.get('type')=='connect']),
        'forwarding':{
            'list_active': db.session.query(Sbc).outerjoin(Forwarding).filter(Forwarding.pid != None).all(),
            'count': Forwarding.query.filter(Forwarding.pid != None).count(),
            'count_max': MAX_NUMBER_PORT - MIN_NUMBER_PORT,
        }
    }
    return render_template('contents/main.html', list_sbc_status=list_sbc_status, client=client)


@app.route("/<int:sbc>", methods=['POST', 'GET'])
@app.route("/<int:sbc>/history/<int:page>", methods=['POST', 'GET'])
@login_required
def index(sbc, page=1):
    current_sbc = Sbc.query.get(sbc)
    if page <= 0 or not current_sbc:
        abort(404)
    # обновление описания
    descriptionForm = DescriptionForm()
    if descriptionForm.validate_on_submit():        
        try:            
            current_sbc.description = descriptionForm.text.data
            db.session.add(current_sbc)
            db.session.commit()
            return redirect(url_for('index', sbc=sbc))
        except:
            flash("Не удалось обновить описание")
            db.session.rollback()        
    descriptionForm.text.data = current_sbc.description
    # поиск информации о текущем состоянии рассматриваемого ок
    current_sbc_status = last_log(sbc)
    # поиск информации о текущем состоянии всех одноплатника
    list_sbc_status = sidebar_content()
    # поиск информации о переадресации портов для ок
    sbc_ports = Forwarding.query.filter_by(sbc_id=sbc).all()
    # количество логов
    count_logs = Logs.query.filter(Logs.sbc_id == sbc).count()
    history = {
        'list': Logs.query.order_by(Logs.id.desc()).filter(Logs.sbc_id == sbc).limit(10 * page),
        'page': page + 1,
        'max_page': False if count_logs / (page * 10) <= 1 else True,
        'count': count_logs
    }
    forms = {'description': descriptionForm}
    return render_template('contents/sbc.html', list_sbc_status=list_sbc_status, current_sbc=current_sbc, current_sbc_status=current_sbc_status, sbc_ports=sbc_ports, history=history, forms=forms, sum_date_with_minutes=sum_date_with_minutes)


@app.route("/delete_client/<int:sbc_id>")
@login_required
@admin_required
def delete_client(sbc_id):
    sbc = Sbc.query.get(sbc_id)
    try:
        db.session.delete(sbc)
        db.session.commit()
        return redirect(url_for('main'))
    except:
        db.session.rollback()
        flash("Не удалось удалить клиента")
    return redirect(url_for('index', sbc=sbc_id))
    

@app.route("/clear_logs/<int:sbc_id>")
@login_required
@admin_required
def clear_logs(sbc_id):    
    try:
        Logs.query.filter_by(sbc_id=sbc_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось отчистить журнал подключений")
    return redirect(url_for('index', sbc=sbc_id))


@app.route("/settings/<int:sbc>", methods=['GET', 'POST'])
@login_required
def settings(sbc):
    """
    Обработка страницы управления портами 
    """
    current_sbc = Sbc.query.get(sbc)
    if not current_sbc:
        abort(404)
    # добавление порта назначения для переадресации
    addPortForm = AddPortForm()
    if addPortForm.validate_on_submit():
        port = addPortForm.number_ap.data
        # смотрим добавлени ли уже порт
        if db.session.query(Forwarding.id).filter_by(sbc_id=sbc, destination_port=port).count():
            flash("Порт уже добавлен", 'error')
            return redirect(url_for('settings', sbc=sbc))
        forwarding = Forwarding(destination_port=port, sbc_id=sbc)        
        try:
            db.session.add(forwarding)
            db.session.commit()
            return redirect(url_for('settings', sbc=sbc))
        except:
            flash("Не удалось добавить порт", 'error')
            db.session.rollback()        
    # поиск информации о текущем состоянии каждого одноплатника
    list_sbc_status = sidebar_content()
    sbc_ports = Forwarding.query.filter_by(sbc_id=sbc).all()
    forms = {'addPort': addPortForm}
    return render_template('contents/settings.html', current_sbc=current_sbc, list_sbc_status=list_sbc_status, sbc_ports=sbc_ports, forms=forms)


@app.route("/open_port/<int:sbc>/<int:port_id>")
@login_required
def open_port(sbc, port_id):
    """
    Открытие порта 
    """    
    forwarding = Forwarding.query.get(port_id)        
    if open_port_f(forwarding):
        return redirect(url_for('settings', sbc=sbc))
    flash('Не удалось открыть порт', 'error')
    return redirect(url_for('settings', sbc=sbc))   


@app.route("/extend_time/<int:sbc>/<int:port_id>")
@login_required
def extend_time(sbc, port_id):
    forwarding = Forwarding.query.filter_by(sbc_id=sbc, id=port_id).first()
    if not forwarding:
        abort(404)
    if forwarding.pid:        
        try:
            forwarding.time_live += 60
            db.session.add(forwarding)
            db.session.commit()
            return redirect(url_for('settings', sbc=sbc))
        except:
            db.session.rollback()
    flash('Не удалось продлить время', 'error')
    return redirect(url_for('settings', sbc=sbc))


@app.route("/open_all_ports/<int:sbc>")
@login_required
def open_all_port(sbc):
    # ищем адрес назначения
    last_date = db.session.query(func.max(Logs.date)).filter_by(sbc_id=sbc)
    dest_address = db.session.query(Logs.virtualAddress).filter_by(
        sbc_id=sbc, date=last_date).first()
    if not dest_address:
        flash('Не удалось открыть порт. Не найден адрес клиента', 'error')
        return redirect(url_for('settings', sbc=sbc))
    # ищем порты для переадресации
    forwardings = Forwarding.query.filter_by(sbc_id=sbc).all()
    for forwarding in forwardings:
        if not open_port_f(forwarding, dest_address):
            flash('Не удалось открыть порт № {}'.format(
                forwarding.destination_port))
    return redirect(url_for('settings', sbc=sbc))


@app.route("/close_port/<int:sbc>/<int:port_id>")
@login_required
def close_port(sbc, port_id):
    port = Forwarding.query.get(port_id)
    if port:
        stop_port_forwarding(port.pid)
        port.pid = None
        port.time_live = None
        port.dedicated_port = None
        port.date_open = None
        try:
            db.session.add(port)
            db.session.commit()
            return redirect(url_for('settings', sbc=sbc))
        except:
            db.session.rollback()
    flash('Не удалось закрыть порт')
    return redirect(url_for('settings', sbc=sbc))


@app.route("/close_all_ports/<int:sbc>")
@login_required
def close_all_port(sbc):
    # ищем переадресованые порты
    forwardings = Forwarding.query.filter_by(sbc_id=sbc).all()
    for forwarding in forwardings:
        stop_port_forwarding(forwarding.pid)
        forwarding.pid = None
        forwarding.time_live = None
        forwarding.dedicated_port = None
        forwarding.date_open = None
        try:
            db.session.add(forwarding)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Не удалось закрыть порт')
    return redirect(url_for('settings', sbc=sbc))


@app.route("/delete_port/<int:sbc>/<int:port_id>")
@login_required
def delete_port(sbc, port_id):
    """
    Удаление номера порта из списка открываемых портов одноплатника
    """
    forwarding = Forwarding.query.get(port_id)
    if not forwarding:
        abort(404)
    if forwarding.pid:
        stop_port_forwarding(forwarding.pid)    
    try:
        Forwarding.query.filter_by(id=port_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось удалить порт")
    return redirect(url_for('settings', sbc=sbc))


@app.route("/users/", methods=['post', 'get'])
@login_required
@admin_required
def user_managment():    
    user_list = User.query.all()    
    users = {'list': user_list}
    list_sbc_status = sidebar_content()
    return render_template('contents/user_managment.html', list_sbc_status=list_sbc_status, users=users)


@app.route("/users/create", methods=['post', 'get'])
@login_required
@admin_required
def user_managment_create():    
    user_list = User.query.all()
    create_user_form = CreateUserForm()
    if create_user_form.validate_on_submit():
        if create_user_form.password.data == create_user_form.second_password.data:
            user = User(username=create_user_form.username.data)
            user.set_password(create_user_form.password.data)
            try:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('user_managment'))
            except:
                db.session.rollback()
                flash("Не удалось создать клиента")
        else:
            flash("Пароли не совпадают")
    users = {'list': user_list,'forms': {'create': create_user_form}}
    list_sbc_status = sidebar_content()
    return render_template('contents/user_managment.html', list_sbc_status=list_sbc_status, users=users)


@app.route("/users/rule", methods=['post', 'get'])
@login_required
@admin_required
def user_managment_rule():    
    user_list = User.query.all()    
    user_rule_form = UserRuleForm()    
    user_rule_form.user.choices = [(u.id, u.username) for u in user_list]
    if user_rule_form.validate_on_submit():
        user = User.query.get(user_rule_form.user.data)
        user.is_admin = user_rule_form.rule.data
        try:            
            db.session.commit()
            return redirect(url_for('user_managment_rule'))
        except:
            flash("Не удалось изменить права пользователя")
            db.session.rollback()        
    users = {'list': user_list, 'forms': {'rule': user_rule_form}}
    list_sbc_status = sidebar_content()
    return render_template('contents/user_managment.html', list_sbc_status=list_sbc_status, users=users)


@app.route("/users/forwarding", methods=['post', 'get'])
@login_required
@admin_required
def user_managment_forwarding():    
    user_list = User.query.all()
    forwarding_form = OnForwardingUserForm()
    forwarding_form.user.choices = [(u.id, u.username) for u in user_list]
    forwarding_form.client.choices = [(c.id, c.name) for c in Sbc.query.all()]
    if forwarding_form.validate_on_submit():
        u = User.query.get(forwarding_form.user.data)            
        f = Forwarding.query.filter_by(sbc_id=forwarding_form.client.data, destination_port=forwarding_form.port.data).first()
        if not forwarding_form.port.data:
            u.redirect_to = forwarding_form.port.data
        elif f:
            u.redirect_to = f.id
        else:
            f = Forwarding(sbc_id=forwarding_form.client.data, destination_port=forwarding_form.port.data)
            db.session.add(f)
            db.session.flush()
            u.redirect_to = f.id
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('user_managment'))    
    users = {'list': user_list, 'forms': {'forwarding': forwarding_form}}
    list_sbc_status = sidebar_content()    
    return render_template('contents/user_managment.html', list_sbc_status=list_sbc_status, users=users)


@app.route("/delete_user/<int:user_id>")
@login_required
@admin_required
def delete_user(user_id):
    if User.query.count() <= 1:
        flash("Не удалось удалить пользователя. Нельзя удалить последнего пользователя", 'error')
        return redirect(url_for('user_managment'))
    count_admin = User.query.filter(User.is_admin == True).count()
    user = User.query.get(user_id)
    if user.is_admin and count_admin <=1:
        flash("Не удалось удалить пользователя. Нельзя удалить последнего пользователя c правами администратора", 'error')
        return redirect(url_for('user_managment'))
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось удалить пользователя", 'error')
        return redirect(url_for('user_managment'))
    return redirect(url_for('user_managment'))


@app.route("/certificates/", methods=['post', 'get'])
@login_required
@admin_required
def certificate_managment():    
    create_cert_form = CreateCertificateForm()
    if create_cert_form.validate_on_submit(): 
        try:       
            create_certificate(create_cert_form.name.data)
        except:
            flash("Не удалось создать сертификат", 'error')
        return redirect(url_for('certificate_managment'))    
    sertificate = {
        'status': get_status_certificate(),
        'forms': create_cert_form 
    }
    list_sbc_status = sidebar_content()    
    return render_template('contents/certificate_managment.html', list_sbc_status=list_sbc_status, sertificate=sertificate)


@app.route("/recall_certificate/<string:name>")
@login_required
@admin_required
def recall_certificate(name):
    try:
        revocation_certificate(name)
    except:
        flash("Возникла ошибка при отзыве сертификата", 'error')
    return redirect(url_for('certificate_managment'))


def list_notactive_client():
    s = db.session.query(func.max(Logs.id)).group_by(Logs.sbc_id).subquery()
    l = db.session.query(Logs.sbc_id).filter(and_(Logs.id.in_(s), Logs.type == 'disconnect')).subquery()
    return Sbc.query.filter(Sbc.id.in_(l)).all()


def sidebar_content():
    # максимальный id логов по группам
    s = db.session.query(func.max(Logs.id)).group_by(Logs.sbc_id).subquery()
    # логи с максимальным id в группе
    ss = db.session.query(Logs).filter(Logs.id.in_(s)).subquery()
    q = db.session.query(Sbc.id, Sbc.name, ss.c.type).outerjoin(ss, Sbc.id==ss.c.sbc_id)    
    return [dict(zip(["id", "name", "type"], row)) for row in q.all()]


def last_log(sbc_id):
    """ Извлекает последний logs для клиента """    
    return Logs.query.filter_by(sbc_id=sbc_id).order_by(Logs.id.desc()).first()
    

def open_port_f(forwarding, dest_a=None):  
    """ Функция открытия порта """
    if not forwarding:
        return None
    # если уже открыт
    if forwarding.pid:
        return forwarding.dedicated_port
    # ищем адрес назначения
    if not dest_a:
        last_date = db.session.query(func.max(Logs.date)).filter_by(sbc_id=forwarding.sbc.id)
        dest_a = db.session.query(Logs.virtualAddress).filter_by(sbc_id=forwarding.sbc.id, date=last_date).first()
    dest_p = forwarding.destination_port
    # ищем свободный порт
    free_port = search_free_port()
    if not free_port or not dest_a or not dest_p:
        return None    
    process = start_port_forwarding(dest_a[0], dest_p, free_port)
    # обновляем записи в бд
    forwarding.date_open = datetime.now()
    forwarding.dedicated_port = free_port
    forwarding.time_live = TIME_WAITING
    forwarding.pid = process.pid
    try:
        db.session.add(forwarding)
        db.session.commit()
        return free_port
    except:
        process.kill()
        db.session.rollback()
    return None    