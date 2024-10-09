## 📄 목차
1. [Project Title](#1-project-title)
2. [Project Introduction](#2-project-introduction)
3. [Team Introduction](#3-team-introduction)
4. [Features](#4-features)
5. [Development Period](#5-development-period)
6. [Requirements](#6-requirements)
7. [ERD](#7-erd)
8. [Project Structure](#8-project-structure)
9. [Trouble Shooting](#9-trouble-shooting)

<br>

# 1. Project Title
        SceneTrip
<br>

# 2. Project Introduction
        A site that provides information on filming locations in media contents such as domestic movies, dramas, and entertainment, and recommends travel plans centered on filming locations to users
<br>

# 3. Team Introduction
### 팀명 : Travelers  
[팀노션 이동](https://www.notion.so/teamsparta/Travelers-fff2dc3ef5148189b38ff20c0d472b26)

| - |주성현|강다영|김경민|조민희|
|:---:|:---:|:---:|:---:|:---:|
| <b>역할</b> |팀장|부팀장|서기|조원|
| <b>Backend</b> |Journals/Comment <br>Communities/Comment | Locations <br>Interlocking an API(한국문화정보원 미디어콘텐츠 영상촬영지데이터) | Accounts | Journals/Article <br>Communities/Article |
| <b>Frontend</b> | 전체 | - | - | - |
| <b>배포</b> | - | - | 전체 | - |

<br>

## 4. Features
|Accounts|Journals|Communities|Locations|
|:---|:---|:---|:---|
|-Sign up <br>-Sign in<br>-Sign out <br>-Mypage <br>-Subscribing <br>-Withdrawl| Journal inquiry & search <br>-Journal creation <br>-Journal modification <br>-Delete journal <br>-Comment features <br>-Reply features <br>-Like for jouranl <br>-Report comment, reply |-Community inquiry & search <br>-Community creation <br>-Community modification <br>-Delete community <br>-Report community <br>-Comment features <br>-Reply features <br>-Report community, comment, reply |-Location inquiry <br>-Location search <br>-Save for locations <br>-Travel plan recommendation |

<br>


## 5. Development Period
    2024.09.23.(월) ~ 2024.09.25.(수) | Creation of SA Document
    2024.09.26.(목) ~ 2024.10.03.(목) | Back-End Development Completed, GitHub Merge
    2024.10.04.(금) ~ 2024.10.06.(월) | Complement Code
    2024.10.07.(화) ~ 2024.10.08.(수) | Front-End Development

<br>

## 6. Requirements
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

## 8. Project Structure 
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

### ◻ Open API Usage Issues
> * <b>Problems</b> : <br>(1) In order for the open API to be used to be linked to functions such as alignment and classification of our project, it had to go through a separately implemented API. <br>(2) Open APIs are slower because they are more than twice the number of data that can be retrieved at once.
> * <b>Solutions</b> : <br> Instead of open API, we decided to receive data directly from csv file and use it. <br> * Whenever the data is updated, we need to get the csv file back and update the DB of our project.
### ◻ Safety Risks In Changing Password, Changing Email
> * <b>Problems</b> : 개인정보를 알고 있기만 하면 회원정보를 변경할 수 있는 점.
> * <b>Solutions</b> : 비밀번호변경, 이메일변경을 시도하면 이메일인증을 거치도록 단계를 강화함.
