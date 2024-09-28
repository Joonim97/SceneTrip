# 데이터 업데이트 시 파일 변경 필요.
# 그때마다 csv형식의 데이터를 json형식으로 변환시켜줘야 함.
# 이를 위한 코드.


import csv
import sqlite3

# 파일 읽기
fileName = r"C:\SceneTrip\한국문화정보원_미디어콘텐츠 영상 촬영지 데이터_20221125.csv"
file = open(fileName, "r", encoding="cp949")
reader = csv.DictReader(file)

# DB연결 및 커서 객체 생성
dbConn = sqlite3.connect(r"C:\SceneTrip\locationdata.sqlite3")
cs = dbConn.cursor()

# 테이블 생성
cs.execute(
    """
CREATE TABLE IF NOT EXISTS location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    연번 NUMERIC,
    미디어타입 VARCHAR,
    제목 VARCHAR,
    장소명 VARCHAR,
    장소타입 VARCHAR,
    장소설명 VARCHAR,
    영업시간 VARCHAR,
    브레이크타임 VARCHAR,
    휴무일 VARCHAR,
    주소 VARCHAR,
    위도 NUMERIC,
    경도 NUMERIC,
    전화번호 VARCHAR,
    최종작성일 CHAR
)
"""
)

data = []

for row in reader:
    data.append(row)

for row in data:
    str_sql = """
    INSERT INTO location (
        연번, 미디어타입, 제목, 장소명, 장소타입, 장소설명, 영업시간, 브레이크타임, 휴무일, 주소, 위도, 경도, 전화번호, 최종작성일
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cs.execute(
        str_sql,
        (
            row["연번"],
            row["미디어타입"],
            row["제목"],
            row["장소명"],
            row["장소타입"],
            row["장소설명"],
            row["영업시간"],
            row["브레이크타임"],
            row["휴무일"],
            row["주소"],
            row["위도"],
            row["경도"],
            row["전화번호"],
            row["최종작성일"],
        ),
    )

dbConn.commit()

print("CSV파일의 데이터가 DB에 입력되었습니다.")

cs.close()
dbConn.close()
