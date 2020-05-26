from app import app, login_manager, database as db
from flask import render_template, redirect, url_for, flash, abort, request
from sqlalchemy import func, and_, or_
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .models import Sbc, Forwarding, Logs, User
from .utils import search_free_port, start_port_forwarding, stop_port_forwarding, sum_date_with_minutes
from .forms import AddPortForm, DescriptionForm, LoginForm, CreateUserForm
from .config import TIME_WAITING

login_manager.login_view = 'login'


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
    list_sbc_status = Sbc.query.all()
    list_sbc_with_active_forwarding = db.session.query(Sbc).outerjoin(
        Forwarding).filter(Forwarding.pid != None).all()
    list_notactive_clients = Sbc.query.filter(
        or_(Sbc.connected == False, Sbc.connected == None)).all()
    count_active_clients = Sbc.query.filter(Sbc.connected == True).count()
    count_all_clients = Sbc.query.count()

    return render_template('contents/main.html', list_sbc_status=list_sbc_status,
                           list_sbc_with_active_forwarding=list_sbc_with_active_forwarding,
                           list_notactive_clients=list_notactive_clients, count_active_clients=count_active_clients, count_all_clients=count_all_clients)


@app.route("/<int:sbc>", methods=['POST', 'GET'])
@app.route("/<int:sbc>/history/<int:page>", methods=['POST', 'GET'])
@login_required
def index(sbc, page=1):

    if page <= 0:
        abort(404)

    current_sbc = Sbc.query.get(sbc)
    if not current_sbc:
        abort(404)

        # обновление описания
    descriptionForm = DescriptionForm()
    if descriptionForm.validate_on_submit():
        update_description(sbc, descriptionForm.text.data)
        return redirect(url_for('index', sbc=sbc))
    descriptionForm.text.data = current_sbc.description

    # поиск информации о текущем состоянии рассматриваемого ок
    max_date = db.session.query(func.max(Logs.date)).filter(Logs.sbc_id == sbc)
    current_sbc_status = Logs.query.filter(
        and_(Logs.sbc_id == sbc, Logs.date == max_date)).first()
    # поиск информации о текущем состоянии всех одноплатника
    list_sbc_status = Sbc.query.all()
    # поиск информации о переадресации портов для ок
    sbc_ports = Forwarding.query.filter_by(sbc_id=sbc).all()

    # количество логов
    count_logs = Logs.query.filter(Logs.sbc_id == sbc).count()
    history = {
        'list': Logs.query.order_by(Logs.date.desc()).filter(Logs.sbc_id == sbc).limit(10 * page),
        'page': page + 1,
        'max_page': False if count_logs / (page * 10) <= 1 else True,
        'count': count_logs
    }
    forms = {'description': descriptionForm}
    return render_template('contents/sbc.html', list_sbc_status=list_sbc_status, current_sbc=current_sbc, current_sbc_status=current_sbc_status, sbc_ports=sbc_ports, history=history, forms=forms, sum_date_with_minutes=sum_date_with_minutes)


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
        add_port(addPortForm.number_ap.data, sbc)
        return redirect(url_for('settings', sbc=sbc))
    # поиск информации о текущем состоянии каждого одноплатника
    list_sbc_status = Sbc.query.all()
    sbc_ports = Forwarding.query.filter_by(sbc_id=sbc).all()
    forms = {'addPort': addPortForm}
    return render_template('contents/settings.html', current_sbc=current_sbc, list_sbc_status=list_sbc_status, sbc_ports=sbc_ports, forms=forms)


@app.route("/open_port/<int:sbc>/<int:port_id>")
@login_required
def open_port(sbc, port_id):
    """
    Открытие порта 
    """
    # ищем порт назначения
    dest_port = Forwarding.query.get(port_id)
    if not dest_port:
        flash('Не удалось открыть порт. Порте не найден', 'error')
        return redirect(url_for('settings', sbc=sbc))
    # ищем адрес назначения
    last_date = db.session.query(func.max(Logs.date)).filter_by(sbc_id=sbc)
    dest_address = db.session.query(Logs.virtualAddress).filter_by(
        sbc_id=sbc, date=last_date).first()
    if not dest_address:
        flash('Не удалось открыть порт. Не найден адрес клиента', 'error')
        return redirect(url_for('settings', sbc=sbc))
    # выделяем порт
    dedicated_port = search_free_port()
    if dedicated_port:
        # запускаем переадресацию
        process = start_port_forwarding(
            dest_address[0], dest_port.destination_port, dedicated_port)
        # обновляем записи в бд
        dest_port.date_open = datetime.now()
        dest_port.dedicated_port = dedicated_port
        dest_port.time_live = TIME_WAITING
        dest_port.pid = 112
        try:
            db.session.add(dest_port)
            db.session.commit()
        except:
            db.session.rollback()
            process.kill()
            flash('Не удалось открыть порт', 'error')
    else:
        flash('Не удалось открыть порт. Все порты заняты', 'error')
    return redirect(url_for('settings', sbc=sbc))


@app.route("/extend_time/<int:sbc>/<int:port_id>")
@login_required
def extend_time(sbc, port_id):
    forwarding = Forwarding.query.filter_by(sbc_id=sbc, id=port_id).first()
    if not forwarding:
        abort(404)
    if forwarding.pid:
        forwarding.time_live += 60
        db.session.add(forwarding)
        try:
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
        # если уже открыт
        if forwarding.pid:
            continue
        # выделяем порт
        dedicated_port = search_free_port()
        if dedicated_port:
            process = start_port_forwarding(
                dest_address[0], dest_port.destination_port, dedicated_port)
            forwarding.date_open = datetime.now()
            forwarding.dedicated_port = dedicated_port
            forwarding.time_live = TIME_WAITING
            forwarding.pid = 112
            db.session.add(forwarding)
            try:
                db.session.commit()
            except:
                process.kill()
                db.session.rollback()
        else:
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
    if forwarding.pid:
        stop_port_forwarding(forwarding.pid)
    Forwarding.query.filter_by(id=port_id).delete()
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось удалить порт")
    return redirect(url_for('settings', sbc=sbc))


@app.route("/users/", methods=['post', 'get'])
@login_required
def user_managment():
    create_user_form = CreateUserForm()
    if create_user_form.validate_on_submit():
        if create_user_form.password.data == create_user_form.second_password.data:
            user = User(username=create_user_form.username.data)
            user.set_password(create_user_form.password.data)
            try:
                db.session.add(user)
                db.session.commit()
            except:
                db.session.rollback()
                flash("Не удалось создать клиента")
    list_users = User.query.all()
    list_sbc_status = Sbc.query.all()
    return render_template('contents/user_managment.html', list_sbc_status=list_sbc_status, list_users=list_users, create_user_form=create_user_form)


@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    if User.query.count() <= 1:
        flash("Не удалось удалить пользователя. Нельзя удалить последнего пользователя", 'error')
        return redirect(url_for('user_managment'))
    user = User.query.get(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось удалить пользователя", 'error')
        return redirect(url_for('user_managment'))
    return redirect(url_for('user_managment'))


@app.route("/delete_client/<int:sbc_id>")
@login_required
def delete_client(sbc_id):
    sbc = Sbc.query.get(sbc_id)
    try:
        db.session.delete(sbc)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось удалить клиента")
        return redirect(url_for('index', sbc=sbc_id))
    return redirect(url_for('main'))


@app.route("/clear_logs/<int:sbc_id>")
@login_required
def clear_logs(sbc_id):
    Logs.query.filter_by(sbc_id=sbc_id).delete()
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("Не удалось отчистить журнал подключений")
    return redirect(url_for('index', sbc=sbc_id))


def add_port(port, sbc):
    """
    Добавление номера порта к списку открываемых портов для sbc одноплатника
    """
    if db.session.query(Forwarding.id).filter_by(sbc_id=sbc, destination_port=port).count():
        flash("Порт уже добавлен", 'error')
        return redirect(url_for('settings', sbc=sbc))

    port = Forwarding(destination_port=port, sbc_id=sbc)
    db.session.add(port)
    try:
        db.session.commit()
    except:
        db.session.rollback()


def sbc_status():
    """
    выборка из базы всех ок и их текущих состояний 
    """
    # выборка последней даты подключения каждого ок из logs
    last_connect_date = db.session.query(Logs.sbc_id, func.max(Logs.date).label(
        'max_date')).group_by(Logs.sbc_id).subquery('last_connect_date')
    # объединение таблиц Sbc и Logs по полученным датам
    query = db.session.query(Sbc, Logs).outerjoin(
        last_connect_date, Sbc.id == last_connect_date.c.sbc_id)
    res = query.outerjoin(Logs, and_(
        Logs.sbc_id == last_connect_date.c.sbc_id, Logs.date == last_connect_date.c.max_date))
    return res


def update_description(id, text):
    """
    Обновление (добавление) описания у ок
    """
    sbc = Sbc.query.get(id)
    sbc.description = text
    try:
        db.session.add(sbc)
        db.session.commit()
    except:
        db.session.rollback()
