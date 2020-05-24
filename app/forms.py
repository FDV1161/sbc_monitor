from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import InputRequired, NumberRange
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