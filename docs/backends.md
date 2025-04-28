# Backends

Currently DPM supports the following backends:

- InMemory
- File
- MongoDB


## InMemory

Keeps policies in memory. It is the default if nothing is specified in the configuration, but it is reccomended only for testing and development.

## File

Keeps policies in a file in json format. Not intended for production.

```bash
--db-type file
--db-url /path/to/my_db.json
```

The file should exists before Polman is started and must have a vaild json content.

```bash
echo "[]" > my_db.json
```

## MongoDB

The default backend.

```bash
--db-type mongodb
--db-url ""
--db-name polman
--db-password ""
--db-user ""
--db-port 27017
--db-host localhost
```

If `--db-url` is specified, the host, port, user and password parameters are ignored.