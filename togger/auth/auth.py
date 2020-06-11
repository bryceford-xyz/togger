import flask_login
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_required, logout_user
from . import auth_api
from .auth_api import get_user, add_user, get_user_by_id

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")
login_manager = LoginManager()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('main', **request.args))
        else:
            return render_template('login.html', query_string=request.query_string.decode('utf-8'))
    email = request.form['email']
    user = get_user(email)
    if user and user.check_password(request.form['password']):
        flask_login.login_user(user)
        return redirect(url_for('main', **request.args))
    flash('Incorrect login or/and password. Please check it and try again')
    return redirect(url_for('auth.login', **request.args))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('main', **request.args))
        else:
            return render_template('register.html', query_string=request.query_string.decode('utf-8'))
    email = request.form['email']
    if get_user(email) is None:
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        user = add_user(username=email, password=request.form['password'], first_name=first_name, last_name=last_name)
        flask_login.login_user(user, remember=True)
        return redirect(url_for('main', **request.args))
    flash('Such user already exists')
    return redirect(url_for('auth.register', **request.args))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route("/profile")
@login_required
def render_profile():
    return render_template('profile.html')


@bp.route("/users", methods=['PUT', 'POST'])
@login_required
def update_user():
    auth_api.update_user(first_name=request.form['firstName'], last_name=request.form['lastName'])
    return '', 204


@login_manager.user_loader
def user_loader(id):
    return get_user_by_id(id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('auth.login', **request.args))


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
