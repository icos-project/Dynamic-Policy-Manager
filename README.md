# Dynamic Policy Manager
The Dynamic Policies Manager component is responsible for the management of the policies related
to technical and business performance associated with each application and the detection and prediction
of violations of such policies in the running application.
In the 1st release of the Dynamic Policy Manager starts to define and send the policy configured to the Monitoring and
Logging component. The DPM creates and sends the policy information to the Monitoring and
Telemetry component. The monitoring component sends an alert and the values of the violation -if
needed- to the Policy Evaluator. The Policy Evaluator sends the alert violation to the Policy Violation
Manager.The Policy Violation Manager stores and analyses the violation and if the remediation action is provided
by itself; it then sends the remediation action to the Job Manager otherwise the Policy Violation Manager
sends a request of the suggested action to the intelligence block.

## Development
An [API](api.md) REST is implemetend for the [use](usage.md) of the Dynamic Policy Manager.

### Requirements

Dynamic Policy Manager is developes in [python3.11](https://www.python.org/downloads/release/python-3110/).
It's possible to run it in different way:
- docker file -> to verify that in your machine is installed a [Docker](https://docs.docker.com/engine/install/) Engine
- helm chart  -> to verify that in your machine is installaed [Heml](https://helm.sh/docs/)
- manual -> to verify python3.11 is installed.

After that you can follows the next steps.

### How to deploy

Before to run the application in development mode, it is suggested to create a [virtual environment](https://docs.python.org/3.11/library/venv.html) and 
install the packages in ```[requirements.txt](requirements.txt)```

Run a local instance without authn and authz and using a default sqlite db

```bash
cd src
python -m polman.cli.main --db-url sqlite:///./dpm.db --verbosity 3 --authn-skip true --authz-skip true
```

The parameters can be passed also through env variables

E.g.:

```bash
DPLM_DB_TYPE=mysql
DPLM_DB_HOST=localhost
DPLM_DB_USER=root
DPLM_DB_PASSWORD=root
DPLM_DB_PORT=3306
DPLM_DB_NAME=dpm

DPLM_AUTHN_CLIENT_SECRET=xxxx
DPLM_AUTHN_CLIENT_ID=shell-backend
DPLM_AUTHN_SERVER=https://keycloak.dev.icos.91.109.56.214.sslip.io/
DPLM_AUTHN_REALM=icos-dev
DPLM_AUTHZ_SKIP=true
DPLM_API_PORT=8000
DPLM_VERBOSITY=3
```

# Legal
The Dynamic Policy Manager is released under the [Apache License version 2.0](LICENSE).
Copyright 2022-2024 Gabriele Giammatteo , Engineering Ingegneria Informatica S.p.A., All rights reserved.

This work has received funding from the European Union's HORIZON research and innovation programme under grant agreement No. 101070177.
