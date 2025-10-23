import os
import requests
import pandas as pd
import psycopg2
from datetime import datetime
import sys

API_URL = "https://randomuser.me/api/?results=50"

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

def validate_config():
    """Validate that all required environment variables are set"""
    required = {
        'DB_HOST': DB_HOST,
        'DB_PORT': DB_PORT,
        'DB_NAME': DB_NAME,
        'DB_USER': DB_USER,
        'DB_PASSWORD': DB_PASSWORD
    }
    
    missing = [key for key, value in required.items() if not value]
    
    if missing:
        print(f"[{datetime.now()}] ERROR: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    print(f"[{datetime.now()}] Configuration validated ✓")

def extract():
    """Extract: Fetch random users from API"""
    print(f"[{datetime.now()}] Extracting data...")
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()['results']
    print(f"[{datetime.now()}] {len(data)} users extracted")
    return data

def transform(data):
    """Transform: Simplify and clean the data"""
    print(f"[{datetime.now()}] Transforming data...")
    
    records = []
    for user in data:
        records.append({
            'first_name': user['name']['first'],
            'last_name': user['name']['last'],
            'email': user['email'],
            'gender': user['gender'],
            'country': user['location']['country'],
            'city': user['location']['city'],
            'age': user['dob']['age'],
            'phone': user['phone']
        })
    
    df = pd.DataFrame(records)
    df['recorded_at'] = datetime.now()
    
    print(f"[{datetime.now()}] Average age: {df['age'].mean():.1f} years")
    return df

def load(df):
    """Load: Insert data into PostgreSQL"""
    print(f"[{datetime.now()}] Connecting to database...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10
        )
    except psycopg2.OperationalError as e:
        print(f"[{datetime.now()}] ERROR: Cannot connect to database: {e}")
        raise
    
    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS random_users (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                gender VARCHAR(10),
                country VARCHAR(50),
                city VARCHAR(100),
                age INTEGER,
                phone VARCHAR(30),
                recorded_at TIMESTAMP
            )
        """)
        
        print(f"[{datetime.now()}] Loading data...")
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO random_users (first_name, last_name, email, gender, country, city, age, phone, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        
        conn.commit()
        print(f"[{datetime.now()}] {len(df)} rows loaded successfully ✓")
        
    except Exception as e:
        conn.rollback()
        print(f"[{datetime.now()}] Error during load: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def main():
    """Main ETL pipeline"""
    print(f"[{datetime.now()}] === Starting ETL Pipeline ===")
    
    validate_config()
    
    try:
        raw_data = extract()
        transformed_data = transform(raw_data)
        load(transformed_data)
        print(f"[{datetime.now()}] === Pipeline completed successfully ✓ ===")
    except Exception as e:
        print(f"[{datetime.now()}] Pipeline error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()