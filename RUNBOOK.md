On-call reference for the BrightCart local compose stack

## If Inventory-api won't restart, check if Inventory-db is healthy or unhealthy
`docker compose ps`

## Inventory-db is unhealthy
A: check "healthcheck" script itself
- username/password/port conflict
- start period is set up too short
- interval/retries/timeout unreasonable

B: db starting stage problems, volumes issues
- bind volume, permission denied
    ./db-data with owner:root, but the /var/lib/postgresql/data with owner: postgres
- ./init.sql fail, db container Exited

C: db missing environment variables

D: resource issues
     - not enough memory, OOM Killer/ full disk, can't write logs

E: no graceful shutdown cause db file crashed, stuck at recovery/crash recovery stage

## Inventory-db is healthy, check inventory-api logs
A: db configuration in api container is wrong
- db host name
- if correct mapping with .env, orders_api.py.db_config{}
- ports

B: SQL issues
- logic wrongly, missing/wrong table, api cannot find value
- skip /docker-entry-initdb.d, but./init.sql is changed
- db migration issue
- db_max_connections
- db become unhealthy after api just starts

C: api itself issue
- dependency etc
- ports conflict

`docker compose down -v`
`docker compose up -d --build`
`docker compose ps`
`docker compose logs -t inventory-db`
`docker inspect db_inventory --format='{{json.State.Health}}' | jq`
`docker compose exec db`
`docker compose logs -t inventory-api`




