# [daily_report_web](https://github.com/obeh29380/daily_report_web)

With [daily_report_web](https://github.com/obeh29380/daily_report_web) you can create daily report app for demolition industry.

## Installation

### Check prerequisites

- docker
- docker compose

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
docker exec app sh /etc/drw/db/register_sample_data.sh
```