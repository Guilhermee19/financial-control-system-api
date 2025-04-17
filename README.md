# Abrir um projeto clonado

python -m venv .venv


.venv\Scripts\activate       # Win
source .venv/bin/activate    # Linux

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py runserver

python manage.py createsuperuser