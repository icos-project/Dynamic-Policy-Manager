# Deployment


## Docker Compose

Dynamic Policy Manager (DPM a.k.a. Polman) and all required services can be easily deployed using docker compose. A good starting configuration can be the following:

- A `docker-compose.yml` file

```yaml title="docker-compose.yml"
 "examples/dev-docker-compose/docker-compose.yml"
```

- A `prometheus.yml` file

```yaml title="prometheus.yml"
  "examples/dev-docker-compose/prometheus.yml"

```

## Helm Chart

This chart deploys the ICOS Dynamic Policy Manager module.
It includes the following components:

Resengit: for the image to build (docker, helm)
mongodb: to manage the data stored


