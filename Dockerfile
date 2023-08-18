FROM python:3.7

USER root

RUN mkdir /etc/drw
COPY app/ /etc/drw/app
COPY setup/ /etc/drw/setup
COPY db/ /etc/drw/db
# RUN chmod 777 /etc/drw/db/setup_db.sh
RUN apt update
RUN apt-get update -y
RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install -r /etc/drw/setup/requirements.txt
# RUN sh /etc/drw/db/setup_db.sh >> /etc/drw/db/setup_db.log
RUN export PYTHONPATH="/etc/drw/db/:$PYTHONPATH"
# ENTRYPOINT [ "/etc/drw/db/migrate_db.sh" ]
CMD ["python3", "/etc/drw/app/app.py"]