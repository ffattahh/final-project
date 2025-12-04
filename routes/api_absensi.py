"""
API Absensi Blueprint - Handles absensi API and export routes
"""
import io
from datetime import datetime
from flask import Blueprint, jsonify, redirect, url_for, session, send_file
from mysql.connector import Error
from openpyxl import Workbook
from services.absensi_service import get_all_absensi, get_absensi_with_filters
from utils.time_helper import get_current_time_wib, format_datetime

api_absensi_bp = Blueprint('api_absensi', __name__, url_prefix='/api')


@api_absensi_bp.route('/absensi', methods=['GET'])
def get_absensi():
    """
    API GET - Ambil semua data absensi

    Returns:
        JSON response dengan list data absensi
    """
    try:
        data = get_all_absensi()

        # Format datetime objects
        for row in data:
            if isinstance(row.get('waktu_absen'), datetime):
                row['waktu_absen'] = format_datetime(row['waktu_absen'])

        return jsonify({
            'success': True,
            'data': data
        }), 200

    except Error as err:
        return jsonify({
            'success': False,
            'message': str(err)
        }), 500


@api_absensi_bp.route('/export_absensi', methods=['GET'])
def export_absensi():
    """
    Export riwayat absensi ke file Excel (.xlsx)

    Returns:
        File Excel dengan data absensi
    """
    if 'guru' not in session:
        return redirect(url_for('auth.index'))

    try:
        # Ambil data absensi
        absensi_list = get_absensi_with_filters()

        # Buat workbook Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Riwayat Absensi"

        # Header
        headers = [
            'ID Absen', 'NIS', 'Nama Siswa',
            'Kelas', 'Jurusan', 'Waktu Absen', 'Status'
        ]
        ws.append(headers)

        # Data rows
        for item in absensi_list:
            waktu_absen = format_datetime(item.get('waktu_absen'))

            ws.append([
                item.get('id_absen', ''),
                item.get('nis', ''),
                item.get('nama_siswa', ''),
                item.get('kelas', ''),
                item.get('jurusan', ''),
                waktu_absen,
                item.get('status', 'hadir')
            ])

        # Auto-adjust column width
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(
                length + 2, 50
            )

        # Save to BytesIO
        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)

        # Generate filename dengan timestamp WIB
        timestamp = get_current_time_wib().strftime('%Y%m%d%H%M%S')
        filename = f"absensi_{timestamp}.xlsx"

        return send_file(
            bio,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except (Error, IOError) as err:
        return f"Error exporting data: {str(err)}", 500
