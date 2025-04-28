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

### Development and testing

Please read the `./docs/development.md` file.

# Legal
The Dynamic Policy Manager is released under the [Apache License version 2.0](LICENSE).
Copyright 2022 - 2025 Engineering Ingegneria Informatica S.p.A., All rights reserved.

This work has received funding from the European Union's HORIZON research and innovation programme under grant agreement No. 101070177.

