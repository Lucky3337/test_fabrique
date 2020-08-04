FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY /requirements.txt /code/
RUN pip install -r requirements.txt

COPY ./compose/local/django/start_django.sh /start_django.sh
#RUN sed -i 's/\r$//g' /start-django
RUN chmod +x /start_django.sh

COPY . /code/