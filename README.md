# Question_bot_v2_Randy_ver
DIscord Question_bot_Randy_ver

디스코드를 기반으로 제작되었으며 python 3.7.5버전을 사용하여 제작된 봇입니다

2026년 09월 03일 최종 테스트 3.9.2 파이썬에서 구동되었습니다.

## Setting
파이썬을 **3.9**버전 이하로 다운하여 셋팅해주세요 [[python download]](https://www.python.org/)

파이썬을 설치까지 완료되었다면 module_setup.bat을 실행시켜주세요!

2026년 09월 03일 discord 2.0 py는 discord 모듈만 설치만 해도 모든 기능 사용가능합니다.
     
꼭 pip 최신화 및 discord.py 설치 해주세요.

Windows
python -m pip install --upgrade pip

pip install discord.py

Linux
가상환경 설정후 ( 가상환경 아래 확인 )

pip install --upgrade pip

pip install discord.py

## Bot
봇 생성 디스코드 개발자 포털 : [DISCORD DEVELOPER PORTAL](https://discord.com/developers/applications)

봇을 생성 후 봇 토큰 확인 페이지 아래에 있는 PRESENCE INTENT, SERVER MEMBERS INTENT 이 2개를 꼭 켜주세요!

## Start Bot
위 사항들이 모두 완료되었다면 (윈도우 전용) Start_bot.bat파일을 실행시켜주세요!

리눅스는 터미널에서 가상환경 변수를 만들어 실행하세요!

1. 봇 프로젝트 폴더로 이동
cd /home/user/question_bot_v2-main_Randy_ver ( 경로 확인 후 터미널 입력 )

2. 파이썬 가상환경 생성 (최초 1회만)
python3 -m venv venv

3. 가상환경 활성화
source venv/bin/activate

4. 봇 실행
python3 main.py
