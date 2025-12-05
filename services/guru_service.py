"""
Service layer untuk operasi terkait data Guru
"""
from utils.db import connect_db


def get_guru_by_username(username):
    """
    Mengambil data guru berdasarkan username
    
    Args:
        username (str): Username guru
        
    Returns:
        dict or None: Dictionary berisi data guru atau None jika tidak ditemukan
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM guru WHERE username=%s LIMIT 1", (username,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        conn.close()


def authenticate_guru(username, password):
    """
    Autentikasi guru berdasarkan username dan password
    
    Args:
        username (str): Username guru
        password (str): Password guru
        
    Returns:
        dict or None: Data guru jika autentikasi berhasil, None jika gagal
    """
    guru = get_guru_by_username(username)
    if guru and guru.get('password') == password:
        return guru
    return None
