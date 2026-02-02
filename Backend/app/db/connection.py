from databases import Database

from dotenv import load_dotenv, find_dotenv
import os

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        load_dotenv(find_dotenv(), override=False)
        self.conn = self._connection_database()

    def _get_connection_string(self) -> str:
        return os.getenv("DB_CONNECTION")
    
    def _connection_database(self) -> Database:
        return Database(self._get_connection_string())
        