#!/usr/bin/env python3
"""
Script to check PostgreSQL data in Docker container
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/food_delivery"

def check_database_data():
    """Check data in the PostgreSQL database"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            print("🔍 Checking PostgreSQL Database Data...")
            print("=" * 50)
            
            # Check if users table exists and has data
            try:
                result = db.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                print(f"👥 Total Users: {user_count}")
                
                if user_count > 0:
                    print("\n📋 User Details:")
                    print("-" * 30)
                    users = db.execute(text("""
                        SELECT id, email, name, role, created_at, is_active 
                        FROM users 
                        ORDER BY created_at DESC
                    """)).fetchall()
                    
                    for user in users:
                        print(f"ID: {user.id}")
                        print(f"Email: {user.email}")
                        print(f"Name: {user.name}")
                        print(f"Role: {user.role}")
                        print(f"Active: {user.is_active}")
                        print(f"Created: {user.created_at}")
                        print("-" * 30)
                
            except Exception as e:
                print(f"❌ Error checking users table: {e}")
            
            # Check all tables
            print("\n📊 Database Tables:")
            print("-" * 30)
            tables = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
            
            for table in tables:
                table_name = table[0]
                try:
                    count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = count_result.scalar()
                    print(f"📋 {table_name}: {count} records")
                except Exception as e:
                    print(f"📋 {table_name}: Error - {e}")
            
            print("\n✅ Database check completed!")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure Docker PostgreSQL is running:")
        print("docker compose up -d postgres")

if __name__ == "__main__":
    check_database_data()
