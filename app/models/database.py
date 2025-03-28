import os
import psycopg2
from psycopg2 import pool
from .db_config import DB_CONFIG

class Database:
    _connection_pool = None
    
    @classmethod
    def initialize(cls, host=None, port=None, database=None, user=None, password=None, min_conn=None, max_conn=None):
        db_host = host or DB_CONFIG['host']
        db_port = port or DB_CONFIG['port']
        db_name = database or DB_CONFIG['database']
        db_user = user or DB_CONFIG['user']
        db_password = password or DB_CONFIG['password']
        db_min_conn = min_conn or DB_CONFIG['min_conn']
        db_max_conn = max_conn or DB_CONFIG['max_conn']
        
        try:
            cls._connection_pool = pool.ThreadedConnectionPool(
                minconn=db_min_conn,
                maxconn=db_max_conn,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            print(f"Пул соединений с базой данных {db_name} успешно инициализирован")
        except Exception as e:
            print(f"Ошибка инициализации пула соединений: {e}")
            cls._connection_pool = None
    
    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize()
            
        if cls._connection_pool is None:
            raise Exception("Пул соединений не инициализирован")
            
        return cls._connection_pool.getconn()
    
    @classmethod
    def release_connection(cls, connection):
        if cls._connection_pool is not None:
            cls._connection_pool.putconn(connection)
    
    @classmethod
    def execute_query(cls, query, params=None):
        connection = None
        cursor = None
        result = None
        
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Если это SELECT запрос
            if query.lower().strip().startswith("select"):
                result = cursor.fetchall()
            
            connection.commit()
            return result
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                cls.release_connection(connection)
    
    @classmethod
    def close_all(cls):
        if cls._connection_pool:
            cls._connection_pool.closeall()
            print("Все соединения с базой данных закрыты")
            cls._connection_pool = None 
            