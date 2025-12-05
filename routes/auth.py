"""
Authentication Blueprint - Handles login/logout routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from services.guru_service import authenticate_guru
from services.siswa_service import authenticate_siswa

auth_bp = Blueprint('auth', __name__, url_prefix='/')


@auth_bp.route('/')
def index():
    """
    Halaman login utama
    
    Returns:
        Rendered template untuk halaman login
    """
    role = request.args.get('role', 'guru')
    return render_template('index.html', role=role)


@auth_bp.route('/login_guru', methods=['POST'])
def login_guru():
    """
    Proses login untuk guru
    
    Returns:
        Redirect ke dashboard guru jika berhasil, error message jika gagal
    """
    username = request.form.get('username')
    password = request.form.get('password')
    guru = authenticate_guru(username, password)
    if not guru:
        return "Login gagal: username/password salah", 401
    session.clear()
    session['guru'] = guru['username']
    session['nama_guru'] = guru['nama_guru']
    session['role'] = 'guru'
    return redirect(url_for('guru.dashboard'))

@auth_bp.route('/login_siswa', methods=['POST'])
def login_siswa():
    """
    Proses login untuk siswa
    
    Returns:
        Redirect ke dashboard siswa jika berhasil, error message jika gagal
    """
    username = request.form.get('username')
    password = request.form.get('password')
    siswa = authenticate_siswa(username, password)
    if not siswa:
        return "Login gagal: username/password salah", 401
    session.clear()
    session['id_siswa'] = siswa['id_siswa']
    session['username'] = siswa['username']
    session['nama_siswa'] = siswa['nama_siswa']
    return redirect(url_for('siswa.dashboard'))
@auth_bp.route('/logout')
def logout():
    """
    Logout dan clear session
    
    Returns:
        Redirect ke halaman login
    """
    session.clear()
    return redirect(url_for('auth.index'))
