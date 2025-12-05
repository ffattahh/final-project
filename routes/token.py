import os
import secrets
import qrcode
from flask import Blueprint, session, jsonify, current_app, url_for
from services.token_service import insert_qr_token

token_bp = Blueprint('token', __name__)


@token_bp.route('/generate_token', methods=['POST'])
def generate_token():
    if 'role' not in session or session['role'] != 'guru':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    token = secrets.token_urlsafe(32)
    ttl = current_app.config.get('TOKEN_TTL_SECONDS', 300)

    # waktu expiry handled inside service
    insert_qr_token(token, ttl)

    # make image
    filename = f"token_{token[:8]}.png"
    out_dir = os.path.join(current_app.root_path, 'static', 'qrcodes')
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)

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
    img.save(filepath)

    qr_url = url_for('static', filename=f'qrcodes/{filename}')
    return jsonify({'status': 'success', 'token': token, 'qr_url': qr_url, 'expires_in': ttl})
