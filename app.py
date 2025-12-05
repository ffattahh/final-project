"""
Flask application untuk sistem absensi QR Code (Refactored)
Aplikasi ini mengelola absensi siswa menggunakan QR code dengan timezone WIB.
"""
import os
from flask import Flask
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Warning: flask_cors not installed. Install with: pip install flask-cors")

from config import Config

# Import blueprints
from routes.auth import auth_bp
from routes.guru import guru_bp
from routes.siswa import siswa_bp
from routes.api_siswa import api_siswa_bp
from routes.api_absensi import api_absensi_bp


def create_app(config_class=Config):
    """
    Application factory untuk membuat Flask app

    Args:
        config_class: Class konfigurasi yang akan digunakan

    Returns:
        Flask: Flask application instance
    """
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Enable CORS if available
    if CORS_AVAILABLE:
        CORS(flask_app)

    # Buat folder untuk QR codes jika belum ada
    qrcode_folder = flask_app.config.get('QRCODE_FOLDER', 'static/qrcodes')
    out_dir = os.path.join(flask_app.root_path, qrcode_folder)
    os.makedirs(out_dir, exist_ok=True)

    # Register blueprints
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(guru_bp)
    flask_app.register_blueprint(siswa_bp)
    flask_app.register_blueprint(api_siswa_bp)
    flask_app.register_blueprint(api_absensi_bp)

    return flask_app


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Jalankan aplikasi
    # Akses dari perangkat lain di LAN: http://[IP_ADDRESS]:5000
    app.run(host='0.0.0.0', port=5000, debug=True)
