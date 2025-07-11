#!/usr/bin/env python3
"""
Database setup script for Alternity Backend
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    
    database_url = os.getenv("DATABASE_URL")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_db = os.getenv("POSTGRES_DB")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        connection = psycopg2.connect(
            host="localhost",
            user=postgres_user,
            password=postgres_password
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{postgres_db}'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{postgres_db}"')
            print(f"✅ Database '{postgres_db}' created successfully")
        else:
            print(f"ℹ️  Database '{postgres_db}' already exists")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create database tables"""
    try:
        from app.deps import Base, engine
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up Alternity Backend Database...")
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please copy env_template.txt to .env and configure your settings")
        return
    
    # Create database
    if create_database():
        # Create tables
        create_tables()
        print("🎉 Database setup completed successfully!")
    else:
        print("❌ Database setup failed!")

if __name__ == "__main__":
    main() 