import os
import oracledb
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

def get_db_connection():
    try:
        connection = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN")
        )
        return connection
    except oracledb.Error as e:
        print(f"Error conectando a Oracle: {e}")
        return None