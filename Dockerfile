FROM python:3.11

USER root

RUN mkdir /etc/drw
COPY app/ /etc/drw/app
COPY setup/ /etc/drw/setup
RUN apt update
RUN apt-get update -y
RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install -r /etc/drw/setup/requirements.txt
# CMD ["uvicorn", "main:app", "--reload"]
