# [daily_report_web](https://github.com/obeh29380/daily_report_web)

With [daily_report_web](https://github.com/obeh29380/daily_report_web) you can create daily report app for demolition industry.

## Installation

### Check prerequisites

- docker  
- docker compose  

Tips: Docker install scripts included: `init_docker.sh`.

### deploy settings

1. Specify Host name if use
    - In `.env`, set `FQDN` (default: `localhost`)
    - Set environment env `FQDN` (This setting has the highest priority)

2. Https settings
    - If use https, edit default.conf and docker-compose.yml to accept access by domain name.
        - maybe, all you have to do is uncomment it out.
    - Also, set hostname by follow step 1.

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
