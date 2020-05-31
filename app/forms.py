from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, NumberRange, Optional
from wtforms.fields.html5 import IntegerField

class AddPortForm(FlaskForm):	
	"""
    форма для добавления номера порта к списку открываемых портов
    """
	number_ap = IntegerField('Номер порта', validators=[InputRequired(), NumberRange(min=1, max=65535)], render_kw={"placeholder": "Номер порта", 'min': '0', 'max':'65535'})
	submit = SubmitField('Добавить')

class DescriptionForm(FlaskForm):
    text = TextAreaField()

class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[InputRequired()])
    password = PasswordField("Пароль", validators=[InputRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")

class CreateUserForm(FlaskForm):
    username = StringField("Логин", validators=[InputRequired()])
    password = PasswordField("Пароль", validators=[InputRequired()])
    second_password = PasswordField("Повторите пароль", validators=[InputRequired()])

class CreateCertificateForm(FlaskForm):
    name = StringField("Название сертификата", validators=[InputRequired()])

class UserRuleForm(FlaskForm):
    user = SelectField('Пользователь', coerce=int)
    rule = SelectField('Права', coerce=int, choices=[(1, 'Администратор'), (0, 'Пользователь')])

class OnForwardingUserForm(FlaskForm):
    user = SelectField('Пользователь', coerce=int)
    client = SelectField('Клиент', coerce=int)
    port = IntegerField('Порт', validators=[Optional(),NumberRange(min=1, max=65535)], render_kw={"placeholder": "Номер порта", 'min': '0', 'max':'65535'})

