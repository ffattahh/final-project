"""
Siswa Blueprint - Handles student attendance management routes
"""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from services.absensi_service import get_absensi_by_id_siswa, insert_absen_by_id
from services.token_service import verify_token
from utils.time_helper import get_current_time_wib, localize_to_wib

siswa_bp = Blueprint('siswa', __name__, url_prefix='/siswa')


@siswa_bp.route('/')
def dashboard():
    """
    Dashboard siswa - menampilkan history absensi
    
    Returns:
        Rendered template dashboard siswa
    """
    if 'id_siswa' not in session:
        return redirect(url_for('auth.index'))
    id_s = session['id_siswa']
    history = get_absensi_by_id_siswa(id_s)
    return render_template(
        'siswa.html',
        nama=session.get('nama_siswa'),
        history=history
    )

@siswa_bp.route('/scan_token', methods=['POST'])
def scan_token():
    """
    Proses scan token QR untuk absensi
    
    Returns:
        JSON response dengan status absensi
    """
    if 'id_siswa' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Siswa belum login'
        }), 401
    data = request.get_json() or {}
    token = data.get('token')
    if not token:
        return jsonify({
            'status': 'error',
            'message': 'Token kosong'
        }), 400
    # Verifikasi token
    row = verify_token(token)
    if not row:
        return jsonify({
            'status': 'error',
            'message': 'Token tidak valid atau sudah expired'
        }), 400
    # Cek waktu expired dengan WIB
    waktu_sekarang_wib = get_current_time_wib()
    waktu_expired = localize_to_wib(row['waktu_expired'])
    if waktu_sekarang_wib > waktu_expired:
        return jsonify({
            'status': 'error',
            'message': 'Token sudah kadaluarsa'
        }), 400
    # Insert absensi
    success = insert_absen_by_id(session['id_siswa'], token)
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Absensi berhasil tercatat'
        })
    return jsonify({
        'status': 'warning',
        'message': 'Anda sudah absen hari ini'
    })
