# [daily_report_web](https://github.com/obeh29380/daily_report_web)

With [daily_report_web](https://github.com/obeh29380/daily_report_web) you can create daily report app for demolition industry.

## Installation

### Check prerequisites

- docker  
- docker compose  

note: Can install docker, docker compose by execute `init_docker.sh`.

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

Then, DB will be migrated and app server will be started.

### register sample data(optional)

In app container, execute
```
sh /etc/drw/db/register_sample_data.sh
```

or out of container (on host)
```
docker exec drw-app sh /etc/drw/db/register_sample_data.sh
```
