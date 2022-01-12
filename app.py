from flask import Flask, render_template, url_for, redirect, request, session
import firebase_admin
from firebase_admin import credentials, firestore
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

dataBase = firestore.client()

app = Flask(__name__)
app.secret_key = 'mitracemerlang'

# fungsi untuk login required
def login_required(f):
  @wraps(f)
  def wrapper(*args , **kwargs):
    if 'user' in session:
      return f(*args, **kwargs)
    else:
      flash('Maaf anda belum login', 'danger')
      return redirect(url_for('login'))
  return wrapper

# fungsi untuk admin required
def admin_required(f):
  @wraps(f)
  def wrapper(*args , **kwargs):
    if 'user' in session:
      if session['user']['access'] == 'admin':
        return f(*args, **kwargs)
      else:
        flash('Maaf anda bukan admin', 'danger')
        return redirect(url_for('dashboard'))
    else:
      flash('Maaf anda belum login', 'danger')
      return redirect(url_for('login'))
  return wrapper

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/index_new')
def index2_new():
  return render_template('index_new.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    data = {
      'username': request.form['username'],
      'password': request.form['password']
    }
    
    users = dataBase.collection('users').where('username', '==', data['username']).stream()
    user = {}
    for us in users:
      user = us.to_dict()
    if user:
      if check_password_hash(user['password'], data['password']):
        session['user'] = user
        session['userId'] = us.id
        return redirect(url_for('dashboard'))
      else:
        flash('Maaf, password anda salah..!', 'danger')
        return redirect(url_for('login'))
    else:
      flash('Email anda belum diregistrasi, silahkan ragistrasi email anda', 'warning')
      return redirect(url_for('login'))
    
  return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
  if request.method == 'POST':
    data = {
      'nama': request.form['nama'],
      'username': request.form['username'],
      'email': request.form['email'],
      'password': request.form['password'],
      'levelAkses': 'Basic Level Akses'
    }
    
    users = dataBase.collection('users').where('email','==', data['email']).stream()
    user = {}
    for us in users:
      user = us.to_dict()
    if user:
      flash('Email sudah terdaftar', 'danger')
      return redirect(url_for('register'))
    
    users = dataBase.collection('users').where('username','==', data['username']).stream()
    user = {}
    for us in users:
      user = us.to_dict()
    if user:
      flash('Username sudah digunakan', 'danger')
      return redirect(url_for('register'))
    
    data['password'] = generate_password_hash(request.form['password'], 'sha256')
    dataBase.collection('users').document().set(data)
    flash('Selamat..! Akun sudah diregistrasi', 'success')
    return redirect(url_for('login'))
    
  return render_template('register.html')

@app.route('/daftar')
@login_required
def daftar():
  return render_template('daftar.html')

@app.route('/daftar_new')
@login_required
def daftar_new():
  return render_template('daftar_new.html')

@app.route('/dashboard')
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/myprofile')
@login_required
def myprofile():
  session['user'] = dataBase.collection('users').document(session['userId']).get().to_dict()
  return render_template('myprofile.html')

@app.route('/myprofile/ubah/<uid>', methods = ['GET', 'POST'])
@login_required
def ubah_profile(uid):
  if request.method == 'POST':
    data = {
      'nama': request.form['nama'],
      'username': request.form['username'],
      'email': request.form['email'],
      'alamat': request.form['alamat'],
      'company': request.form['company'],
      'npwp': request.form['npwp']
    }
    dataBase.collection('users').document(uid).set(data, merge = True)
    flash('Selamat, profil anda berhasil diubah', 'success')
    return redirect(url_for('myprofile'))
  session['user'] = dataBase.collection('users').document(session['userId']).get().to_dict()
  return render_template('ubah_profile.html')

@app.route('/clients')
@login_required
def clients():
  clients = dataBase.collection('users').stream()
  client = []
  for cl in clients:
    c = cl.to_dict()
    c['id'] = cl.id
    client.append(c)
  return render_template('clients.html', data = client)

@app.route('/clients/ubah/<uid>', methods = ['GET', 'POST'])
@login_required
def ubah_clients(uid):
  if request.method == 'POST':
    data = {
      'nama': request.form['nama'],
      'username': request.form['username'],
      'levelAkses': request.form['levelAkses']
    }
    dataBase.collection('users').document(uid).set(data, merge = True)
    flash('Selamat! data anda berhasil di ubah', 'primary')
    return redirect(url_for('clients'))
  user = dataBase.collection('users').document(uid).get().to_dict()
  user['id'] = uid
  return render_template('ubah_clients.html', user = user)

@app.route('/agents')
@login_required
def agents():
  return render_template('agents.html')

@app.route('/logout')
def logout():
  session.clear()
  return render_template('login.html')




if __name__ == '__main__':
    app.run(debug=True)
