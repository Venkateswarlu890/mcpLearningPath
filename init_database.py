"""
Database initialization script for the AI Learning & Interview Platform
Run this script to set up the database and create initial tables
"""

from auth import auth_manager
import sqlite3
import os

def init_database():
    """Initialize the database with all required tables"""
    print("🔧 Initializing database...")
    
    # The auth_manager automatically creates tables when initialized
    # Let's verify the database was created successfully
    if os.path.exists("users.db"):
        print("✅ Database file created successfully")
        
        # Test database connection
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        print("✅ Database initialization completed successfully!")
        
        # Show database schema
        print("\n📋 Database Schema:")
        print("=" * 50)
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        # Get table schemas
        tables_to_show = ['users', 'user_sessions', 'learning_progress', 'interview_sessions', 'user_preferences']
        
        for table_name in tables_to_show:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"\n🔹 {table_name.upper()} Table:")
            for col in columns:
                col_id, name, data_type, not_null, default_val, pk = col
                pk_marker = " (PRIMARY KEY)" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default_val}" if default_val else ""
                print(f"   {name}: {data_type}{null_marker}{default_marker}{pk_marker}")
        
        conn.close()
        
    else:
        print("❌ Database file was not created")

def show_sample_data():
    """Show sample data structure for each table"""
    print("\n📝 Sample Data Structure:")
    print("=" * 50)
    
    print("\n👤 USERS Table Sample:")
    print("""
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "password_hash": "hashed_password_here",
        "salt": "random_salt_here",
        "full_name": "John Doe",
        "created_at": "2024-01-15 10:30:00",
        "last_login": "2024-01-15 14:20:00",
        "is_active": 1,
        "profile_data": "{\"preferences\": {...}}"
    }
    """)
    
    print("\n🔐 USER_SESSIONS Table Sample:")
    print("""
    {
        "id": 1,
        "user_id": 1,
        "session_token": "random_session_token",
        "created_at": "2024-01-15 10:30:00",
        "expires_at": "2024-01-22 10:30:00",
        "is_active": 1
    }
    """)
    
    print("\n📚 LEARNING_PROGRESS Table Sample:")
    print("""
    {
        "id": 1,
        "user_id": 1,
        "learning_goal": "Learn Python basics in 3 days",
        "progress_data": "{\"messages\": [...], \"generated_at\": 1705312200}",
        "created_at": "2024-01-15 10:30:00",
        "updated_at": "2024-01-15 10:30:00",
        "status": "active"
    }
    """)
    
    print("\n🎯 INTERVIEW_SESSIONS Table Sample:")
    print("""
    {
        "id": 1,
        "user_id": 1,
        "interview_type": "technical",
        "role": "python",
        "language": "english",
        "difficulty": "intermediate",
        "session_data": "{\"interview_history\": [...], \"candidate_profile\": {...}}",
        "final_report": "{\"overall_score\": 8, \"strengths\": [...], ...}",
        "created_at": "2024-01-15 10:30:00",
        "completed_at": "2024-01-15 11:00:00",
        "status": "completed"
    }
    """)
    
    print("\n⚙️ USER_PREFERENCES Table Sample:")
    print("""
    {
        "id": 1,
        "user_id": 1,
        "preferences_data": "{\"theme\": \"dark\", \"notifications\": true, ...}",
        "updated_at": "2024-01-15 10:30:00"
    }
    """)

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    print("\n🧹 Cleaning up expired sessions...")
    auth_manager.cleanup_expired_sessions()
    print("✅ Expired sessions cleaned up")

if __name__ == "__main__":
    print("🚀 AI Learning & Interview Platform - Database Initialization")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Show sample data structure
    show_sample_data()
    
    # Clean up expired sessions
    cleanup_expired_sessions()
    
    print("\n🎉 Database setup completed!")
    print("\n📖 Next steps:")
    print("1. Run the main application: streamlit run app.py")
    print("2. Register a new user account")
    print("3. Start creating learning paths and taking interviews")
    print("4. Your progress will be automatically saved!")
