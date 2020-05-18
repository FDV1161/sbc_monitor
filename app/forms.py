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

class DeletePortForm(FlaskForm):
    """
    форма для удаления номера порта из списка открываемых портов
    """
    number_dp = HiddenField()
    submit = SubmitField('Удалить')

class OpenPortForm(FlaskForm):
    """
    форма для открытия конкретного порта
    """
    number_op = HiddenField()
    submit = SubmitField('Открыть')

class ClosePortForm(FlaskForm):
    """
    форма для закрытия конкретного порта
    """
    number_cp = HiddenField()
    submit = SubmitField('Закрыть')

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

