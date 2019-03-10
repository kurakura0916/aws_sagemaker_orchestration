FROM python:3.6.3

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-dev

RUN pip3 install --upgrade pip

ADD config/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
