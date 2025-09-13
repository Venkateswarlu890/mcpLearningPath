"""
Authentication system for the AI Learning & Interview Platform
Handles user registration, login, session management, and password security
"""

import hashlib
import secrets
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re

# Conditional import for streamlit
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create a mock st object for when streamlit is not available
    class MockStreamlit:
        class session_state:
            def __init__(self):
                self._state = {}
            def __getitem__(self, key):
                return self._state.get(key)
            def __setitem__(self, key, value):
                self._state[key] = value
            def __contains__(self, key):
                return key in self._state
            def get(self, key, default=None):
                return self._state.get(key, default)
            def __delitem__(self, key):
                if key in self._state:
                    del self._state[key]
        def rerun(self):
            pass
        def success(self, message):
            print(f"SUCCESS: {message}")
        def error(self, message):
            print(f"ERROR: {message}")
        def info(self, message):
            print(f"INFO: {message}")
        def warning(self, message):
            print(f"WARNING: {message}")
        def subheader(self, text):
            print(f"SUBHEADER: {text}")
        def text_input(self, label, **kwargs):
            return input(f"{label}: ")
        def text_area(self, label, **kwargs):
            return input(f"{label}: ")
        def button(self, label, **kwargs):
            return input(f"Press Enter to {label.lower()}: ") == ""
        def form_submit_button(self, label):
            return input(f"Press Enter to {label.lower()}: ") == ""
        def form(self, key):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def container(self):
            return self
        def columns(self, n):
            return [self for _ in range(n)]
        def markdown(self, text):
            print(f"MARKDOWN: {text}")
        def write(self, text):
            print(f"WRITE: {text}")
        def empty(self):
            return self
        def progress(self, value):
            print(f"PROGRESS: {value*100:.1f}%")
        def spinner(self, text):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    st = MockStreamlit()

class AuthManager:
    """Manages user authentication and session handling"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with user tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                profile_data TEXT
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Learning progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                learning_goal TEXT NOT NULL,
                progress_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Interview sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                interview_type TEXT NOT NULL,
                role TEXT NOT NULL,
                language TEXT DEFAULT 'english',
                difficulty TEXT DEFAULT 'intermediate',
                session_data TEXT,
                final_report TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                preferences_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for secure password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == password_hash
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    def register_user(self, username: str, email: str, password: str, full_name: str = None) -> tuple:
        """Register a new user"""
        # Validate inputs
        if not username or not email or not password:
            return False, "All fields are required"
        
        if not self.validate_email(email):
            return False, "Invalid email format"
        
        is_valid, message = self.validate_password(password)
        if not is_valid:
            return False, message
        
        # Check if user already exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return False, "Username or email already exists"
        
        # Hash password and create user
        password_hash, salt = self.hash_password(password)
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, full_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return True, f"User {username} registered successfully"
        except Exception as e:
            conn.close()
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username_or_email: str, password: str) -> tuple:
        """Login user and create session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find user by username or email
        cursor.execute('''
            SELECT id, username, email, password_hash, salt, full_name, is_active
            FROM users WHERE (username = ? OR email = ?) AND is_active = 1
        ''', (username_or_email, username_or_email))
        
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False, "Invalid credentials"
        
        user_id, username, email, password_hash, salt, full_name, is_active = user
        
        # Verify password
        if not self.verify_password(password, password_hash, salt):
            conn.close()
            return False, "Invalid credentials"
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)  # 7-day session
        
        cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, session_token, expires_at))
        
        # Update last login
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        # Store session in Streamlit session state
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.email = email
        st.session_state.full_name = full_name
        st.session_state.session_token = session_token
        st.session_state.is_authenticated = True
        
        return True, f"Welcome back, {username}!"
    
    def logout_user(self):
        """Logout user and invalidate session"""
        if 'session_token' in st.session_state:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions SET is_active = 0 
                WHERE session_token = ?
            ''', (st.session_state.session_token,))
            
            conn.commit()
            conn.close()
        
        # Clear session state
        for key in ['user_id', 'username', 'email', 'full_name', 'session_token', 'is_authenticated']:
            if key in st.session_state:
                del st.session_state[key]
    
    def verify_session(self, session_token: str) -> tuple:
        """Verify if session is valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.full_name, s.expires_at
            FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.session_token = ? AND s.is_active = 1 AND s.expires_at > CURRENT_TIMESTAMP
        ''', (session_token,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, user
        return False, None
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, email, full_name, created_at, last_login, profile_data
            FROM users WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'username': user[0],
                'email': user[1],
                'full_name': user[2],
                'created_at': user[3],
                'last_login': user[4],
                'profile_data': user[5]
            }
        return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET profile_data = ?, full_name = ?
                WHERE id = ?
            ''', (str(profile_data), profile_data.get('full_name'), user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def save_learning_progress(self, user_id: int, learning_goal: str, progress_data: Dict[str, Any]) -> bool:
        """Save learning progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO learning_progress (user_id, learning_goal, progress_data)
                VALUES (?, ?, ?)
            ''', (user_id, learning_goal, str(progress_data)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def get_learning_progress(self, user_id: int) -> list:
        """Get user's learning progress history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT learning_goal, progress_data, created_at, updated_at, status
            FROM learning_progress WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        progress = cursor.fetchall()
        conn.close()
        
        return [
            {
                'learning_goal': p[0],
                'progress_data': p[1],
                'created_at': p[2],
                'updated_at': p[3],
                'status': p[4]
            }
            for p in progress
        ]
    
    def save_interview_session(self, user_id: int, interview_data: Dict[str, Any]) -> bool:
        """Save interview session data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO interview_sessions 
                (user_id, interview_type, role, language, difficulty, session_data, final_report)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                interview_data.get('interview_type'),
                interview_data.get('role'),
                interview_data.get('language', 'english'),
                interview_data.get('difficulty', 'intermediate'),
                str(interview_data.get('session_data', {})),
                str(interview_data.get('final_report', {}))
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def get_interview_sessions(self, user_id: int) -> list:
        """Get user's interview session history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT interview_type, role, language, difficulty, session_data, 
                   final_report, created_at, completed_at, status
            FROM interview_sessions WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        sessions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'interview_type': s[0],
                'role': s[1],
                'language': s[2],
                'difficulty': s[3],
                'session_data': s[4],
                'final_report': s[5],
                'created_at': s[6],
                'completed_at': s[7],
                'status': s[8]
            }
            for s in sessions
        ]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions SET is_active = 0 
            WHERE expires_at < CURRENT_TIMESTAMP
        ''')
        
        conn.commit()
        conn.close()

# Initialize auth manager
auth_manager = AuthManager()

def show_login_form():
    """Display login form"""
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username_or_email and password:
                success, message = auth_manager.login_user(username_or_email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in all fields")

def show_register_form():
    """Display registration form"""
    st.subheader("📝 Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        full_name = st.text_input("Full Name (Optional)")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = auth_manager.register_user(username, email, password, full_name)
                    if success:
                        st.success(message)
                        st.info("Please login with your credentials")
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all required fields")

def show_user_profile():
    """Display user profile"""
    if 'user_id' in st.session_state:
        profile = auth_manager.get_user_profile(st.session_state.user_id)
        if profile:
            st.subheader("👤 User Profile")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Username:** {profile['username']}")
                st.write(f"**Email:** {profile['email']}")
                st.write(f"**Full Name:** {profile['full_name'] or 'Not set'}")
            
            with col2:
                st.write(f"**Member Since:** {profile['created_at']}")
                st.write(f"**Last Login:** {profile['last_login'] or 'Never'}")
            
            # Learning Progress Summary
            st.subheader("📚 Learning Progress")
            progress = auth_manager.get_learning_progress(st.session_state.user_id)
            
            if progress:
                for p in progress[:5]:  # Show last 5
                    with st.expander(f"Goal: {p['learning_goal'][:50]}..."):
                        st.write(f"**Status:** {p['status']}")
                        st.write(f"**Created:** {p['created_at']}")
                        st.write(f"**Updated:** {p['updated_at']}")
            else:
                st.info("No learning progress yet. Start by creating a learning path!")
            
            # Interview Sessions Summary
            st.subheader("🎯 Interview Sessions")
            sessions = auth_manager.get_interview_sessions(st.session_state.user_id)
            
            if sessions:
                for s in sessions[:5]:  # Show last 5
                    with st.expander(f"{s['interview_type'].title()} - {s['role']}"):
                        st.write(f"**Language:** {s['language']}")
                        st.write(f"**Difficulty:** {s['difficulty']}")
                        st.write(f"**Status:** {s['status']}")
                        st.write(f"**Date:** {s['created_at']}")
            else:
                st.info("No interview sessions yet. Start by taking a mock interview!")

def require_auth():
    """Decorator to require authentication for app sections"""
    if 'is_authenticated' not in st.session_state or not st.session_state.is_authenticated:
        st.error("🔒 Please login to access this feature")
        return False
    return True

def show_auth_sidebar():
    """Show authentication controls in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Authentication")
    
    if 'is_authenticated' in st.session_state and st.session_state.is_authenticated:
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
        
        if st.sidebar.button("👤 Profile"):
            st.session_state.show_profile = True
        
        if st.sidebar.button("🚪 Logout"):
            auth_manager.logout_user()
            st.sidebar.success("Logged out successfully")
            st.rerun()
    else:
        st.sidebar.info("Please login to save your progress")
        
        if st.sidebar.button("🔐 Login"):
            st.session_state.show_login = True
        
        if st.sidebar.button("📝 Register"):
            st.session_state.show_register = True

# Initialize session state for auth (only if streamlit is available)
if STREAMLIT_AVAILABLE:
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
