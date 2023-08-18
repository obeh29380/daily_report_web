#!/bin/bash

cd /etc/drw/db
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head

cd /
