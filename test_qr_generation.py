"""
Test script to verify QR generation functionality
"""
import requests
import json

BASE_URL = "http://192.168.18.76:5000"

def test_login():
    """Test guru login"""
    login_data = {
        "username": "admin",
        "password": "admin123",
        "role": "guru"
    }

    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")

    if response.status_code == 200:
        # Get session cookie
        session_cookie = response.cookies.get('session')
        return session_cookie
    return None

def test_qr_generation(session_cookie):
    """Test QR token generation"""
    cookies = {'session': session_cookie} if session_cookie else {}

    response = requests.post(
        f"{BASE_URL}/guru/generate_token",
        cookies=cookies,
        headers={'Content-Type': 'application/json'}
    )

    print(f"QR Generation response status: {response.status_code}")
    print(f"QR Generation response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            print("✅ QR generation successful!")
            print(f"Token: {data.get('token')}")
            print(f"QR URL: {data.get('qr_url')}")
            print(f"Expires in: {data.get('expires_in')} seconds")
            return True
        else:
            print(f"❌ QR generation failed: {data.get('message')}")
    else:
        print(f"❌ HTTP error: {response.status_code}")
    return False

if __name__ == "__main__":
    print("Testing QR generation functionality...")

    # Test login
    session_cookie = test_login()
    if not session_cookie:
        print("❌ Login failed, cannot test QR generation")
        exit(1)

    # Test QR generation
    success = test_qr_generation(session_cookie)
    if success:
        print("🎉 All tests passed! QR generation is working correctly.")
    else:
        print("❌ QR generation test failed.")
