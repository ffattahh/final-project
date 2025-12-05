"""
Service layer untuk operasi QR Token
"""
import secrets
from datetime import timedelta
from utils.db import connect_db
from utils.time_helper import get_current_time_wib


def generate_new_token():
    """
    Generate token QR baru yang unik
    
    Returns:
        str: Token string yang aman
    """
    return secrets.token_urlsafe(32)


def insert_qr_token(token, expires_dt):
    """
    Menyimpan token QR baru ke database
    
    Args:
        token (str): Token string
        expires_dt (datetime): Waktu expired token
        
    Returns:
        None
    """
    conn = connect_db()
    cur = conn.cursor()
    try:
        waktu_buat_wib = get_current_time_wib()
        cur.execute(
            """INSERT INTO qr_token (token, waktu_buat, waktu_expired, status)
               VALUES (%s, %s, %s, 'aktif')""",
            (token, waktu_buat_wib, expires_dt)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def verify_token(token):
    """
    Memverifikasi apakah token masih aktif
    
    Args:
        token (str): Token yang akan diverifikasi
        
    Returns:
        dict or None: Data token jika aktif, None jika tidak
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT * FROM qr_token WHERE token=%s AND status='aktif' LIMIT 1",
            (token,)
        )
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        conn.close()


def expire_token(token):
    """
    Mengubah status token menjadi expired
    
    Args:
        token (str): Token yang akan di-expire
        
    Returns:
        None
    """
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE qr_token SET status='expired' WHERE token=%s",
            (token,)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def create_token_with_ttl(ttl_seconds=300):
    """
    Membuat token baru dengan Time To Live tertentu
    
    Args:
        ttl_seconds (int): Durasi token dalam detik (default 300 = 5 menit)
        
    Returns:
        tuple: (token, expires_at) - Token string dan waktu expired
    """
    token = generate_new_token()
    waktu_sekarang = get_current_time_wib()
    expires_at = waktu_sekarang + timedelta(seconds=ttl_seconds)
    insert_qr_token(token, expires_at)
    return token, expires_at
