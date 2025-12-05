"""
API CRUD Blueprint - Handles CRUD operations for Siswa
"""
from flask import Blueprint, jsonify, request
from mysql.connector import Error
from services.siswa_service import (
    get_all_siswa,
    get_siswa_by_id,
    create_siswa,
    update_siswa,
    delete_siswa
)

api_siswa_bp = Blueprint('api_siswa', __name__, url_prefix='/api/siswa')


@api_siswa_bp.route('', methods=['GET'])
def get_siswa():
    """
    API GET - Ambil semua data siswa

    Returns:
        JSON response dengan list data siswa
    """
    try:
        data = get_all_siswa()
        return jsonify({
            'success': True,
            'data': data
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'Error: {str(err)}'
        }), 500


@api_siswa_bp.route('/<int:id_siswa>', methods=['GET'])
def get_siswa_detail(id_siswa):
    """
    API GET - Ambil satu data siswa berdasarkan ID

    Args:
        id_siswa (int): ID siswa

    Returns:
        JSON response dengan data siswa
    """
    try:
        data = get_siswa_by_id(id_siswa)

        if data is None:
            return jsonify({
                'success': False,
                'message': 'Siswa tidak ditemukan'
            }), 404

        return jsonify({
            'success': True,
            'data': data
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'Error: {str(err)}'
        }), 500


@api_siswa_bp.route('', methods=['POST'])
def add_siswa():
    """
    API POST - Tambah siswa baru

    Returns:
        JSON response dengan status dan ID siswa baru
    """
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        nis = data.get('nis', '')
        nama_siswa = data.get('nama_siswa', '')
        jurusan = data.get('jurusan', '')
        kelas = data.get('kelas', '')

        # Validasi data
        if not username or not password or not nis or not nama_siswa:
            return jsonify({
                'success': False,
                'message': 'Data tidak lengkap. Username, password, NIS, '
                          'dan nama siswa wajib diisi.'
            }), 400

        last_id = create_siswa(username, password, nis, nama_siswa, jurusan, kelas)

        return jsonify({
            'success': True,
            'message': 'Siswa berhasil ditambahkan',
            'id': last_id
        }), 201

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'Error: {str(err)}'
        }), 500


@api_siswa_bp.route('/<int:id_siswa>', methods=['PUT'])
def update_siswa_data(id_siswa):
    """
    API PUT - Update data siswa

    Args:
        id_siswa (int): ID siswa yang akan diupdate

    Returns:
        JSON response dengan status update
    """
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        nis = data.get('nis', '')
        nama_siswa = data.get('nama_siswa', '')
        jurusan = data.get('jurusan', '')
        kelas = data.get('kelas', '')

        # Validasi data
        if not username or not password or not nis or not nama_siswa:
            return jsonify({
                'success': False,
                'message': 'Data tidak lengkap. Username, password, NIS, '
                          'dan nama siswa wajib diisi.'
            }), 400

        rowcount = update_siswa(
            id_siswa, username, password, nis,
            nama_siswa, jurusan, kelas
        )

        if rowcount == 0:
            return jsonify({
                'success': False,
                'message': 'Siswa tidak ditemukan'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Data siswa berhasil diupdate'
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'Error: {str(err)}'
        }), 500


@api_siswa_bp.route('/<int:id_siswa>', methods=['DELETE'])
def delete_siswa_data(id_siswa):
    """
    API DELETE - Hapus siswa

    Args:
        id_siswa (int): ID siswa yang akan dihapus

    Returns:
        JSON response dengan status penghapusan
    """
    try:
        rowcount = delete_siswa(id_siswa)

        if rowcount == 0:
            return jsonify({
                'success': False,
                'message': 'Siswa tidak ditemukan'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Siswa berhasil dihapus'
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': f'Error: {str(err)}'
        }), 500
