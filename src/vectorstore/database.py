import psycopg

from pgvector.psycopg import register_vector

from config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER


def get_connection():
    """
    Create and configure a PostgreSQL connection.
    """

    connection = psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )

    register_vector(connection)

    return connection


if __name__ == "__main__":
    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("SELECT current_database(), current_user;")
            database, user = cursor.fetchone()

            print(f"Database: {database}")
            print(f"User: {user}")

            cursor.execute(
                """
                SELECT extversion
                FROM pg_extension
                WHERE extname = 'vector';
                """
            )

            result = cursor.fetchone()

            print("pgvector:", result[0] if result else "not installed")

            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'document_chunks'
                );
                """
            )

            table_exists = cursor.fetchone()[0]
            print("document_chunks:", table_exists)