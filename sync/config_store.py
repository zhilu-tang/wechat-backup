import os
import sqlite3
import threading
from functools import lru_cache

# 修改: 定义数据库文件的存储路径
DB_DIR = os.path.expanduser("~/.wechat_backup")
DB_PATH = os.path.join(DB_DIR, "wechat_backup.db")

# 确保数据库目录存在
os.makedirs(DB_DIR, exist_ok=True)


class Database:
    def __init__(self):
        self.local = threading.local()  # 每个线程拥有自己的连接
        self.ensure_tables_initialized()

    def __enter__(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(DB_PATH)
            self.local.connected  = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.local, 'conn'):
            self.local.conn.close()
            self.local.connected  = False

    def execute(self, query, params=None):
        if not self.local.conn or not self.local.connected:
            self.local.conn = sqlite3.connect(DB_PATH)  # 重新建立连接
        cursor = self.local.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.local.conn.commit()
            return cursor
        except Exception as e:
            self.local.conn.rollback()
            raise e

    def init_db(self):
        """初始化数据库和表结构"""
        with self as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS file_hashes (
                    file_path TEXT PRIMARY KEY,
                    hash_value TEXT
                )
                """
            )

    def ensure_tables_initialized(self):
        """确保数据库表已初始化"""
        try:
            with self as db:
                cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
                if not cursor.fetchone():
                    self.init_db()
        except sqlite3.OperationalError:
            self.init_db()

    def get_config(self, key, default=None):
        """从数据库中获取配置值"""
        with self as db:
            cursor = db.execute("SELECT value FROM config WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default

    def set_config(self, key, value):
        """在数据库中设置配置值"""
        with self as db:
            db.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, value),
            )

    def get_file_hash(self, file_path):
        """从数据库中获取文件哈希值"""
        with self as db:
            cursor = db.execute("SELECT hash_value FROM file_hashes WHERE file_path = ?", (file_path,))
            result = cursor.fetchone()
            return result[0] if result else None

    def set_file_hash(self, file_path, hash_value):
        """在数据库中设置文件哈希值"""
        with self as db:
            db.execute(
                "INSERT OR REPLACE INTO file_hashes (file_path, hash_value) VALUES (?, ?)",
                (file_path, hash_value),
            )

# 创建全局数据库实例
db = Database()

# 提供与原函数相同的接口
def get_config(key, default=None):
    """从数据库中获取配置值"""
    with db as db_instance:  # 使用全局 db 实例
        cursor = db_instance.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else default

def set_config(key, value):
    """在数据库中设置配置值"""
    with db as db_instance:  # 使用全局 db 实例
        db_instance.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, value),
        )

@lru_cache(maxsize=None)
def get_config(key, default_value):
    """从数据库中获取配置值"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else default_value

def set_config(key, value):
    """将配置值保存到数据库中"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        conn.commit()

def get_file_hash(file_path):
    """从数据库中获取文件的 MD5 哈希值"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS file_hashes (file_path TEXT PRIMARY KEY, file_hash TEXT)")
        cursor.execute("SELECT file_hash FROM file_hashes WHERE file_path = ?", (file_path,))
        result = cursor.fetchone()
        return result[0] if result else None

def set_file_hash(file_path, file_hash):
    """将文件的 MD5 哈希值保存到数据库中"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS file_hashes (file_path TEXT PRIMARY KEY, file_hash TEXT)")
        cursor.execute("INSERT OR REPLACE INTO file_hashes (file_path, file_hash) VALUES (?, ?)", (file_path, file_hash))
        conn.commit()

def get_file_hash(file_path):
    return db.get_file_hash(file_path)

def set_file_hash(file_path, hash_value):
    db.set_file_hash(file_path, hash_value)