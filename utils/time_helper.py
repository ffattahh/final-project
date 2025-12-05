"""
Time helper utilities untuk timezone WIB
"""
from datetime import datetime
from config import WIB


def get_current_time_wib():
    """
    Mendapatkan waktu sekarang dalam timezone WIB (Asia/Jakarta)
    
    Returns:
        datetime: Current time in WIB timezone
    """
    return datetime.now(WIB)


def localize_to_wib(naive_datetime):
    """
    Mengkonversi naive datetime ke WIB timezone
    
    Args:
        naive_datetime: Datetime object without timezone info
        
    Returns:
        datetime: Datetime with WIB timezone
    """
    if naive_datetime.tzinfo is None:
        return WIB.localize(naive_datetime)
    return naive_datetime


def format_datetime(dt_object, fmt='%Y-%m-%d %H:%M:%S'):
    """
    Format datetime object ke string
    
    Args:
        dt_object: Datetime object to format
        fmt: String format pattern
        
    Returns:
        str: Formatted datetime string
    """
    if isinstance(dt_object, datetime):
        return dt_object.strftime(fmt)
    return str(dt_object)
