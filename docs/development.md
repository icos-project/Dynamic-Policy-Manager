# Development 


Dynamic Policy Manager (DPM - a.k.a. Polman) is based on Python 3.11. To start development, clone the repository and install the needed libraries:

```bash
$ git clone https://production.eng.it/gitlab/icos/meta-kernel/dynamic-policy-manager.git
$ pip install -r requirements.txt
$ export PYTHONPATH=src
```

Dynamic Policy Manager has a command line tool to start and configure the service. To start an instance of Polman with a minimal configuration, run:

```bash
$ python -m polman.cli.main --authn-skip --authz-skip app
```

This will start an instance using a basic in-memory database and without authentication/authorization (both not reccomended for real use). In addition this instance will not be able to contact Prometheus to set rules (options `--prometheus-rules-api-url`). So only creation of inactive policies will suceeed (using the `do_not_activate=true` query string option).

APIs can be tested using Swagger at: <http://127.0.0.1:8000/polman/docs>

A more sane configuration would be:

```bash
$ python -m polman.cli.main --verbosity 3 --db-type mongodb --authn-skip --authz-skip --prometheus-rules-api-url http://localhost:5000/api/v1/rules app
```

In this case it will use a localhost mongodb server (without authentication) and will contact the Prometheus Rules API at the specified URL.

A list of all supported configuration options can be obtained with the `--help` flag.

```bash
$ python -m polman.cli.main --help

Usage: python -m polman.cli.main [OPTIONS] COMMAND [ARGS]...

Options:
  --icos-job-manager-base-url TEXT
  --prometheus-rules-api-url TEXT
  --api-enable-admin-api / --no-api-enable-admin-api
                                  [default: no-api-enable-admin-api]
  --api-allowed-cors-origins TEXT
  --api-root TEXT                 [default: /polman]
  --api-port INTEGER              [default: 8000]
  --api-host TEXT                 [default: 127.0.0.1]
  --authz-skip / --no-authz-skip  [default: no-authz-skip]
  --authn-verify-audience / --no-authn-verify-audience
                                  [default: no-authn-verify-audience]
  --authn-client-secret TEXT
  --authn-client-id TEXT
  --authn-realm TEXT              [default: icos]
  --authn-server TEXT             [default: https://localhost/]
  --authn-skip / --no-authn-skip  [default: no-authn-skip]
  --db-url TEXT
  --db-name TEXT
  --db-password TEXT
  --db-user TEXT
  --db-port INTEGER               [default: 0]
  --db-host TEXT
  --db-type TEXT                  [default: inmemory]
  --rich-output / --no-rich-output
                                  [default: no-rich-output]
  --verbosity INTEGER             [default: 2]
  --quiet / --no-quiet            [default: no-quiet]
  --help                          Show this message and exit.

Commands:
  app
  print-config

```

**Environment Variables**: all  options can be defined also through environment variables with the prefix `PLM_` and the name of the option in uppercase with `_` instead of `-`. For instance:

- `--authn-skip` -> `PLM_AUTHN_SKIP`
- `--verbosity`  -> `PLM_VERBOSITY`
- `--prometheus-rules-api-url` -> `PLM_PROMETHEUS_RULES_BASE_URL`


## Docker Compose

A convenient way to have a portable development environment is to use `docker compose`. An example can be found at [Deployment - Docker Compose](deployment.md#docker-compose)

## Devenv

In order to have a predicatble and reproducible development environment, DPM is being developed using <https://devenv.sh>. In the source code repository there are `devenv.nix` and `devenv.yaml` files that declare the environment.

To enter a development shell, just run:
```bash
$ devenv shell
```

To start a service of services that makes easier to develop and test DPM, run:
```bash
$ devenv up
```

The services started are:

- mongodb server
- prometheus server
- proometheus-api server
- echo-server (used to show notification sent)
- a data generator to generate metrics in prometheus
- a Keycloak instance