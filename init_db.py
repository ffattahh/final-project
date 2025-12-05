"""
Database initialization script for absensi_qr database
"""
import mysql.connector
from config import DB_CONFIG

def create_tables():
    """Create all required tables if they don't exist"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Create qr_token table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS qr_token (
            id INT AUTO_INCREMENT PRIMARY KEY,
            token VARCHAR(255) UNIQUE NOT NULL,
            waktu_buat DATETIME NOT NULL,
            waktu_expired DATETIME NOT NULL,
            status ENUM('aktif', 'expired') DEFAULT 'aktif'
        )
    """)

    # Create siswa table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            id_siswa INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nis VARCHAR(20) UNIQUE NOT NULL,
            nama_siswa VARCHAR(100) NOT NULL,
            jurusan VARCHAR(50),
            kelas VARCHAR(20)
        )
    """)

    # Create absensi table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS absensi (
            id_absensi INT AUTO_INCREMENT PRIMARY KEY,
            id_siswa INT,
            waktu_absen DATETIME NOT NULL,
            token_qr VARCHAR(255),
            status VARCHAR(20) DEFAULT 'hadir',
            nama_siswa VARCHAR(100),
            jurusan VARCHAR(50),
            kelas VARCHAR(20),
            FOREIGN KEY (id_siswa) REFERENCES siswa(id_siswa)
        )
    """)

    # Create guru table (assuming it exists based on session usage)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guru (
            id_guru INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nama_guru VARCHAR(100) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
