 FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN /usr/local/bin/python -m pip install --upgrade pip
 RUN mkdir /code
 WORKDIR /code
 ADD requirements.txt /code/
 RUN pip install -r requirements.txt
 ADD . /code/
 #docker-compose run web python manage.py migrate
