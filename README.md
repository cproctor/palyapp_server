# Paly App

This is the server for a pilot mobile app to distribute Paly's journalism 
content over mobile. The pilot app's goals are to increase reader participation, 
feedback, and discussion. We will do this by:

- Developing a filtering/tagging system to help readers find content they care about,
- Providing a forum for discussion. Users must register, but can post anonymously or with their names attached
- Making reader comments a more significant part of the content
- Helping connect readers with journalists

## Installation

    git clone https://github.com/cproctor/palyapp_server.git
    python3 -m venv env
    source env/bin/activate
    cd palyapp_server
    pip install -r requirements.txt
    cp palyapp/settings-default.py palyapp/settings.py
    python manage.py migrate
    python manage.py loaddata stories2/fixtures/publications.fixture.json
    python manage.py runserver
    open http://127.0.0.1:8000/v2/
    
