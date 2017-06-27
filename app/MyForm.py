__author__ = 'jspell'
from flask_wtf import Form
from wtforms import (StringField, SelectField,
                     validators, BooleanField,
                     RadioField, PasswordField,
                     FieldList, FormField, StringField)
from wtforms.validators import (DataRequired, Required,
                                Regexp, Length, InputRequired)

GTM_WIDEIP = ['test.jspell.mhhs.org']


class LoginForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_.]+$',
                message=("Username should be one word, letters, numbers"
                         " and underscores only.")
            )
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6),
        ])


class MyBaseForm(Form):
    one_status = StringField()
    one_app_status = StringField()
    one_service_status = StringField()
    onesource = BooleanField('onesource.memorialhermann.org')
    onesourceapps = BooleanField('onesourceapps.mhhs.org')
    onesourceservices = BooleanField('onesourceservices')


class BoolWideIP(Form):
    pass
    #wideips = FieldList(FormField(BooleeanForm), min_entries=1)
