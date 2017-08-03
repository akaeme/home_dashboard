from flask import Flask, render_template, url_for, request, redirect, jsonify
from wtforms import Form, StringField, PasswordField, validators
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from threading import Thread, Timer
from flask_socketio import SocketIO
import os
import RPi.GPIO as GPIO
from temperature import dht11
import time
import datetime


app = Flask(__name__)
app.threaded = True
bcrypt = Bcrypt(app)
socket_io = SocketIO(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['HOMEDASHBOARD_MAIL']
app.config['MAIL_PASSWORD'] = os.environ['HOMEDASHBOARD_MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///home_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

MESSAGE = 'Dear admin, \n\n\t%s ended up registering on the Home Dashboard Platform, with the email %s.\n\t' \
          'Please go to the platform and confirm the access request.\n\nRegards,\n\t Home Dashboard\n\t ' \
          'homedashboard.no.reply@gmail.com'

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin=17)

def read_temperature():
    result = instance.read()
    if result.is_valid():
        # print("Last valid input: " + str(datetime.datetime.now()))
        socket_io.emit('values', {'temperature':result.temperature, 'humidity':result.humidity})
    Timer(2.0, read_temperature).start()



@socket_io.on('start')
def handleMessage(msg):
    print('Message: ', msg)
    read_temperature()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    register_form = UserRegisterForm(request.form, prefix="register-form")
    login_form = UserLoginForm(request.form, prefix="login-form")
    return render_template('index.html', register_form=register_form, login_form=login_form)


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
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/database/')
def database():
    return render_template('database.html')


@app.route('/streaming/')
# @login_required
def streaming():
    # logout_user()
    return render_template('streaming.html')


@app.route('/room_control/')
# @login_required
def room_control():
    return render_template('room_control.html')


@app.route('/home_automation/')
def home_automation():
    return render_template('home_automation.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    form = UserLoginForm(prefix='login-form', username=username, password=password)
    validation = form.validate()
    if request.method == 'POST' and validation:
        results = User.query.filter_by(username=username).all()
        if len(results) > 0:
            user = results[0]
            if user.allowed:
                if bcrypt.check_password_hash(user.password, password):
                    login_user(user)
                    return jsonify(success='')
                else:
                    return jsonify(error={'password': 'Wrong password'})
            else:
                return jsonify(error={'authorization': 'False'})
        else:
            return jsonify(error={'username': 'Username does not exist'})


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()


@app.route('/register/', methods=['GET', 'POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    confirm = request.json['confirm']
    email = request.json['email']
    form = UserRegisterForm(prefix='register-form', username=username, email=email, password=password, confirm=confirm)
    validation = form.validate()
    if request.method == 'POST' and validation:
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)
        results = User.query.filter_by(username=username).all()
        if len(results) > 0:
            error_dict = {'username': 'Username already taken'}
            return jsonify(error=error_dict)
        else:
            user = User(username=username, email=email, password=password, allowed=False)
            db.session.add(user)
            db.session.commit()
            send_email(subject='New Register Request', sender=os.environ['HOMEDASHBOARD_MAIL'],
                       recipients=[os.environ['HOMEDASHBOARD_MAIL']],
                       text_body=MESSAGE % (username, email))
            return jsonify(success='')
    else:
        error_dict = {}
        error_keys = form.errors.keys()
        if 'username' in error_keys:
            error_dict['username'] = form.errors['username']
        if 'email' in error_keys:
            error_dict['email'] = form.errors['email']
        if 'password' in error_keys:
            error_dict['password'] = form.errors['password']
        return jsonify(error=error_dict)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(50), unique=False)
    password = db.Column(db.String(150))
    allowed = db.Column(db.Boolean)

    def __init__(self, username, email, password, allowed):
        self.username = username
        self.email = email
        self.password = password
        self.allowed = allowed

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserLoginForm(Form):
    username = StringField('Username', [validators.DataRequired(message='May not be null or empty'),
                                        validators.Length(min=4, max=25)],
                           render_kw={"placeholder": "username"})
    password = PasswordField('Password', [validators.DataRequired(message='May not be null or empty'),
                                          validators.Length(min=6, max=30)],
                             render_kw={"placeholder": "password"})


class UserRegisterForm(Form):
    username = StringField('Username', [validators.DataRequired(message='May not be null or empty'),
                                        validators.Length(min=4, max=25, message='Length must be between 4-25')],
                           render_kw={"placeholder": "username"})
    email = StringField('Email Address', [validators.Length(min=6, max=50, message='Invalid email')],
                        render_kw={"placeholder": "email"})
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ], render_kw={"placeholder": "password"})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "confirm password"})


if __name__ == '__main__':
    socket_io.run(app, host='0.0.0.0', debug=True)
