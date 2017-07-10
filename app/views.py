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
from app.MyForm import SelectForm

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
        # Get the username / password from form
        username = myform.username.data
        password = myform.password.data

        # Attempt login using the ADAuth class
        auth = ADAuth(username, password)
        try:
            if auth.check_group_for_account() == True:
                all_users[username] = None
                user = User(auth.user)
                login_user(user)
                return redirect(url_for('f5tool'))
            else:
                raise ValueError('not member of AD group ')
        except ValueError as e:
            error = str(e) + " invalid credentials %s..." % username

    return render_template("login.html", form=myform, error=error)


@app.route('/f5tool', methods=['GET', 'POST'])
#@login_required
def f5tool():
    error = None
    all_wide_ip = secret.get_wideip()
    print(all_wide_ip)
    form = SelectForm()

    # Determine primary site for all sites
    gtmutil = gtm.GTMUtils()
    primary_sites = query_prime_pool(all_wide_ip, gtmutil)
    #session['primary_sites'] = primary_sites
    #session['gtmutil'] = gtmutil

    # If POST then switch sites / email
    if request.method == 'POST':
        1 / 0
        # Setup email params
        email_dict = {}
        email_dict['sc_account'] = current_user
        email_dict['sites'] = []

        # Find which of the checkboxes have been selected
        select = {}
        for name, value in form.data.items():
            select[name] = value
        # For each checked perform failover / add to email
        for k, v in select.items():
            if v:
                gtmutil.switch_primary_gtm_pool(k)
                email_dict['sites'].append(k)
                email_dict['site_before'] = primary_sites[k]['site']

        # Send email
        send_email(email_dict)

    form = _create_form(all_wide_ip)
    a_form = form()
    1 / 0
    return render_template('f5form.html', form=a_form)


@app.route('/test', methods=['GET', 'POST'])
def test():
    all_wide_ip = secret.get_wideip()
    first_wide_ip = all_wide_ip.pop(0)
    form = SelectForm.append_field(first_wide_ip, BooleanField(first_wide_ip))
    for wide_ip in all_wide_ip:
        form.append_field(wide_ip, BooleanField(wide_ip))
        print(form)
    a_form = form()
    return render_template('test.html', form=a_form)


def query_prime_pool(pools, gtmutil):
    r_status = {}
    for pool in pools:
        r_status[pool] = gtmutil.get_primary_pool_member(pool)
    return r_status


def _create_form(all_wide_ip):
    # Create form - a checkbox per wideip from config file
    # must create form before iterating (pop first value)
    first_wide_ip = all_wide_ip.pop(0)
    form = SelectForm.append_field(first_wide_ip, BooleanField(first_wide_ip))

    for wide_ip in all_wide_ip:
        form.append_field(wide_ip, BooleanField(wide_ip))

    return form


def send_email(email_dict):
    '''
    Will send an email to users specified in ADMINS
    with information for customer name, cost center &
    the support center rep who filled the request
    param: email_dict({
                sc_rep: 'userid', site_before: 'SITE ID',
                site_after: 'SITE ID', sites: ['one', 'two', 'three']
                })
    return: email send status
    '''
    from flask_mail import Message
    from app import mail
    from flask import render_template

    MAIL_SERVER = secret.get_mail_server()
    MAIL_PORT = secret.get_mail_port()
    MAIL_USE_TLS = secret.get_mail_tls()
    MAIL_USE_SSL = secret.mail_use_ssl()
    ADMINS = secret.get_admins()

    if email_dict['site_before'] == 'TMC':
        email_dict['site_after'] = 'MC'
    else:
        email_dict['site_after'] = 'TMC'

    msg = Message('OneSource F5 Failover', sender='OneSource@mhhs.org',
                  recipients=ADMINS)

    msg.body = render_template('f5_failover.txt',
                               sc_account=email_dict['sc_account'],
                               site_before=email_dict['site_before'],
                               site_after=email_dict['site_after'],
                               sites=email_dict['sites']
                               )
    msg.html = render_template('f5_failover_email.html',
                               sc_account=email_dict['sc_account'],
                               site_before=email_dict['site_before'],
                               site_after=email_dict['site_after'],
                               sites=email_dict['sites']
                               )

    try:
        mail.send(msg)
        return "Email sent..."
    except:
        return "No email sent..."
