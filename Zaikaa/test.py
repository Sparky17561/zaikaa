import psycopg2
from psycopg2 import sql

# Database connection credentials
host = "localhost"
port = 5432
user = "postgres"
password = "abc123"  # Replace with your PostgreSQL password

# Step 1: Connect to the default 'postgres' database
try:
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="postgres")
    conn.autocommit = True  # Enable autocommit mode for database creation
    cursor = conn.cursor()

    # Step 2: Create the 'zaikaa' database
    cursor.execute("CREATE DATABASE zaikaa;")
    print("Database 'zaikaa' created successfully!")

    # Close connection to 'postgres' and reconnect to 'zaikaa'
    cursor.close()
    conn.close()

    # Step 3: Connect to the 'zaikaa' database
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="zaikaa")
    cursor = conn.cursor()

    # Step 4: Create the 'shops' table
    create_table_query = """
    CREATE TABLE shops (
        shop_id SERIAL PRIMARY KEY,
        shop_name VARCHAR(100) UNIQUE,
        passkey VARCHAR(5) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'shops' created successfully!")

except psycopg2.Error as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
