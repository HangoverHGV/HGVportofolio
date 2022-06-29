from flask import Flask, render_template, redirect, url_for, send_file, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import inspect, create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import os
import webbrowser
from dotenv import load_dotenv
from keygen import generatepass
import convertpdf
from calculatorcubaj import Volum
from time import sleep


app = Flask(__name__)
#---------------------------------SQL----------------------------------------

load_dotenv()


db_user = os.getenv('MARIADB_USER')
db_databse = os.getenv('MARIADB_DATABASE')
db_pass = os.getenv('MARIADB_PASSWORD')
db_host = os.getenv('MARIADB_HOST')

uri = 'mysql+pymysql://'+ str(db_user) +':'+ str(db_pass) +'@'+ str(db_host) +'/'+ str(db_databse)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = generatepass()

db = SQLAlchemy(app)

class Rezultate(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    lungime = db.Column(db.String(50))
    diametru = db.Column(db.String(50))
    volumul = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), nullable = False, unique = True)
    name = db.Column(db.String(150), nullable = False)
    password = db.Column(db.String(150), nullable = False)
    calculator = db.relationship('Rezultate')

tblnamerez = Rezultate().__class__.__name__
tblnameusr = User().__class__.__name__

#------------------------------------CheckConnection---------------------------

for i in range(6):
    connected = True
    try:
        db.session.execute('SELECT 1')
    except:
        connected = False
    
    if connected:
        break
    else:
        sleep(3)


engine = create_engine(uri)
def GetTableName(name):
    exists = False
    tables = inspect(engine)
    for t_name in tables.get_table_names():
        if(t_name == name):
            exists = True
            break
        else:
            exists = False
    
    return exists



if GetTableName(tblnamerez) == False or GetTableName(tblnameusr) == False:
    db.create_all()


#------------------------------------authentication---------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#---------------------------------------Home------------------------------------

@app.route('/')
def index():
    return render_template('index.html', user=current_user)


#---------------------------------------Download CV------------------------------------

@app.route('/downcv')
def downloadcv():
    return send_file('mycv/CV_Hango_Bogdan_en.pdf', as_attachment=True)


#--------------------PDF Converter-----------------------------

@app.route('/pdfconvert')
def pdfconvert():
    return render_template('pdfconvert.html', user=current_user)

@app.route('/pdfconvert/convert', methods = ["POST"])
def convert():
    dir_path = r'files'
    convertpdf.CreateAndDelete(dir_path)
    
    savePath = 'files/'

    file = request.files['pdf']
    if not file:
        return redirect(url_for('pdfconvert'))
    file.save(savePath + file.filename)
    filePath = savePath + str(os.path.basename(file.filename))
    fileName, fileextension = os.path.splitext(file.filename)

    destination = 'files/' 
    path = 'files/' + fileName + '.docx'
    convertpdf.convert_pdf2docx(filePath, destination)
    print(convertpdf.convert_pdf2docx(filePath, destination))
    var = send_file(path, as_attachment=True)

    return var

#--------------------Calculator-----------------------------
vol = 0 
tot = 0
@app.route('/calculatorcubaj')
@login_required
def calculatorcubaj():
    total =0
    result = Rezultate.query.all()

    for i in result:
        if i.user_id == current_user.id:
            total += float(i.volumul)

    tot = round(total, 3)

    return render_template('calculatorcubaj.html', user=current_user, volum=vol, total = tot)

@app.route('/calculatorcubaj/calculate', methods = ["POST"])
def calculate():
    global vol, tot
    vol = 0  
    lungime = request.form['lungime']
    diametru = request.form['diametru']


    if lungime.isdigit() and diametru.isdigit():
        dimensions = Rezultate(lungime = lungime, diametru = diametru, volumul = Volum(lungime, diametru),user_id=current_user.id)
        db.session.add(dimensions)
        db.session.commit()
        vol = Volum(lungime, diametru)
    return redirect(url_for('calculatorcubaj'))

@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
def delete(id):
    row_to_delete = Rezultate.query.get(id)
    db.session.delete(row_to_delete)

    db.session.commit()
    return redirect(url_for('calculatorcubaj'))


#--------------------Sign UP-----------------------------

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(username=username).first()

        if user:
            flash('Emai already exists.', category='error')
        elif len(username) < 4:
            flash('Email must be greater that 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 !=password2:
            flash('Passwords don`t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(username=username, name=name, password = generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            # login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('login'))

    return render_template('signup.html', user=current_user)
#--------------------Log IN-----------------------------

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
            else:
                flash('Incorect password, try again.', category='error')
        else:
            flash('E-mail doesn`t exist!', category='error')
    
    return render_template('login.html', user=current_user)

#--------------------Log OUT-----------------------------

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))










#---------------RUN-----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)