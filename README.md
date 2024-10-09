## 📄 목차
1. [프로젝트명](#1-프로젝트명)
2. [프로젝트 소개](#2-프로젝트-소개)
3. [팀 소개](#3-travelers-팀-소개)
4. [주요기능](#4-주요기능)
5. [개발기간](#5-개발기간)
6. [개발환경](#6-개발환경)
7. [ERD](#7-erd)
8. [프로젝트 파일 구조](#8-프로젝트-파일-구조)
9. [Trouble Shooting](#9-trouble-shooting)

<br>

# 1. 프로젝트명
### SceneTrip
<br>

# 2. 프로젝트 소개
    국내 영화,드라마,예능 등 미디어콘텐츠 속 촬영지정보를 제공하고, 사용자에게 촬영지를 중심으로 한 여행플랜을 추천해주는 사이트

<br>

# 3. Travelers 팀 소개
  
[팀노션 이동](https://www.notion.so/teamsparta/Travelers-fff2dc3ef5148189b38ff20c0d472b26)

| - |주성현|강다영|김경민|조민희|
|:---:|:---:|:---:|:---:|:---:|
| <b>역할</b> |팀장|부팀장|서기|조원|
| <b>Backend</b> |Journals/Comment <br>Communities/Comment | Locations <br>API활용(한국문화정보원 미디어콘텐츠 영상촬영지데이터) | Accounts | Journals/Article <br>Communities/Article |
| <b>Frontend</b> | 전체 | - | - | - |
| <b>배포</b> | - | - | 전체 | - |

<br>

## 4. 주요기능
|Accounts|Journals|Communities|Locations|
|:---|:---|:---|:---|
|-회원가입 <br>-로그인<br>-로그아웃 <br>-마이페이지 <br>-구독 <br>-회원탈퇴| 저널 조회&검색 <br>-저널 작성 <br>-저널 수정 <br>-저널 삭제 <br>-댓글 기능 <br>-대댓글 기능 <br>-댓글, 대댓글 신고 |-커뮤니티 조회&검색 <br>-커뮤니티 작성 <br>-커뮤니티 수정 <br>-커뮤니티 삭제 <br>-커뮤니티글 신고 <br>-댓글 기능 <br>-대댓글 기능 <br>-댓글, 대댓글 신고 |-촬영지 조회 <br>-촬영지 검색 <br>-촬영지 저장 <br>-여행플랜 추천 |

<br>


## 5. 개발기간
    2024.09.23.(월) ~ 2024.09.25.(수) | SA문서 작성
    2024.09.26.(목) ~ 2024.10.03.(목) | 1차개발 완료 후 머지
    2024.10.04.(금) ~ 2024.10.06.(월) | 코드보완
    2024.10.07.(화) ~ 2024.10.08.(수) | 프론트엔드 시작

<br>

## 6. 개발환경
    Django                           4.2
    djangorestframework              3.15.2
    djangorestframework-simplejwt    5.3.1
    django-seed                      0.3.1
    Faker                            30.0.0
    django-hitcount                  1.3.5
    pillow                           10.4.0
    pytz                             2024.2
    tzdata                           2024.2
    PyJWT                            2.9.0


<br>

## 7. ERD
(추후 첨부)
<br>

## 8. 프로젝트 파일 구조 
```
📦SceneTrip
┣ 📂accounts
 ┃ ┣ 📂migrations
 ┃ ┃ ┣ 📜0001_initial.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📜admin.py
 ┃ ┣ 📜apps.py
 ┃ ┣ 📜emails.py
 ┃ ┣ 📜models.py
 ┃ ┣ 📜serializers.py
 ┃ ┣ 📜tests.py
 ┃ ┣ 📜urls.py
 ┃ ┣ 📜views.py
 ┃ ┗ 📜__init__.py
 ┣ 📂communities
 ┃ ┣ 📂migrations
 ┃ ┃ ┣ 📜0001_initial.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📜admin.py
 ┃ ┣ 📜apps.py
 ┃ ┣ 📜models.py
 ┃ ┣ 📜serializers.py
 ┃ ┣ 📜tests.py
 ┃ ┣ 📜urls.py
 ┃ ┣ 📜views.py
 ┃ ┗ 📜__init__.py
 ┣ 📂journals
 ┃ ┣ 📂migrations
 ┃ ┃ ┣ 📜0001_initial.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📜admin.py
 ┃ ┣ 📜apps.py
 ┃ ┣ 📜models.py
 ┃ ┣ 📜serializers.py
 ┃ ┣ 📜tests.py
 ┃ ┣ 📜urls.py
 ┃ ┣ 📜views.py
 ┃ ┗ 📜__init__.py
 ┣ 📂locations
 ┃ ┣ 📂management
 ┃ ┃ ┗ 📂commands
 ┃ ┃ ┃ ┗ 📜import_locations.py
 ┃ ┣ 📂migrations
 ┃ ┃ ┣ 📜0001_initial.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📜admin.py
 ┃ ┣ 📜apps.py
 ┃ ┣ 📜check_tables.py
 ┃ ┣ 📜models.py
 ┃ ┣ 📜serializers.py
 ┃ ┣ 📜tests.py
 ┃ ┣ 📜urls.py
 ┃ ┣ 📜views.py
 ┃ ┗ 📜__init__.py
 ┣ 📂SceneTrip
 ┃ ┣ 📜asgi.py
 ┃ ┣ 📜settings.py
 ┃ ┣ 📜urls.py
 ┃ ┣ 📜wsgi.py
 ┃ ┗ 📜__init__.py
 ┣ 📜.gitignore
 ┣ 📜.gitmessage.txt
 ┣ 📜manage.py
 ┣ 📜README.md
 ┣ 📜requirements.txt
 ┣ 📜secrets.json
 ┗ 📜한국문화정보원_미디어콘텐츠 영상 촬영지 데이터_20221125.csv
 ```
<br>

## 9. Trouble Shooting
