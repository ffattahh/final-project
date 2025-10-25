from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import (
    get_guru_by_username, get_siswa_by_username, insert_qr_token,
    verify_token, insert_absen_by_id, get_absensi_by_id_siswa, get_all_absensi
)
import os, qrcode, uuid, subprocess, sys
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "change_this_secret"
OUT_DIR = os.path.join('static', 'qrcodes')
os.makedirs(OUT_DIR, exist_ok=True)

TOKEN_TTL_SECONDS = 300  # 5 minutes

# ---------- routes ----------
@app.route('/')
def index():
    role = request.args.get('role', 'guru')
    return render_template('index.html',  role=role)

# login guru
@app.route('/login_guru', methods=['POST'])
def login_guru():
    username = request.form.get('username')
    password = request.form.get('password')
    guru = get_guru_by_username(username)
    if not guru or guru['password'] != password:
        return "Login gagal: username/password salah", 401
    session.clear()
    session['guru'] = guru['username']
    session['nama_guru'] = guru['nama_guru']
    return redirect(url_for('guru_dashboard'))

@app.route('/guru')
def guru_dashboard():
    if 'guru' not in session:
        return redirect(url_for('index'))
    absensi = get_all_absensi()
    return render_template('guru.html', nama=session.get('nama_guru'), absensi=absensi)

@app.route('/generate_token', methods=['POST'])
def generate_token():
    if 'guru' not in session:
        return jsonify({'status':'error','message':'Unauthorized'}), 401
    token = str(uuid.uuid4())
    expires_dt = datetime.now() + timedelta(seconds=TOKEN_TTL_SECONDS)
    insert_qr_token(token, expires_dt)
    filename = f"token_{datetime.now().strftime('%Y%m%d%H%M%S')}_{token[:8]}.png"
    filepath = os.path.join(OUT_DIR, filename)
    img = qrcode.make(token)
    img.save(filepath)
    return jsonify({
        'status':'success',
        'token': token,
        'qr_url': url_for('static', filename=f"qrcodes/{filename}"),
        'expires_in': TOKEN_TTL_SECONDS
    })

# login siswa
@app.route('/login_siswa', methods=['POST'])
def login_siswa():
    username = request.form.get('username')
    password = request.form.get('password')
    siswa = get_siswa_by_username(username)
    if not siswa or siswa['password'] != password:
        return "Login gagal: username/password salah", 401
    session.clear()
    session['id_siswa'] = siswa['id_siswa']
    session['username'] = siswa['username']
    session['nama_siswa'] = siswa['nama_siswa']
    return redirect(url_for('siswa_dashboard'))

@app.route('/siswa')
def siswa_dashboard():
    if 'id_siswa' not in session:
        return redirect(url_for('index'))
    id_s = session['id_siswa']
    history = get_absensi_by_id_siswa(id_s)
    return render_template('siswa.html', nama=session.get('nama_siswa'), history=history)

# siswa kirim token setelah scan
@app.route('/scan_token', methods=['POST'])
def scan_token():
    if 'id_siswa' not in session:
        return jsonify({'status':'error','message':'Siswa belum login'}), 401
    data = request.get_json() or {}
    token = data.get('token')
    if not token:
        return jsonify({'status':'error','message':'Token kosong'}), 400
    row = verify_token(token)
    if not row:
        return jsonify({'status':'error','message':'Token tidak valid atau sudah expired'}), 400
    # cek waktu kadaluarsa
    if datetime.now() > row['waktu_expired']:
        # expire token in DB
        # expire_token(row['token'])  # optional: implement expire_token in db if desired
        return jsonify({'status':'error','message':'Token sudah kadaluarsa'}), 400
    # insert absen (by id_siswa dari session)
    success = insert_absen_by_id(session['id_siswa'], token)
    if success:
        # expire token optionally so one token cannot be reused across sessions (if you want single-use)
        # expire_token(token)
        return jsonify({'status':'success','message':'Absensi berhasil tercatat'})
    else:
        return jsonify({'status':'warning','message':'Anda sudah absen hari ini'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------------------
# HTTPS helper: create cert
# ---------------------------
def ensure_cert(cert_file='cert.pem', key_file='key.pem'):
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file

    # Try openssl (recommended)
    try:
        openssl_cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', key_file, '-out', cert_file,
            '-days', '365', '-nodes', '-subj', '/CN=localhost'
        ]
        subprocess.check_call(openssl_cmd)
        print("Sertifikat dibuat dengan openssl:", cert_file, key_file)
        return cert_file, key_file
    except Exception as e:
        print("openssl tidak tersedia atau gagal:", e)

    # Fallback: werkzeug.make_ssl_devcert (older werkzeug)
    try:
        from werkzeug.serving import make_ssl_devcert
        make_ssl_devcert('ssl_cert', host='localhost')
        # make_ssl_devcert creates ssl_cert.key and ssl_cert.crt
        return 'ssl_cert.crt', 'ssl_cert.key'
    except Exception as e:
        print("make_ssl_devcert tidak tersedia:", e)

    # else: instruct user
    raise RuntimeError("Tidak dapat membuat sertifikat otomatis. Instal openssl atau buat cert.pem & key.pem secara manual.")

# ---------------------------
# Run app with HTTPS on 0.0.0.0
# ---------------------------
if __name__ == '__main__':
    # create certs if needed and then run
    try:
        cert, key = ensure_cert('cert.pem', 'key.pem')
    except Exception as ex:
        print("ERROR: tidak bisa membuat sertifikat otomatis.", ex)
        print("Silakan buat sertifikat manual: openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes")
        sys.exit(1)

    # Run on all interfaces so other devices in LAN (HP) can access via IP
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=(cert, key))
