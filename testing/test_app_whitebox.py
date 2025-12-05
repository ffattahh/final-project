# test_app_whitebox.py
"""
White Box Testing untuk aplikasi Flask Absensi QR
Testing mencakup: Database functions, Routes, API endpoints
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pytz
import json
import io

# Import fungsi dari app.py
import sys
sys.path.insert(0, '.')

# Mock mysql.connector sebelum import app
sys.modules['mysql.connector'] = MagicMock()
sys.modules['mysql.connector.pooling'] = MagicMock()

from app import (
    get_current_time_wib,
    get_guru_by_username,
    get_siswa_by_username,
    get_siswa_by_id,
    verify_token,
    insert_absen_by_id,
    app,
    WIB
)


class TestTimezoneFunction(unittest.TestCase):
    """Test fungsi timezone WIB"""
    
    def test_get_current_time_wib_returns_datetime(self):
        """Test bahwa fungsi mengembalikan object datetime"""
        result = get_current_time_wib()
        self.assertIsInstance(result, datetime)
    
    def test_get_current_time_wib_has_timezone(self):
        """Test bahwa datetime memiliki timezone info"""
        result = get_current_time_wib()
        self.assertIsNotNone(result.tzinfo)
    
    def test_get_current_time_wib_is_wib_timezone(self):
        """Test bahwa timezone adalah WIB (UTC+7)"""
        result = get_current_time_wib()
        self.assertEqual(result.tzinfo.zone, 'Asia/Jakarta')


class TestDatabaseFunctions(unittest.TestCase):
    """Test fungsi-fungsi database dengan mocking"""
    
    @patch('app.connect_db')
    def test_get_guru_by_username_found(self, mock_connect):
        """Path 1: Guru ditemukan"""
        # Setup mock
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            'id_guru': 1,
            'username': 'guru1',
            'nama_guru': 'Pak Budi'
        }
        
        # Execute
        result = get_guru_by_username('guru1')
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'guru1')
        mock_cursor.execute.assert_called_once()
    
    @patch('app.connect_db')
    def test_get_guru_by_username_not_found(self, mock_connect):
        """Path 2: Guru tidak ditemukan"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = None
        
        result = get_guru_by_username('nonexistent')
        
        self.assertIsNone(result)
    
    @patch('app.connect_db')
    def test_get_siswa_by_id_found(self, mock_connect):
        """Path 1: Siswa ditemukan berdasarkan ID"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            'id_siswa': 1,
            'username': 'siswa1',
            'nama_siswa': 'Andi'
        }
        
        result = get_siswa_by_id(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id_siswa'], 1)
    
    @patch('app.connect_db')
    def test_verify_token_valid_active(self, mock_connect):
        """Path 1: Token valid dan status aktif"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            'token': 'abc123',
            'status': 'aktif',
            'waktu_expired': datetime.now(WIB) + timedelta(minutes=5)
        }
        
        result = verify_token('abc123')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'aktif')
    
    @patch('app.connect_db')
    def test_verify_token_not_found(self, mock_connect):
        """Path 2: Token tidak ditemukan"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = None
        
        result = verify_token('invalid_token')
        
        self.assertIsNone(result)


class TestInsertAbsenFunction(unittest.TestCase):
    """Test fungsi insert_absen_by_id dengan berbagai path"""
    
    @patch('app.connect_db')
    def test_insert_absen_duplicate_today(self, mock_connect):
        """Path 1: Siswa sudah absen hari ini (duplikat)"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock: sudah ada absen hari ini
        mock_cursor.fetchone.return_value = {'id_absen': 1}
        
        result = insert_absen_by_id(1, 'token123')
        
        self.assertFalse(result)
    
    @patch('app.connect_db')
    def test_insert_absen_siswa_not_found(self, mock_connect):
        """Path 2: Siswa tidak ditemukan"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock: tidak ada duplikat, tapi siswa tidak ada
        mock_cursor.fetchone.side_effect = [None, None]
        
        result = insert_absen_by_id(999, 'token123')
        
        self.assertFalse(result)
    
    @patch('app.get_current_time_wib')
    @patch('app.connect_db')
    def test_insert_absen_success(self, mock_connect, mock_time):
        """Path 3: Absensi berhasil diinsert"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_time.return_value = datetime(2024, 12, 5, 8, 0, 0, tzinfo=WIB)
        
        # Mock: tidak duplikat, siswa ditemukan
        mock_cursor.fetchone.side_effect = [
            None,  # Cek duplikat: tidak ada
            {'nama_siswa': 'Andi', 'jurusan': 'RPL', 'kelas': '12A'}  # Data siswa
        ]
        
        result = insert_absen_by_id(1, 'token123')
        
        self.assertTrue(result)
        # Verify insert was called
        self.assertEqual(mock_cursor.execute.call_count, 3)


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask routes dengan white box approach"""
    
    def setUp(self):
        """Setup test client"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_key'
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
    
    def tearDown(self):
        """Cleanup"""
        self.ctx.pop()
    
    def test_index_route_default_role(self):
        """Path 1: Akses index tanpa parameter role"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_index_route_with_role_guru(self):
        """Path 2: Akses index dengan role=guru"""
        response = self.client.get('/?role=guru')
        self.assertEqual(response.status_code, 200)
    
    def test_index_route_with_role_siswa(self):
        """Path 3: Akses index dengan role=siswa"""
        response = self.client.get('/?role=siswa')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.get_guru_by_username')
    def test_login_guru_success(self, mock_get_guru):
        """Path 1: Login guru berhasil"""
        mock_get_guru.return_value = {
            'username': 'guru1',
            'password': 'pass123',
            'nama_guru': 'Pak Budi'
        }
        
        response = self.client.post('/login_guru', data={
            'username': 'guru1',
            'password': 'pass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
    
    @patch('app.get_guru_by_username')
    def test_login_guru_wrong_password(self, mock_get_guru):
        """Path 2: Login guru gagal - password salah"""
        mock_get_guru.return_value = {
            'username': 'guru1',
            'password': 'pass123',
            'nama_guru': 'Pak Budi'
        }
        
        response = self.client.post('/login_guru', data={
            'username': 'guru1',
            'password': 'wrongpass'
        })
        
        self.assertEqual(response.status_code, 401)
    
    @patch('app.get_guru_by_username')
    def test_login_guru_user_not_found(self, mock_get_guru):
        """Path 3: Login guru gagal - user tidak ada"""
        mock_get_guru.return_value = None
        
        response = self.client.post('/login_guru', data={
            'username': 'nonexistent',
            'password': 'pass123'
        })
        
        self.assertEqual(response.status_code, 401)
    
    def test_guru_dashboard_without_login(self):
        """Path 1: Akses dashboard guru tanpa login"""
        response = self.client.get('/guru')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    @patch('app.get_all_absensi')
    def test_guru_dashboard_with_login(self, mock_get_absensi):
        """Path 2: Akses dashboard guru dengan login"""
        mock_get_absensi.return_value = []
        
        with self.client.session_transaction() as sess:
            sess['guru'] = 'guru1'
            sess['nama_guru'] = 'Pak Budi'
            sess['role'] = 'guru'
        
        response = self.client.get('/guru')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.get_siswa_by_username')
    def test_login_siswa_success(self, mock_get_siswa):
        """Path 1: Login siswa berhasil"""
        mock_get_siswa.return_value = {
            'id_siswa': 1,
            'username': 'siswa1',
            'password': 'pass123',
            'nama_siswa': 'Andi'
        }
        
        response = self.client.post('/login_siswa', data={
            'username': 'siswa1',
            'password': 'pass123'
        })
        
        self.assertEqual(response.status_code, 302)
    
    def test_scan_token_without_login(self):
        """Path 1: Scan token tanpa login siswa"""
        response = self.client.post('/scan_token',
            data=json.dumps({'token': 'abc123'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    @patch('app.verify_token')
    def test_scan_token_invalid_token(self, mock_verify):
        """Path 2: Token tidak valid"""
        mock_verify.return_value = None
        
        with self.client.session_transaction() as sess:
            sess['id_siswa'] = 1
        
        response = self.client.post('/scan_token',
            data=json.dumps({'token': 'invalid'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('tidak valid', data['message'])
    
    def test_scan_token_empty_token(self):
        """Path 3: Token kosong"""
        with self.client.session_transaction() as sess:
            sess['id_siswa'] = 1
        
        response = self.client.post('/scan_token',
            data=json.dumps({'token': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    @patch('app.insert_absen_by_id')
    @patch('app.get_current_time_wib')
    @patch('app.verify_token')
    def test_scan_token_expired(self, mock_verify, mock_time, mock_insert):
        """Path 4: Token sudah kadaluarsa"""
        mock_time.return_value = datetime(2024, 12, 5, 9, 0, 0, tzinfo=WIB)
        mock_verify.return_value = {
            'token': 'abc123',
            'waktu_expired': datetime(2024, 12, 5, 8, 0, 0, tzinfo=WIB)
        }
        
        with self.client.session_transaction() as sess:
            sess['id_siswa'] = 1
        
        response = self.client.post('/scan_token',
            data=json.dumps({'token': 'abc123'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('kadaluarsa', data['message'])


class TestAPIEndpoints(unittest.TestCase):
    """Test API CRUD endpoints"""
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    @patch('app.get_all_absensi')
    def test_api_get_absensi_success(self, mock_get):
        """Path 1: API get absensi berhasil"""
        mock_get.return_value = [
            {
                'id_absen': 1,
                'waktu_absen': datetime(2024, 12, 5, 8, 0, 0),
                'nama_siswa': 'Andi'
            }
        ]
        
        response = self.client.get('/api/absensi')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    @patch('app.get_db_connection')
    def test_api_add_siswa_success(self, mock_conn):
        """Path 1: Tambah siswa berhasil"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_conn.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        response = self.client.post('/api/siswa',
            data=json.dumps({
                'username': 'siswa_baru',
                'password': 'pass123',
                'nis': '12345',
                'nama_siswa': 'Budi',
                'jurusan': 'RPL',
                'kelas': '12A'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_api_add_siswa_incomplete_data(self):
        """Path 2: Data tidak lengkap"""
        response = self.client.post('/api/siswa',
            data=json.dumps({
                'username': 'siswa_baru'
                # Missing required fields
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    @patch('app.get_db_connection')
    def test_api_delete_siswa_success(self, mock_conn):
        """Path 1: Hapus siswa berhasil"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_conn.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        response = self.client.delete('/api/siswa/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    @patch('app.get_db_connection')
    def test_api_delete_siswa_not_found(self, mock_conn):
        """Path 2: Siswa tidak ditemukan"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_conn.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        
        response = self.client.delete('/api/siswa/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])


class TestBoundaryValues(unittest.TestCase):
    """Test boundary values untuk kondisi-kondisi kritis"""
    
    @patch('app.connect_db')
    def test_token_exactly_expired(self, mock_connect):
        """Boundary: Token tepat di waktu expired"""
        # Setup mock untuk verify_token
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Token expired tepat di waktu sekarang
        now = datetime.now(WIB)
        mock_cursor.fetchone.return_value = {
            'token': 'abc123',
            'status': 'aktif',
            'waktu_expired': now
        }
        
        result = verify_token('abc123')
        self.assertIsNotNone(result)


# Test Runner dengan Coverage Report
if __name__ == '__main__':
    print("="*70)
    print("WHITE BOX TESTING - Flask Absensi QR App")
    print("="*70)
    
    # Run tests
    unittest.main(verbosity=2)