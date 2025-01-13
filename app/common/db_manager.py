import sqlite3
import base64
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='app/data/history.db'):
        self.db_path = db_path
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    image_data TEXT NOT NULL,
                    latex_result TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    request_id TEXT NOT NULL,
                    UNIQUE(request_id)
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"数据库初始化错误: {e}")
        finally:
            if conn:
                conn.close()

    def add_record(self, image_data, latex_result, confidence, request_id):
        """添加记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 将图片转换为base64
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        else:
            image_base64 = image_data
            
        try:
            cursor.execute('''
                INSERT INTO history (timestamp, image_data, latex_result, confidence, request_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), image_base64, latex_result, confidence, request_id))
            conn.commit()
            # 获取新插入记录的ID
            record_id = cursor.lastrowid
            print(f"Added new record with ID: {record_id}")
            return record_id  # 返回新记录的ID
        except sqlite3.IntegrityError:
            # 如果request_id已存在，则更新记录
            cursor.execute('''
                UPDATE history 
                SET timestamp=?, image_data=?, latex_result=?, confidence=?
                WHERE request_id=?
            ''', (datetime.now(), image_base64, latex_result, confidence, request_id))
            conn.commit()
            # 获取更新记录的ID
            cursor.execute('SELECT id FROM history WHERE request_id=?', (request_id,))
            record_id = cursor.fetchone()[0]
            print(f"Updated existing record with ID: {record_id}")
            return record_id  # 返回更新记录的ID
        finally:
            conn.close()

    def get_records(self, page=1, page_size=10, search_text=None):
        """获取记录（支持分页和搜索）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询条件
        where_clause = ""
        params = []
        if search_text:
            where_clause = "WHERE latex_result LIKE ?"
            params.append(f"%{search_text}%")
        
        # 获取总记录数
        count_sql = f"SELECT COUNT(*) FROM history {where_clause}"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * page_size
        sql = f"""
            SELECT id, timestamp, image_data, latex_result, confidence, request_id 
            FROM history {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [page_size, offset])
        records = cursor.fetchall()
        
        conn.close()
        
        return records, total_count

    def delete_record(self, record_id):
        """删除记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM history WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

    def clear_history(self):
        """清空历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def update_latex(self, record_id, latex):
        """更新记录的 LaTeX 内容"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            sql = 'UPDATE history SET latex_result = ? WHERE id = ?'
            params = (latex, record_id)
            print(f"Executing SQL: {sql} with params: {params}")  # 打印SQL语句和参数
            cursor.execute(sql, params)
            conn.commit()
            print(f"Rows affected: {cursor.rowcount}")  # 打印受影响的行数
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating latex: {e}")
            return False 

    def get_history_records(self, page=1, page_size=10, search_text=None):
        """获取历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询条件
        where_clause = ""
        params = []
        if search_text:
            where_clause = "WHERE latex_result LIKE ?"
            params = [f"%{search_text}%"]
            
        # 获取总记录数
        count_sql = f"SELECT COUNT(*) FROM history {where_clause}"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取分页数据
        sql = f"""
            SELECT id, timestamp, image_data, latex_result, confidence, request_id 
            FROM history {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [page_size, offset])
        records = cursor.fetchall()
        
        conn.close()
        
        return records, total_count 