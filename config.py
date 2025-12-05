"""
Configuration file untuk aplikasi Flask Absensi QR Code
"""
import os

try:
    import pytz
    WIB = pytz.timezone('Asia/Jakarta')
except ImportError:
    # Fallback jika pytz tidak terinstall
    print("Warning: pytz not installed. Install with: pip install pytz")
    from datetime import timezone, timedelta
    WIB = timezone(timedelta(hours=7))  # WIB = UTC+7

# ========================================
# DATABASE CONFIGURATION
# ========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'absensi_qr'
}

# ========================================
# FLASK CONFIGURATION
# ========================================
class Config:
    """Flask application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'random_secret_key'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True

    # QR Code settings
    TOKEN_TTL_SECONDS = 300  # 5 menit

    # File paths
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    QRCODE_FOLDER = 'static/qrcodes'
