"""
Guru Blueprint - Handles teacher dashboard and QR generation routes
"""
import os
import qrcode
from flask import (
    Blueprint, render_template, session, redirect,
    url_for, jsonify, send_file, current_app
)
from services.absensi_service import get_all_absensi
from services.token_service import create_token_with_ttl
from utils.time_helper import get_current_time_wib

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')


@guru_bp.route('/')
def dashboard():
    """
    Dashboard guru - menampilkan data absensi semua siswa

    Returns:
        Rendered template dashboard guru
    """
    if 'guru' not in session:
        return redirect(url_for('auth.index'))

    absensi = get_all_absensi()
    return render_template(
        'guru.html',
        nama=session.get('nama_guru'),
        absensi=absensi
    )


@guru_bp.route('/generate_token', methods=['POST'])
def generate_token():
    """
    Generate token QR untuk absensi

    Returns:
        JSON response dengan token, QR URL, dan waktu expired
    """
    if 'role' not in session or session['role'] != 'guru':
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized'
        }), 401
    try:
        # Generate token dengan TTL dari config
        ttl_seconds = current_app.config.get('TOKEN_TTL_SECONDS', 300)
        token, _ = create_token_with_ttl(ttl_seconds)
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(token)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Simpan QR code ke file
        qrcode_folder = current_app.config.get('QRCODE_FOLDER', 'static/qrcodes')
        out_dir = os.path.join(current_app.root_path, qrcode_folder)
        os.makedirs(out_dir, exist_ok=True)

        waktu_sekarang = get_current_time_wib()
        timestamp = waktu_sekarang.strftime('%Y%m%d_%H%M%S')
        filename = f"token_{timestamp}.png"
        filepath = os.path.join(out_dir, filename)

        img.save(filepath)

        qr_url = url_for('static', filename=f'qrcodes/{filename}')

        return jsonify({
            'status': 'success',
            'token': token,
            'qr_url': qr_url,
            'expires_in': ttl_seconds
        })

    except (IOError, OSError) as err:
        return jsonify({
            'status': 'error',
            'message': str(err)
        }), 500


@guru_bp.route('/qrcodes/<filename>')
def serve_qr(filename):
    """
    Serve QR code file

    Args:
        filename (str): Nama file QR code

    Returns:
        File QR code atau error message
    """
    qrcode_folder = current_app.config.get('QRCODE_FOLDER', 'static/qrcodes')
    out_dir = os.path.join(current_app.root_path, qrcode_folder)
    filepath = os.path.join(out_dir, filename)

    # Cek apakah file ada
    if not os.path.exists(filepath):
        return "QR Code not found", 404

    # Cek permission
    if not os.access(filepath, os.R_OK):
        return "Access denied", 403

    try:
        return send_file(filepath, mimetype='image/png')
    except IOError:
        return "Internal Server Error", 500
