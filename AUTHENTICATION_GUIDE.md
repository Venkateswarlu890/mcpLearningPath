# 🔐 Authentication & Database Guide

## Overview

This guide explains the authentication system and database structure for the AI Learning & Interview Platform. The system provides secure user management, session handling, and data persistence for learning paths and interview sessions.

## 🏗️ Architecture

### Authentication System
- **Secure Password Hashing**: Uses PBKDF2 with SHA-256 and random salts
- **Session Management**: Token-based sessions with expiration
- **User Registration**: Email validation and password strength requirements
- **Profile Management**: User profiles with preferences and progress tracking

### Database Structure
- **SQLite Database**: Lightweight, file-based database (`users.db`)
- **5 Main Tables**: Users, Sessions, Learning Progress, Interview Sessions, Preferences
- **Data Persistence**: Automatic saving of learning paths and interview results

## 📊 Database Schema

### 1. Users Table (`users`)
Stores user account information and authentication data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique user identifier |
| `username` | TEXT UNIQUE | User's chosen username |
| `email` | TEXT UNIQUE | User's email address |
| `password_hash` | TEXT | Hashed password (PBKDF2) |
| `salt` | TEXT | Random salt for password hashing |
| `full_name` | TEXT | User's full name (optional) |
| `created_at` | TIMESTAMP | Account creation date |
| `last_login` | TIMESTAMP | Last login timestamp |
| `is_active` | BOOLEAN | Account status (active/inactive) |
| `profile_data` | TEXT | JSON string of profile preferences |

### 2. User Sessions Table (`user_sessions`)
Manages user login sessions and tokens.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Session identifier |
| `user_id` | INTEGER | Foreign key to users table |
| `session_token` | TEXT UNIQUE | Secure session token |
| `created_at` | TIMESTAMP | Session creation time |
| `expires_at` | TIMESTAMP | Session expiration time |
| `is_active` | BOOLEAN | Session status |

### 3. Learning Progress Table (`learning_progress`)
Stores user learning paths and progress data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Progress record identifier |
| `user_id` | INTEGER | Foreign key to users table |
| `learning_goal` | TEXT | User's learning objective |
| `progress_data` | TEXT | JSON string of learning path data |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |
| `status` | TEXT | Progress status (active/completed) |

### 4. Interview Sessions Table (`interview_sessions`)
Stores mock interview session data and results.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Session identifier |
| `user_id` | INTEGER | Foreign key to users table |
| `interview_type` | TEXT | Type of interview (technical/behavioral) |
| `role` | TEXT | Interview role (python/data_science/etc.) |
| `language` | TEXT | Interview language (english/telugu/hindi) |
| `difficulty` | TEXT | Difficulty level (beginner/intermediate/advanced) |
| `session_data` | TEXT | JSON string of interview session data |
| `final_report` | TEXT | JSON string of final evaluation report |
| `created_at` | TIMESTAMP | Session start time |
| `completed_at` | TIMESTAMP | Session completion time |
| `status` | TEXT | Session status (active/completed) |

### 5. User Preferences Table (`user_preferences`)
Stores user-specific application preferences.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Preference record identifier |
| `user_id` | INTEGER UNIQUE | Foreign key to users table |
| `preferences_data` | TEXT | JSON string of user preferences |
| `updated_at` | TIMESTAMP | Last update time |

## 🔒 Security Features

### Password Security
- **PBKDF2 Hashing**: Industry-standard key derivation function
- **Random Salts**: Unique salt for each password
- **100,000 Iterations**: High iteration count for security
- **Password Validation**: Enforces strong password requirements

### Session Security
- **Secure Tokens**: Cryptographically secure random tokens
- **Session Expiration**: 7-day session lifetime
- **Automatic Cleanup**: Expired sessions are automatically removed
- **Token Validation**: Server-side session verification

### Data Protection
- **SQL Injection Prevention**: Parameterized queries
- **Input Validation**: Email format and password strength validation
- **Data Sanitization**: Proper handling of user inputs

## 📝 Data Examples

### Learning Progress Data Structure
```json
{
  "goal": "Learn Python basics in 3 days",
  "messages": [
    "Day 1: Python fundamentals and syntax",
    "Day 2: Data structures and control flow",
    "Day 3: Functions and modules"
  ],
  "generated_at": 1705312200,
  "api_config": {
    "secondary_tool": "Drive",
    "youtube_url": "https://pipedream.net/...",
    "drive_url": "https://pipedream.net/...",
    "notion_url": null
  }
}
```

### Interview Session Data Structure
```json
{
  "interview_type": "technical",
  "role": "python",
  "language": "english",
  "difficulty": "intermediate",
  "session_data": {
    "interview_history": [
      {
        "question": "Explain Python decorators",
        "answer": "Decorators are functions that modify other functions...",
        "evaluation": {
          "technical_score": 8,
          "communication_score": 7,
          "overall_score": 8
        }
      }
    ],
    "candidate_profile": {
      "name": "John Doe",
      "years_of_experience": 3,
      "skills": ["Python", "Django", "PostgreSQL"]
    },
    "pretest_result": {
      "score": 0.8,
      "passed": true
    }
  },
  "final_report": {
    "overall_score": 8,
    "strengths": ["Strong technical knowledge", "Clear communication"],
    "weaknesses": ["Could improve in system design"],
    "recommendations": ["Practice system design questions"]
  }
}
```

## 🚀 Getting Started

### 1. Initialize Database
```bash
python init_database.py
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
streamlit run app.py
```

### 4. Register Account
1. Click "Register" in the sidebar
2. Fill in username, email, and password
3. Password must meet security requirements:
   - At least 8 characters
   - Uppercase and lowercase letters
   - Numbers and special characters

### 5. Login and Use Features
1. Login with your credentials
2. Your learning paths and interview sessions will be automatically saved
3. View your profile to see progress history

## 🔧 API Reference

### AuthManager Class

#### `register_user(username, email, password, full_name=None)`
Registers a new user account.
- **Returns**: `(success: bool, message: str)`

#### `login_user(username_or_email, password)`
Authenticates user and creates session.
- **Returns**: `(success: bool, message: str)`

#### `logout_user()`
Logs out user and invalidates session.

#### `save_learning_progress(user_id, learning_goal, progress_data)`
Saves learning path data.
- **Returns**: `bool`

#### `save_interview_session(user_id, interview_data)`
Saves interview session data.
- **Returns**: `bool`

#### `get_user_profile(user_id)`
Retrieves user profile information.
- **Returns**: `Dict[str, Any]` or `None`

#### `get_learning_progress(user_id)`
Gets user's learning progress history.
- **Returns**: `List[Dict[str, Any]]`

#### `get_interview_sessions(user_id)`
Gets user's interview session history.
- **Returns**: `List[Dict[str, Any]]`

## 🛠️ Maintenance

### Database Backup
```bash
cp users.db users_backup_$(date +%Y%m%d).db
```

### Clean Expired Sessions
The system automatically cleans up expired sessions, but you can manually trigger it:
```python
from auth import auth_manager
auth_manager.cleanup_expired_sessions()
```

### Reset User Password
Currently, password reset requires manual database intervention. Future versions will include email-based password reset.

## 🔍 Troubleshooting

### Common Issues

1. **Database Locked Error**
   - Ensure no other processes are using the database
   - Check file permissions

2. **Session Expired**
   - User needs to login again
   - Sessions expire after 7 days

3. **Password Validation Failed**
   - Check password meets all requirements
   - Ensure no special characters are causing issues

4. **Email Already Exists**
   - Use a different email address
   - Check if account already exists

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## 🔮 Future Enhancements

- [ ] Email-based password reset
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration (Google, GitHub)
- [ ] Role-based access control
- [ ] Data export functionality
- [ ] Advanced analytics and reporting
- [ ] Multi-language support for UI
- [ ] API rate limiting
- [ ] Audit logging

## 📞 Support

For issues or questions about the authentication system:
1. Check this documentation first
2. Review the error messages in the application
3. Check the database file permissions
4. Ensure all dependencies are installed correctly

---

**Note**: This authentication system is designed for educational and development purposes. For production use, consider additional security measures such as HTTPS, database encryption, and regular security audits.
