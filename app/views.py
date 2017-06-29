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
from app import app, login_manager
from app.user import User

sys.path.append('/home/jspell/Documents/dev')
from f5tools import gtm, ltm

all_users = {}


@login_manager.user_loader
def load_user(username):
    '''
    Loads user from the currently authenticated AD user
    '''
    try:
        if username in all_users.keys():
            user = User(username)
            user.id = username
            return user
    except:
        return None


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
                user = User(auth.user)
                login_user(user)
                '''if not next_is_valid(next):
                    return flask.abort(400)'''
                return redirect(url_for('f5tool'))
            else:
                raise ValueError('not member of AD group ')
        except ValueError as e:
            error = str(e) + " invalid credentials %s..." % username

    return render_template("login.html", form=myform, error=error)


@app.route('/f5tool', methods=['GET', 'POST'])
@login_required
def f5tool():
    error = None
    all_wide_ip = secret.get_wideip()
    form = MyBaseForm()
    gtmutil = gtm.GTMUtils()
    if request.method == 'POST':
        one_val = form.onesource.data
        onesourceapps_val = form.onesourceapps.data
        onesourceservices_val = form.onesourceservices.data
        if one_val or onesourceapps_val or onesourceservices_val:
            if one_val:
                gtmutil.switch_primary_gtm_pool(all_wide_ip[0])
            elif onesourceapps_val:
                gtmutil.switch_primary_gtm_pool(all_wide_ip[1])
            elif onesourceservices_val:
                gtmutil.switch_primary_gtm_pool(all_wide_ip[2])

    primary_sites = query_prime_pool(all_wide_ip, gtmutil)
    return render_template('f5form.html', form=form,
                           one=primary_sites['test.jspell.mhhs.org']['site'],
                           oneapps=None,
                           oneservices=None)


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


def query_prime_pool(pools, gtmutil):
    r_status = {}
    for pool in pools:
        r_status[pool] = gtmutil.get_primary_pool_member(pool)
    return r_status
