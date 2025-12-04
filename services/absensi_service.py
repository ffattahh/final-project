"""
Service layer untuk operasi Absensi
"""
from utils.db import connect_db
from utils.time_helper import get_current_time_wib


def insert_absen_by_id(id_siswa, token_qr):
    """
    Mencatat absensi siswa

    Args:
        id_siswa (int): ID siswa yang absen
        token_qr (str): Token QR yang digunakan

    Returns:
        bool: True jika berhasil, False jika sudah absen hari ini
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    try:
        # Cek duplikat absensi hari ini
        cur.execute(
            "SELECT id_absen FROM absensi WHERE id_siswa=%s AND DATE(waktu_absen)=CURDATE()",
            (id_siswa,)
        )
        if cur.fetchone():
            return False

        # Ambil data siswa
        cur.execute(
            "SELECT nama_siswa, jurusan, kelas FROM siswa WHERE id_siswa=%s",
            (id_siswa,)
        )
        siswa = cur.fetchone()

        if not siswa:
            return False

        # Insert absensi dengan waktu WIB
        waktu_absen_wib = get_current_time_wib()
        cur.execute("""
            INSERT INTO absensi
            (id_siswa, waktu_absen, token_qr, status, nama_siswa, jurusan, kelas)
            VALUES (%s, %s, %s, 'hadir', %s, %s, %s)
        """, (
            id_siswa,
            waktu_absen_wib,
            token_qr,
            siswa['nama_siswa'],
            siswa['jurusan'],
            siswa['kelas']
        ))

        conn.commit()
        return True

    finally:
        cur.close()
        conn.close()


def get_absensi_by_id_siswa(id_siswa):
    """
    Mengambil riwayat absensi berdasarkan ID siswa

    Args:
        id_siswa (int): ID siswa

    Returns:
        list: List of dictionaries berisi riwayat absensi
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT a.*, s.nama_siswa, s.nis
            FROM absensi a
            JOIN siswa s ON a.id_siswa = s.id_siswa
            WHERE a.id_siswa=%s
            ORDER BY a.waktu_absen DESC
        """, (id_siswa,))

        rows = cur.fetchall()
        return rows

    finally:
        cur.close()
        conn.close()


def get_all_absensi():
    """
    Mengambil semua data absensi

    Returns:
        list: List of dictionaries berisi semua data absensi
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT a.*, s.nama_siswa, s.nis
            FROM absensi a
            JOIN siswa s ON a.id_siswa = s.id_siswa
            ORDER BY a.waktu_absen DESC
        """)

        rows = cur.fetchall()
        return rows

    finally:
        cur.close()
        conn.close()


def get_absensi_with_filters(query_params=None):
    """
    Mengambil data absensi dengan filter

    Args:
        query_params (dict): Dictionary berisi parameter filter

    Returns:
        list: List of dictionaries berisi data absensi yang difilter
    """
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT a.*, s.nis, s.nama_siswa, s.kelas, s.jurusan
            FROM absensi a
            JOIN siswa s ON a.id_siswa = s.id_siswa
            WHERE 1=1
            ORDER BY a.waktu_absen DESC
        """

        # Tambahkan filter jika ada (bisa dikembangkan)
        cur.execute(query)
        rows = cur.fetchall()
        return rows

    finally:
        cur.close()
        conn.close()
