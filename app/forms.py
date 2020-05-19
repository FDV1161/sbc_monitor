from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import InputRequired, NumberRange
from wtforms.fields.html5 import IntegerField

class AddPortForm(FlaskForm):	
	"""
    форма для добавления номера порта к списку открываемых портов
    """
	number_ap = IntegerField('Номер порта', validators=[InputRequired(), NumberRange(min=1, max=65535)], render_kw={"placeholder": "Номер порта", 'min': '0', 'max':'65535'})
	submit = SubmitField('Добавить')


class OpenAllPortForm(FlaskForm):
    """
    форма для открытия всех портов
    """
    sbc_number_oap = HiddenField()
    submit = SubmitField('Закрыть')

class CloseAllPortForm(FlaskForm):
    """
    форма для закрытия всех портов
    """
    sbc_number_cap = HiddenField()
    submit = SubmitField('Закрыть')

class tableForm(FlaskForm):
    close_port = SubmitField('Закрыть')
    open_port = SubmitField('Открыть')
    del_port = SubmitField('Удалить')