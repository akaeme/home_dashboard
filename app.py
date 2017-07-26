import os
from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps
from flask_bcrypt import Bcrypt
from databaseUtils import connection
app = Flask(__name__)
bcrypt = Bcrypt(app)


@app.route('/')
def index():
    register_form = UserRegisterForm(request.form, prefix="register-form")
    login_form = UserLoginForm(request.form, prefix="login-form")
    return render_template('index.html', register_form=register_form, login_form=login_form)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('index'))
    return wrap


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/dashboard/')
#@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/database/')
def database():
    return render_template('database.html')


@app.route('/streaming/')
def streaming():
    return render_template('streaming.html')


@app.route('/room_control/')
def room_control():
    return render_template('room_control.html')


@app.route('/home_automation/')
def home_automation():
    return render_template('home_automation.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    username = request.args.get('username', default='', type=str)
    password = request.args.get('password', default='', type=str)
    form = UserLoginForm(prefix='login-form', username=username, password=password)
    print(form.username.data)
    print(form.password.data)
    print(form.validate())
    '''
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.password.data
        print(username, email)'''
    return jsonify(result='You are wise')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    username = request.args.get('username', default='', type=str)
    password = request.args.get('password', default='', type=str)
    confirm = request.args.get('confirm', default='', type=str)
    email = request.args.get('email', '', type=str)
    form = UserRegisterForm(prefix='register-form', username=username, email=email, password=password, confirm=confirm)

    '''if request.method == 'GET' and form.validate():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)
        con = connection()
        cursor = con.execute('SELECT * FROM admins WHERE username = ?', (username, ))
        results = cursor.fetchall()
        if len(results) > 0:
            return jsonify(invalid='username')
        else:
            con.execute('INSERT INTO admins(username, password, email) VALUES (?,?,?)', (username, password, email))
            con.commit()
            con.close()
            return jsonify(confirm='email')'''
    return jsonify(confirm='email')
    # return redirect(url_for('dashboard'))


class UserLoginForm(Form):
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)],
                           render_kw={"placeholder": "username"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6, max=30)],
                             render_kw={"placeholder": "password"})


class UserRegisterForm(Form):
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)],
                           render_kw={"placeholder": "username"})
    email = StringField('Email Address', [validators.Length(min=6, max=50)], render_kw={"placeholder": "email"})
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ], render_kw={"placeholder": "password"})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "confirm password"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
