# [daily_report_web](https://github.com/obeh29380/daily_report_web)

With [daily_report_web](https://github.com/obeh29380/daily_report_web) you can create daily report app for demolition industry.

## Installation

### Check prerequisites

- docker  
- docker compose  

Tips: Docker install scripts included: `init_docker.sh`.

### deploy settings

1. If connect with https
    1. Specify Host name
        - In `.env`, set `FQDN` (default: `localhost`)
        - Set environment env `FQDN` (This setting has the highest priority)
    1. Setup docker-compose.yml
        - rename docker-compose.yml.https to docker-compose.yml

2. If connect with http
    - rename docker-compose.yml.http to docker-compose.yml.

### deploy application

```
docker compose up -d
```

Then, App server will be started.

### register sample data(optional)

1. To create db, execute command below.
```
python /etc/drw/app/table.py
```

1. To register sample data, execute command below.
```
python /etc/drw/app/utils/json2db.py
```

### Informations

1. Access restriction
    - This application allow domestic(Japan) access only.
    - Setting in nginx.
        - `allowip.conf`
