"""
Test script for the authentication system
Run this to verify that the authentication and database functionality works correctly
"""

from auth import auth_manager
import os

def test_database_creation():
    """Test if database is created successfully"""
    print("🧪 Testing database creation...")
    
    if os.path.exists("users.db"):
        print("✅ Database file created successfully")
        return True
    else:
        print("❌ Database file not found")
        return False

def test_user_registration():
    """Test user registration functionality"""
    print("\n🧪 Testing user registration...")
    
    # Test valid registration
    success, message = auth_manager.register_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!",
        full_name="Test User"
    )
    
    if success:
        print("✅ User registration successful")
        return True
    else:
        print(f"❌ User registration failed: {message}")
        return False

def test_user_login():
    """Test user login functionality"""
    print("\n🧪 Testing user login...")
    
    # Test valid login
    success, message = auth_manager.login_user("testuser", "TestPass123!")
    
    if success:
        print("✅ User login successful")
        return True
    else:
        print(f"❌ User login failed: {message}")
        return False

def test_password_validation():
    """Test password validation"""
    print("\n🧪 Testing password validation...")
    
    test_cases = [
        ("weak", False, "Too short"),
        ("WeakPass", False, "No numbers or special chars"),
        ("weakpass123", False, "No uppercase or special chars"),
        ("WEAKPASS123", False, "No lowercase or special chars"),
        ("WeakPass123", False, "No special characters"),
        ("TestPass123!", True, "Valid password")
    ]
    
    all_passed = True
    for password, expected, description in test_cases:
        is_valid, message = auth_manager.validate_password(password)
        if is_valid == expected:
            print(f"✅ {description}: {password} - {message}")
        else:
            print(f"❌ {description}: {password} - Expected {expected}, got {is_valid}")
            all_passed = False
    
    return all_passed

def test_email_validation():
    """Test email validation"""
    print("\n🧪 Testing email validation...")
    
    test_cases = [
        ("valid@example.com", True),
        ("user.name@domain.co.uk", True),
        ("invalid-email", False),
        ("@domain.com", False),
        ("user@", False),
        ("user@domain", False)
    ]
    
    all_passed = True
    for email, expected in test_cases:
        is_valid = auth_manager.validate_email(email)
        if is_valid == expected:
            print(f"✅ Email validation: {email} - {'Valid' if is_valid else 'Invalid'}")
        else:
            print(f"❌ Email validation: {email} - Expected {expected}, got {is_valid}")
            all_passed = False
    
    return all_passed

def test_learning_progress():
    """Test learning progress saving and retrieval"""
    print("\n🧪 Testing learning progress...")
    
    # Get user ID (assuming test user was created)
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        print("❌ Test user not found")
        return False
    
    user_id = user[0]
    
    # Test saving learning progress
    progress_data = {
        "goal": "Learn Python basics",
        "messages": ["Day 1: Variables and data types", "Day 2: Control structures"],
        "generated_at": 1705312200
    }
    
    success = auth_manager.save_learning_progress(user_id, "Learn Python basics", progress_data)
    if success:
        print("✅ Learning progress saved successfully")
    else:
        print("❌ Failed to save learning progress")
        return False
    
    # Test retrieving learning progress
    progress = auth_manager.get_learning_progress(user_id)
    if progress and len(progress) > 0:
        print("✅ Learning progress retrieved successfully")
        return True
    else:
        print("❌ Failed to retrieve learning progress")
        return False

def test_interview_session():
    """Test interview session saving and retrieval"""
    print("\n🧪 Testing interview session...")
    
    # Get user ID
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        print("❌ Test user not found")
        return False
    
    user_id = user[0]
    
    # Test saving interview session
    interview_data = {
        "interview_type": "technical",
        "role": "python",
        "language": "english",
        "difficulty": "intermediate",
        "session_data": {
            "interview_history": [
                {
                    "question": "What is Python?",
                    "answer": "Python is a programming language",
                    "evaluation": {"overall_score": 8}
                }
            ]
        },
        "final_report": {
            "overall_score": 8,
            "strengths": ["Good technical knowledge"],
            "weaknesses": ["Could improve communication"]
        }
    }
    
    success = auth_manager.save_interview_session(user_id, interview_data)
    if success:
        print("✅ Interview session saved successfully")
    else:
        print("❌ Failed to save interview session")
        return False
    
    # Test retrieving interview sessions
    sessions = auth_manager.get_interview_sessions(user_id)
    if sessions and len(sessions) > 0:
        print("✅ Interview sessions retrieved successfully")
        return True
    else:
        print("❌ Failed to retrieve interview sessions")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Delete test user and related data
    cursor.execute("DELETE FROM users WHERE username = 'testuser'")
    conn.commit()
    conn.close()
    
    print("✅ Test data cleaned up")

def main():
    """Run all tests"""
    print("🚀 Authentication System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Creation", test_database_creation),
        ("Password Validation", test_password_validation),
        ("Email Validation", test_email_validation),
        ("User Registration", test_user_registration),
        ("User Login", test_user_login),
        ("Learning Progress", test_learning_progress),
        ("Interview Session", test_interview_session)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Authentication system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    # Clean up test data
    cleanup_test_data()
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    main()
