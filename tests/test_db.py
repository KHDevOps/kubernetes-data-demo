import psycopg2
import os

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)),
    database=os.getenv('DB_NAME', 'postgres'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'testpassword')
)

cursor = conn.cursor()
cursor.execute('SELECT version();')
print(f'✅ Database connection successful')

cursor.close()
conn.close()
