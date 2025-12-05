"""
Database connection utilities
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def connect_db():
    """
    Membuat koneksi ke database MySQL
    
    Returns:
        mysql.connector.connection: Database connection object
    """
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        print(f"Error connecting to database: {err}")
        raise


def get_db_connection():
    """
    Fungsi alternatif untuk mendapatkan koneksi database
    Mengembalikan None jika koneksi gagal
    
    Returns:
        mysql.connector.connection or None: Database connection object or None
    """
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None
