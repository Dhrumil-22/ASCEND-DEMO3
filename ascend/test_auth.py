"""
Authentication System Testing Script

This script demonstrates and tests all authentication endpoints.
Run this to see the complete authentication flow in action.

Usage:
    python test_auth.py
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

# Store session cookies
session = requests.Session()


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_response(response):
    """Print formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def test_1_register_student():
    """Test 1: Register a student account"""
    print_section("TEST 1: Register Student")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "alice_student",
        "email": "alice@example.com",
        "password": "student_password_123",
        "role": "student",
        "full_name": "Alice Johnson"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 201:
        print("\n✓ Student registered successfully!")
        print(f"  - Username: {response.json()['user']['username']}")
        print(f"  - Role: {response.json()['user']['role']}")
        print(f"  - Verified: {response.json()['user']['is_verified']}")
    else:
        print("\n✗ Registration failed!")


def test_2_register_mentor():
    """Test 2: Register a mentor account"""
    print_section("TEST 2: Register Mentor")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "bob_mentor",
        "email": "bob@example.com",
        "password": "mentor_password_456",
        "role": "mentor",
        "full_name": "Bob Smith"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 201:
        print("\n✓ Mentor registered successfully!")
        print(f"  - Username: {response.json()['user']['username']}")
        print(f"  - Role: {response.json()['user']['role']}")
        print(f"  - Verified: {response.json()['user']['is_verified']}")
        if 'note' in response.json():
            print(f"  - Note: {response.json()['note']}")
    else:
        print("\n✗ Registration failed!")


def test_3_register_admin_fail():
    """Test 3: Try to register admin (should fail)"""
    print_section("TEST 3: Try to Register Admin (Should Fail)")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "admin_user",
        "email": "admin@example.com",
        "password": "admin_password_789",
        "role": "admin"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 403:
        print("\n✓ Admin registration correctly blocked!")
        print(f"  - Error: {response.json()['error']}")
    else:
        print("\n✗ Admin registration should have been blocked!")


def test_4_duplicate_username():
    """Test 4: Try to register with duplicate username"""
    print_section("TEST 4: Duplicate Username (Should Fail)")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "alice_student",  # Already exists
        "email": "alice2@example.com",
        "password": "password123",
        "role": "student"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 400:
        print("\n✓ Duplicate username correctly rejected!")
        print(f"  - Error: {response.json()['error']}")
    else:
        print("\n✗ Duplicate username should have been rejected!")


def test_5_login_student():
    """Test 5: Login as student"""
    print_section("TEST 5: Login as Student")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "alice_student",
        "password": "student_password_123",
        "remember": True
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = session.post(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Login successful!")
        print(f"  - Username: {response.json()['user']['username']}")
        print(f"  - Role: {response.json()['user']['role']}")
        print(f"  - Session cookie set: Yes")
    else:
        print("\n✗ Login failed!")


def test_6_wrong_password():
    """Test 6: Try to login with wrong password"""
    print_section("TEST 6: Wrong Password (Should Fail)")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "alice_student",
        "password": "wrong_password",
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 401:
        print("\n✓ Wrong password correctly rejected!")
        print(f"  - Error: {response.json()['error']}")
    else:
        print("\n✗ Wrong password should have been rejected!")


def test_7_get_profile():
    """Test 7: Get profile (authenticated)"""
    print_section("TEST 7: Get Profile (Authenticated)")
    
    url = f"{BASE_URL}/auth/profile"
    
    print(f"\nGET {url}")
    print("Using session cookie from login")
    
    response = session.get(url)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Profile retrieved successfully!")
        print(f"  - Username: {response.json()['user']['username']}")
        print(f"  - Email: {response.json()['user']['email']}")
    else:
        print("\n✗ Failed to get profile!")


def test_8_update_profile():
    """Test 8: Update profile"""
    print_section("TEST 8: Update Profile")
    
    url = f"{BASE_URL}/auth/profile"
    data = {
        "full_name": "Alice Marie Johnson",
        "bio": "Passionate Python learner and aspiring data scientist"
    }
    
    print(f"\nPUT {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = session.put(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Profile updated successfully!")
        print(f"  - Full Name: {response.json()['user']['full_name']}")
        print(f"  - Bio: {response.json()['user']['bio']}")
    else:
        print("\n✗ Failed to update profile!")


def test_9_change_password():
    """Test 9: Change password"""
    print_section("TEST 9: Change Password")
    
    url = f"{BASE_URL}/auth/change-password"
    data = {
        "current_password": "student_password_123",
        "new_password": "new_student_password_456"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = session.post(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Password changed successfully!")
    else:
        print("\n✗ Failed to change password!")


def test_10_logout():
    """Test 10: Logout"""
    print_section("TEST 10: Logout")
    
    url = f"{BASE_URL}/auth/logout"
    
    print(f"\nPOST {url}")
    
    response = session.post(url)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Logout successful!")
    else:
        print("\n✗ Logout failed!")


def test_11_access_after_logout():
    """Test 11: Try to access profile after logout (should fail)"""
    print_section("TEST 11: Access Profile After Logout (Should Fail)")
    
    url = f"{BASE_URL}/auth/profile"
    
    print(f"\nGET {url}")
    print("Session should be cleared")
    
    response = session.get(url)
    print_response(response)
    
    if response.status_code == 401:
        print("\n✓ Access correctly denied after logout!")
    else:
        print("\n✗ Should have been denied access!")


def test_12_login_with_new_password():
    """Test 12: Login with new password"""
    print_section("TEST 12: Login with New Password")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "alice_student",
        "password": "new_student_password_456"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = session.post(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Login with new password successful!")
    else:
        print("\n✗ Login with new password failed!")


def run_all_tests():
    """Run all authentication tests"""
    print("\n" + "="*70)
    print(" "*15 + "AUTHENTICATION SYSTEM TESTS")
    print("="*70)
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("Run: python app.py")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n✗ Server is not responding correctly!")
            return
    except requests.exceptions.RequestException:
        print("\n✗ Cannot connect to server!")
        print("Please start the Flask app first: python app.py")
        return
    
    print("\n✓ Server is running!")
    
    # Run all tests
    tests = [
        test_1_register_student,
        test_2_register_mentor,
        test_3_register_admin_fail,
        test_4_duplicate_username,
        test_5_login_student,
        test_6_wrong_password,
        test_7_get_profile,
        test_8_update_profile,
        test_9_change_password,
        test_10_logout,
        test_11_access_after_logout,
        test_12_login_with_new_password
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
    
    print("\n" + "="*70)
    print(" "*20 + "ALL TESTS COMPLETED!")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
