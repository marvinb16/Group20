from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        activeUser = User.query.filter_by(username=username).first()
        if activeUser:
            if check_password_hash(activeUser.password, password):
                flash('Logged in successfully.', category = 'success')
                login_user(activeUser, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect password, try again.', category = 'error')
        else:
            flash("Username does not exist.", category='error')

    return render_template("login.html", activeUser = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == "POST":
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        activeUser = User.query.filter_by(username=username).first()
        if activeUser:
            flash('Username is unavailable', category='error')
        elif len(username) < 4:
            flash('Username must be longer than 4 characters.', category='error')
        elif len(password1) < 6:
            flash('Password must be longer than 6 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            new_user = User(username=username, password=generate_password_hash(password2, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash('Account successfully created.', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.index'))

    return render_template("signUp.html", activeUser = current_user)