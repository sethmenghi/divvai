# VERSION 1
# AUTHOR: Seth Menghi
# DESCRIPTION: AWS Receipt Splitter
# BUILD: docker build --rm -t splitter/splitter .

FROM python:3
MAINTAINER Seth Menghi "sethmenghi@gmail.com"

RUN sudo apt-get update -y \
    sudo apt-get install -y \
        python-pip \
        python-dev \
        build-essential \
        libpq-dev \
        python3-dev \
        python-opencv \
        python3-psycopg2 \
        libjpeg-dev \
        libopencv-dev \
        libav-tools \
        libpng-dev \
        python-numpy \
        zlib1g-dev \
        awscli

COPY ./docker/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . /app
WORKDIR /app

# RUN ["chmod", "+x", "/app/docker/splitter-entrypoint.sh"]
ENTRYPOINT ["./docker/splitter-entrypoint.sh"]

CMD ["python", "-m", "flask", "run", "--port=5000", "--host=0.0.0.0"]
