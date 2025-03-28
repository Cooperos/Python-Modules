import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'postgres'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'weldingandsons'),
    'user': os.environ.get('DB_USER', 'weldingandsons-dbadmin'),
    'password': os.environ.get('DB_PASSWORD', '1234'),
    'min_conn': int(os.environ.get('DB_MIN_CONN', 1)),
    'max_conn': int(os.environ.get('DB_MAX_CONN', 10))
} 
