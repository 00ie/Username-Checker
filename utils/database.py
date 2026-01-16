import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class Database:
    
    def __init__(self, db_path: str = "data/username_checker.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.create_tables()
    
    def connect(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                platforms_checked TEXT NOT NULL,
                platforms_available TEXT NOT NULL,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                total_checked INTEGER DEFAULT 0,
                total_available INTEGER DEFAULT 0,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                was_available BOOLEAN,
                platforms_available TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                platforms TEXT NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        conn.commit()
    
    def save_check_result(self, username: str, platforms_checked: List[str], 
                         platforms_available: List[str], session_id: Optional[str] = None):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO check_results (username, platforms_checked, platforms_available, session_id)
            VALUES (?, ?, ?, ?)
        ''', (
            username,
            json.dumps(platforms_checked),
            json.dumps(platforms_available),
            session_id
        ))
        
        conn.commit()
    
    def get_check_history(self, limit: int = 100, username: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.connect()
        cursor = conn.cursor()
        
        if username:
            cursor.execute('''
                SELECT * FROM check_results 
                WHERE username = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (username, limit))
        else:
            cursor.execute('''
                SELECT * FROM check_results 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'username': row['username'],
                'timestamp': row['timestamp'],
                'platforms_checked': json.loads(row['platforms_checked']),
                'platforms_available': json.loads(row['platforms_available']),
                'session_id': row['session_id']
            })
        
        return results
    
    def create_session(self, session_id: str, config: Dict[str, Any]):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (id, config)
            VALUES (?, ?)
        ''', (session_id, json.dumps(config)))
        
        conn.commit()
    
    def update_session_stats(self, session_id: str, total_checked: int, total_available: int):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET total_checked = ?, total_available = ?
            WHERE id = ?
        ''', (total_checked, total_available, session_id))
        
        conn.commit()
    
    def end_session(self, session_id: str):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET ended_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
    
    def add_to_favorites(self, username: str, platforms: List[str], notes: str = ""):
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO favorites (username, platforms, notes)
                VALUES (?, ?, ?)
            ''', (username, json.dumps(platforms), notes))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_favorites(self) -> List[Dict[str, Any]]:
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM favorites ORDER BY added_at DESC')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'username': row['username'],
                'platforms': json.loads(row['platforms']),
                'added_at': row['added_at'],
                'notes': row['notes']
            })
        
        return results
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_checks,
                COUNT(CASE WHEN platforms_available != '[]' THEN 1 END) as total_available,
                COUNT(DISTINCT username) as unique_usernames
            FROM check_results
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        row = cursor.fetchone()
        
        return {
            'total_checks': row['total_checks'],
            'total_available': row['total_available'],
            'unique_usernames': row['unique_usernames'],
            'success_rate': (row['total_available'] / row['total_checks'] * 100) if row['total_checks'] > 0 else 0
        }
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


db = Database()
