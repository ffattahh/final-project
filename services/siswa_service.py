"""
Service layer untuk operasi terkait data Siswa
"""
from mysql.connector import Error
from utils.db import connect_db, get_db_connection


def get_siswa_by_username(username):
    """
    Mengambil data siswa berdasarkan username

    Args:
        username (str): Username siswa

    Returns:
        dict or None: Dictionary berisi data siswa atau None
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("SELECT * FROM siswa WHERE username=%s LIMIT 1", (username,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        conn.close()


def get_siswa_by_id(id_siswa):
    """
    Mengambil data siswa berdasarkan ID

    Args:
        id_siswa (int): ID siswa

    Returns:
        dict or None: Dictionary berisi data siswa atau None
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("SELECT * FROM siswa WHERE id_siswa=%s LIMIT 1", (id_siswa,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        conn.close()


def authenticate_siswa(username, password):
    """
    Autentikasi siswa berdasarkan username dan password

    Args:
        username (str): Username siswa
        password (str): Password siswa

    Returns:
        dict or None: Data siswa jika berhasil, None jika gagal
    """
    siswa = get_siswa_by_username(username)

    if siswa and siswa.get('password') == password:
        return siswa

    return None


def get_all_siswa():
    """
    Mengambil semua data siswa

    Returns:
        list: List of dictionaries berisi data siswa

    Raises:
        Error: Jika terjadi error database
    """
    connection = get_db_connection()
    if connection is None:
        raise Error("Koneksi database gagal")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM siswa ORDER BY id_siswa ASC")
        data = cursor.fetchall()
        return data
    finally:
        cursor.close()
        connection.close()


def create_siswa(username, password, nis, nama_siswa, jurusan='', kelas=''):
    """
    Menambahkan siswa baru ke database

    Args:
        username (str): Username siswa
        password (str): Password siswa
        nis (str): Nomor Induk Siswa
        nama_siswa (str): Nama lengkap siswa
        jurusan (str): Jurusan siswa
        kelas (str): Kelas siswa

    Returns:
        int: ID siswa yang baru ditambahkan

    Raises:
        Error: Jika terjadi error database
    """
    connection = get_db_connection()
    if connection is None:
        raise Error("Koneksi database gagal")

    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO siswa (username, password, nis, nama_siswa, jurusan, kelas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (username, password, nis, nama_siswa, jurusan, kelas)
        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def update_siswa(id_siswa, username, password, nis, nama_siswa, jurusan='', kelas=''):
    """
    Update data siswa

    Args:
        id_siswa (int): ID siswa yang akan diupdate
        username (str): Username baru
        password (str): Password baru
        nis (str): NIS baru
        nama_siswa (str): Nama siswa baru
        jurusan (str): Jurusan baru
        kelas (str): Kelas baru

    Returns:
        int: Jumlah rows yang terpengaruh

    Raises:
        Error: Jika terjadi error database
    """
    connection = get_db_connection()
    if connection is None:
        raise Error("Koneksi database gagal")

    cursor = connection.cursor()

    try:
        query = """
            UPDATE siswa
            SET username=%s, password=%s, nis=%s, nama_siswa=%s, jurusan=%s, kelas=%s
            WHERE id_siswa=%s
        """
        values = (username, password, nis, nama_siswa, jurusan, kelas, id_siswa)
        cursor.execute(query, values)
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()


def delete_siswa(id_siswa):
    """
    Menghapus data siswa

    Args:
        id_siswa (int): ID siswa yang akan dihapus

    Returns:
        int: Jumlah rows yang terhapus

    Raises:
        Error: Jika terjadi error database
    """
    connection = get_db_connection()
    if connection is None:
        raise Error("Koneksi database gagal")

    cursor = connection.cursor()

    try:
        query = "DELETE FROM siswa WHERE id_siswa=%s"
        cursor.execute(query, (id_siswa,))
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()
