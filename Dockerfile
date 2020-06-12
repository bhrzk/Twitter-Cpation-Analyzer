FROM python:3.7.5-buster
# FROM vernaai/analyzer:server

LABEL maintainer="Behrouz Kashanifar bhrzk1@gmail.com"


WORKDIR /var/www/html/
COPY ./requirements.txt /var/www/html/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /var/www/html/