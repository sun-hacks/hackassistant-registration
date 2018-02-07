FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 80

CMD [ "/usr/local/bin/gunicorn", "--workers", "3", "-b", "0.0.0.0:80", "--log-level", "debug", "--log-file", "-", "--access-logfile", "-", "app.wsgi:application"]
