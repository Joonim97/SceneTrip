import unittest
import sqlite3
from unittest.mock import patch

class TestCheckTables(unittest.TestCase):

    def setUp(self):
        # 메모리내 SQLite 데이터베이스 생성
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        # 테스트용 테이블
        self.cursor.execute('''CREATE TABLE test_table (
                            id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
        self.conn.commit()

    def tearDown(self):
        # 테스트 후 연결닫음
        self.conn.close()

    @patch('check_tables.sqlite3.connect')
    def test_check_tables(self, mock_connect):
        # mock 객체에 DB를 연결하도록 설정함
        mock_connect.return_value = self.conn

        # check_tables.py의 로직을 직접 실행하여 테이블 확인
        from check_tables import db_path, conn, cursor
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # 'test_table'이 있는지 확인
        self.assertIn(('test_table',), tables)
        print("Tables in the database:", tables)

if __name__ == '__main__':
    unittest.main()
