FROM python:3.7

COPY ./requirements.txt .
COPY ./app ./app
RUN apt update
RUN apt-get update -y
RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

USER root
CMD ["python3", "app/app.py"]