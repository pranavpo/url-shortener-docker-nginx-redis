import psycopg2
import os


def register_db():
    print(os.getenv("DATABASE_HOST"))
    print(os.getenv("DATABASE_USER"))
    print(os.getenv("DATABASE_NAME"))
    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOST", "127.0.0.1"),
        user=os.getenv("DATABASE_USER", "sql_shortener_dev"),
        password=os.getenv("DATABASE_PASSWORD", "sqlshortener"),
        dbname=os.getenv("DATABASE_NAME", "sql_shortener")
    )
    check_db_status(conn)
    return conn


def check_db_status(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'url_list'
        );
    """)

    table_exists = cur.fetchone()[0]

    if not table_exists:
        create_table(cur)
        print("Table 'url_list' created successfully.")
    else:
        print("Table 'url_list' already exists.")

    # Commit the transaction if a new table was created
    conn.commit()

    # Close the cursor and connection
    cur.close()
    return conn


def create_table(cur):
    cur.execute("""
            CREATE TABLE IF NOT EXISTS public.url_list (
                id SERIAL PRIMARY KEY,
                original_url TEXT NOT NULL,
                short_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
