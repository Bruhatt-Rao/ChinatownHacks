import os
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse

class Database:
    def __init__(self, database_url=None):
        self.conn = None
        self.cursor = None
        self.database_url = database_url or os.getenv('DATABASE_URL')

    def connect(self):
        if not self.conn:
            try:
                if self.database_url:
                    # Use connection string directly if provided
                    self.conn = psycopg2.connect(self.database_url)
                else:
                    # Fall back to individual parameters
                    self.conn = psycopg2.connect(
                        dbname=os.getenv('POSTGRES_DB', 'chinatown'),
                        user=os.getenv('POSTGRES_USER', 'postgres'),
                        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
                        host=os.getenv('POSTGRES_HOST', 'localhost'),
                        port=os.getenv('POSTGRES_PORT', '5432')
                    )
                self.cursor = self.conn.cursor(cursor_factory=DictCursor)
            except psycopg2.Error as e:
                print(f"Database connection error: {e}")
                raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def init_db(self):
        self.connect()
        # Drop the existing table if it exists
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.conn.commit()
        
        # Create the table with larger column sizes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(512) NOT NULL
            )
        """)
        self.conn.commit()

    def get_user_by_id(self, user_id):
        self.connect()
        self.cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = self.cursor.fetchone()
        return dict(user) if user else None

    def get_user_by_username(self, username):
        self.connect()
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = self.cursor.fetchone()
        return dict(user) if user else None

    def get_user_by_email(self, email):
        self.connect()
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = self.cursor.fetchone()
        return dict(user) if user else None

    def create_user(self, username, email, password):
        self.connect()
        password_hash = generate_password_hash(password)
        try:
            self.cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (username, email, password_hash)
            )
            user_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return user_id
        except psycopg2.IntegrityError:
            self.conn.rollback()
            return None

    def verify_password(self, username, password):
        user = self.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

# Create a global database instance
db = Database() 