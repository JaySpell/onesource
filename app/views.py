import sys
from app.MyForm import LoginForm, BoolWideIP, MyBaseForm
from flask import (Flask, render_template, flash, redirect,
                   request, url_for, session, escape, g, request)
from flask_login import (current_user, login_user,
                         logout_user, login_required)
from wtforms import BooleanField, Form
from app.ad_auth import ADAuth
import ldap
from app import secret
from app import app

sys.path.append('/home/jspell/Documents/dev')
from f5tools import gtm, ltm


@app.route('/')
@app.route('/index')
def index():
    return render_template('test.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated == True:
        error = 'Already logged in...'
        return redirect(url_for('f5tool'))

    myform = LoginForm()
    if myform.validate_on_submit():
        '''Get the username / password from form'''
        username = myform.username.data
        password = myform.password.data
        '''Attempt login using the ADAuth class'''
        auth = ADAuth(username, password)
        try:
            if auth.check_group_for_account() == True:
                all_users[username] = None
                user = User(unicode(auth.user))
                login_user(user)
                '''if not next_is_valid(next):
                    return flask.abort(400)'''
                return redirect(url_for('f5tool'))
            else:
                raise ValueError('not member of AD group ')
        except ValueError as e:
            error = unicode(e) + " invalid credentials %s..." % username

    return render_template("login.html", form=myform, error=error)


@app.route('/f5tool', methods=['GET', 'POST'])
def f5tool():
    error = None
    all_wide_ip = secret.get_wideip()

    if request.POST == 'POST':
        one_val = form.one.data
        onesourceapps_val = form.onesourceapps.data
        onesourceservices_val = form.onesourceservices.data
        if one_val or onesourceapps_val or onesourceservices_val:
            if one_val:
                gtmutil.switch_primary_gtm_pool(all_wide_ip['one'])
            elif onesourceapps_val:
                gtmutil.switch_primary_gtm_pool(all_wide_ip['onesourceapps'])
            elif onesourceservices_val:
                gtmutil.switch_primary_gtm_pool(all_wide_ip['onesourceservices'])

    form = MyBaseForm()
    primary_sites = query_prime_pool(all_wide_ip)
    return render_template('f5form.html', form=form
                           one=primary_sites['one'],
                           oneapps=primary_sites['onesourceapps'],
                           oneservices=primary_sites['oneservices'])


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')


def wide_ip_view(all_wide_ip):
    class F(MyBaseForm):
        pass

    for wideip in all_wide_ip:
        setattr(F, label, BooleanField())

    form = F()

    return form


def query_prime_pool(pools):
    gtmutil = f5tool.GTMUtils()
    r_status = {}
    for pool in pools:
        r_status[pool] = gtmutil.get_primary_pool_member(pool)
    return r_status
