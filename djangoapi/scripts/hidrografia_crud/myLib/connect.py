from myLib import settings
import psycopg

def connect():
    conn= psycopg.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
        )
    print("Connected")
    return conn