import sqlite3

# 데이터베이스 파일 경로
db_path = 'locationdata.sqlite3'

# 데이터베이스 연결
conn = sqlite3.connect(db_path)

# 커서 생성
cursor = conn.cursor()

# 테이블 목록 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:", tables)

# 연결 종료
conn.close()