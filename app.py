from flask import Flask, render_template, url_for, redirect, request, session, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, db
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pandas as pd

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred, {
  'databaseURL': "https://mitra-cemerlang-default-rtdb.asia-southeast1.firebasedatabase.app"
})

wilayah = db.reference('/wilayah')

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
      'levelAkses': 'Basic'
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

@app.route('/formulir/<uid>', methods = ['GET', 'POST'])
@login_required
def formulir(uid):
  kota = dataBase.collection('T_Umum_Wilayah_Kota').order_by('Kota', direction = firestore.Query.ASCENDING).stream()
  kt = []
  for kot in kota:
    k = kot.to_dict()
    k['id'] = kot.id
    kt.append(k)
    
  provinsi = dataBase.collection('T_Umum_Wilayah_Provinsi').order_by('Provinsi', direction = firestore.Query.ASCENDING).stream()
  prov = []
  for pr in provinsi:
    p = pr.to_dict()
    p['id'] = pr.id
    prov.append(p)
    
  if request.method == 'POST':
    data = {
      # KATEGORI WAJIB PAJAK
      'kategoriWajibPajak': request.form['kwp'],
      'statusCabangPusat': request.form['status'],
      'npwpSuami': request.form['npwpSuami'],
      'npwpPusat': request.form['npwpPusat'],
      # IDENTITAS WAJIB PAJAK
      'gelarDepan': request.form['gelarDp'],
      'gelarBelakang': request.form['gelarBl'],
      'tempatLahir': request.form['tempatLahir'],
      'tanggalLahir': request.form['tanggalLahir'],
      'statusNikah': request.form['statusNikah'],
      'kebangsaan': request.form['kebangsaan'],
      'nikPassport': request.form['nikPassport'],
      'nomorTelepon': request.form['telpWP'],
      'nomorHp': request.form['hpWP'],
      # SUMBER PENGHASILAN UTAMA
      'pekerjaanDlmHubKerja': request.form['pdhk'],
      'kegiatanUsaha': request.form['kegUsaha'],
      'merkDagangUsaha': request.form['merkDagUsh'],
      'karyawan': request.form['karyawan'],
      'metode': request.form['metode'],
      # ALAMAT TEMPAT TINGGAL
      'jalan': request.form['jalan'],
      'blok': request.form['blok'],
      'nomorRumah': request.form['nomor'],
      'RT': request.form['rt'],
      'RW': request.form['rw'],
      'kodeWilayah': request.form['kodeWilayah'],
      'kelurahanDesa': request.form['lurahDesa'],
      'kecamatan': request.form['kecamatan'],
      'kabKota': request.form['kabKota'],
      'provinsi': request.form['provinsi'],
      'kodePos': request.form['kodePos'],
      'teleponRumah': request.form['telp'],
      'fax': request.form['fax'],
      'handphone': request.form['handphone'],
      # INFO TAMBAHAN
      'tanggungan': request.form['tanggungan'],
      'kisaranPenghasilan': request.form['kisaran']
    }
    dataBase.collection('users').document(uid).set(data, merge = True)
    flash('Formulir berhasil di input', 'success')
    return redirect(url_for('dashboard'))
  session['user'] = dataBase.collection('users').document(session['userId']).get().to_dict()
  return render_template('formulir.html', kota = kt, provinsi = prov)

@app.route('/dashboard')
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/wilayah_kota')
@login_required
def wilayahKota():
  kota = dataBase.collection('T_Umum_Wilayah_Kota').order_by('Kota', direction = firestore.Query.ASCENDING).stream()
  kt = []
  for kot in kota:
    k = kot.to_dict()
    k['id'] = kot.id
    kt.append(k)
  return render_template('wilayahKota.html', data = kt)

@app.route('/fire_base', methods = ['GET', 'POST'])
@login_required
def fire_base():
  if request.method == "POST":
    data = {
      'Provinsi': request.form['tambahKota']
    }

    wilayah.child('Provinsi').push(data)
    flash('kota terdaftar', 'success')
    return redirect(url_for('fire_base'))
  return render_template('fire_base.html')

@app.route('/tambah_kota', methods = ['GET', 'POST'])
@login_required
def tambah_kota():
  if request.method == 'POST':
    data = {
      'Kota': request.form['tambahKota']
    }
    
    kotaS = dataBase.collection('T_Umum_Wilayah_Kota').where('Kota', '==', data['Kota']).stream()
    kota = {}
    for kt in kotaS:
      kota = kt.to_dict()
    if kota:
      flash('Maaf, kota sudah terdaftar', 'danger')
      return redirect(url_for('tambah_kota'))
    
    dataBase.collection('T_Umum_Wilayah_Kota').document().set(data)
    flash('Berhasil tambah kota', 'success')
    return redirect(url_for('wilayahKota'))
  return render_template('tambah_kota.html')

@app.route('/kota/ubah/<uid>', methods = ['GET', 'POST'])
@login_required
def ubah_kota(uid):
  if request.method == 'POST':
    data = {
      'Kota': request.form['tambahKota']
    }
    
    kotaS = dataBase.collection('T_Umum_Wilayah_Kota').where('Kota', '==', data['Kota']).stream()
    kota = {}
    for kt in kotaS:
      kota = kt.to_dict()
    if kota:
      flash('Maaf, kota sudah terdaftar', 'danger')
      return redirect(url_for('wilayahKota'))
    
    dataBase.collection('T_Umum_Wilayah_Kota').document(uid).set(data, merge = True)
    flash('Kota berhasil diubah', 'success')
    return redirect(url_for('wilayahKota'))
  user = dataBase.collection('T_Umum_Wilayah_Kota').document(uid).get().to_dict()
  user['id'] = uid
  return render_template('ubah_kota.html', user = user)

@app.route('/kota/hapus/<uid>')
@login_required
def hapus_kota(uid):
  dataBase.collection('T_Umum_Wilayah_Kota').document(uid).delete()
  flash('Kota berhasil dihapus', 'success')
  return redirect(url_for('wilayahKota'))

@app.route('/wilayah_provinsi')
@login_required
def wilayahProvinsi():
  provinsi = dataBase.collection('T_Umum_Wilayah_Provinsi').order_by('Provinsi', direction = firestore.Query.ASCENDING).stream()
  prov = []
  for pr in provinsi:
    p = pr.to_dict()
    p['id'] = pr.id
    prov.append(p)
  return render_template('wilayahProvinsi.html', data = prov)

@app.route('/tambah_provinsi', methods = ['GET', 'POST'])
@login_required
def tambah_provinsi():
  if request.method == 'POST':
    data = {
      'Provinsi': request.form['tambahProvinsi']
    }
    
    provinsi = dataBase.collection('T_Umum_Wilayah_Provinsi').where('Provinsi', '==', data['Provinsi']).stream()
    prov = {}
    for p in provinsi:
      prov = p.to_dict()
    if prov:
      flash('Maaf, Provinsi sudah terdaftar', 'danger')
      return redirect(url_for('wilayahProvinsi'))
    
    dataBase.collection('T_Umum_Wilayah_Provinsi').document().set(data)
    flash('Berhasil tambah provinsi', 'success')
    return redirect(url_for('wilayahProvinsi'))
  return render_template('tambah_provinsi.html')

@app.route('/provinsi/ubah/<uid>', methods = ['GET', 'POST'])
@login_required
def ubah_provinsi(uid):
  if request.method == 'POST':
    data = {
      'Provinsi': request.form['tambahProvinsi']
    }
    
    provinsi = dataBase.collection('T_Umum_Wilayah_Provinsi').where('Provinsi', '==', data['Provinsi']).stream()
    prov = {}
    for p in provinsi:
      prov = p.to_dict()
    if prov:
      flash('Maaf, Provinsi sudah terdaftar', 'danger')
      return redirect(url_for('wilayahProvinsi'))
    
    dataBase.collection('T_Umum_Wilayah_Provinsi').document(uid).set(data, merge = True)
    flash('Provinsi berhasil diubah', 'success')
    return redirect(url_for('wilayahProvinsi'))
  user = dataBase.collection('T_Umum_Wilayah_Provinsi').document(uid).get().to_dict()
  user['id'] = uid
  return render_template('ubah_provinsi.html', user = user)

@app.route('/provinsi/hapus/<uid>')
@login_required
def hapus_provinsi(uid):
  dataBase.collection('T_Umum_Wilayah_Provinsi').document(uid).delete()
  flash('Kota berhasil dihapus', 'success')
  return redirect(url_for('wilayahProvinsi'))

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
  # return jsonify(client)

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

@app.route('/clients/lihat/<uid>')
def lihat_clients(uid):
  user = dataBase.collection('users').document(uid).get().to_dict()
  return render_template('lihat_clients.html', user = user)

@app.route('/clients/hapus/<uid>')
def hapus_clients(uid):
  dataBase.collection('users').document(uid).delete()
  flash('Data User berhasil dihapus', 'danger')
  return redirect(url_for('clients'))

@app.route('/agents')
@login_required
def agents():
  return render_template('agents.html')

@app.route('/logout')
def logout():
  session.clear()
  return render_template('login.html')

@app.route('/dataExcelForm', methods = ['GET', 'POST'])
def dataExcelForm():
  return render_template('dataExcelForm.html')

@app.route('/dataExcel', methods = ['GET', 'POST'])
def dataExcel():
  if request.method == 'POST':
    file = request.form['importExcel']
    data = pd.read_excel(file)
  return render_template('dataExcel.html', data = data.to_html())


if __name__ == '__main__':
    app.run(debug=True)