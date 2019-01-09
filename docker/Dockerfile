# VERSION 1
# AUTHOR: Seth Menghi
# DESCRIPTION: AWS Receipt Splitter
# BUILD: docker build --rm -t splitter/splitter .

FROM python:3
MAINTAINER Seth Menghi "sethmenghi@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y libpq-dev python3-dev
RUN apt-get install python3-psycopg2

EXPOSE 5000

# RUN apt-get install -y awscli
COPY . /app
WORKDIR /app

COPY ./docker/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# RUN ["chmod", "+x", "/app/docker/splitter-entrypoint.sh"]
ENTRYPOINT ["./docker/splitter-entrypoint.sh"]

CMD ["python", "-m", "flask", "run", "--port=5000", "--host=0.0.0.0"]
