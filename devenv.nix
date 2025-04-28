#
# ICOS Dynamic Policy Manager
# Copyright © 2022 - 2025 Engineering Ingegneria Informatica S.p.A.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# This work has received funding from the European Union's HORIZON research
# and innovation programme under grant agreement No. 101070177.
#

{ inputs, pkgs, config, ... }:
let
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };

  rulesDir        = config.env.DEVENV_STATE + "/rules";
  prometheusDir   = config.env.DEVENV_STATE + "/prometheus";
  keycloakDir     = config.env.DEVENV_STATE + "/keycloak";
  alertManagerDir = config.env.DEVENV_STATE + "/alertmanager";

  # hack to make the container prometheus-api running with rootlesskit to
  # see prometheus executed on the host as process.
  # see: https://stackoverflow.com/questions/72500740/how-to-access-localhost-on-rootless-docker
  # from docker v26 it should be possible to use the DOCKERD_ROOTLESS_ROOTLESSKIT_DISABLE_HOST_LOOPBACK
  ip = "192.168.2.82";

  alertManagerConfig = pkgs.writeText "alertManagerConfig" ''
    receivers:
        - name: dpm-webhook
          webhook_configs:
          - url: "http://localhost:8000/polman/watcher/api/v1/webhooks/alertmanager"
            send_resolved: true
    route:
      receiver: dpm-webhook
      group_wait: 60s
  
  '';

  # see https://github.com/little-angry-clouds/prometheus-data-generator
  prometheusDataGeneratorConfig = pkgs.writeText "dataGeneratorConfig" ''
    config:
      - name: node_cpu_seconds_total
        description: "node export cpu metric"
        labels: [cpu, mode, icos_controller_id, icos_agent_id, icos_host_id, icos_host_name]
        type: counter
        sequence:
          - eval_time: 600
            interval: 1
            value: 1
            labels:
              cpu: 0
              mode: idle
              icos_controller_id: icos-controller-1
              icos_agent_id: icos-agent-1
              icos_host_id: 57e17cac94714bf6976f1e071d64d586
              icos_host_name: "93111014:icosedge"
          - eval_time: 400
            interval: 1
            value: 0.2
            labels:
              cpu: 0
              mode: idle
              icos_controller_id: icos-controller-1
              icos_agent_id: icos-agent-1
              icos_host_id: 57e17cac94714bf6976f1e071d64d586
              icos_host_name: "93111014:icosedge"

      - name: container_cpu_utilization_ratio
        description: "Container cpu metric"
        labels: [icos_agent_id, icos_app_component, icos_app_instance, icos_app_name, icos_controller_id, k8s_container_name, k8s_pod_name, k8s_namespace_name, k8s_node_name, k8s_pod_uid]
        type: gauge
        sequence:
          - eval_time: 600
            interval: 1
            values: 0.2 - 0.4
            operation: set
            labels:
              icos_agent_id: ocm-staging-2
              icos_app_component: backend
              icos_app_instance: 9997ccb4-3dd9-4f5c-aac9-d69160c373c6
              icos_app_name: fake-gabriele-app
              icos_controller_id: staging-a
              k8s_container_name: app-container-1
              k8s_pod_name: fake-app-demo-6dd587fb59-25j8b
              k8s_namespace_name: gabriele-test
              k8s_node_name: node1
              k8s_pod_uid: 39d20a54-fc4c-485d-8e0d-595aba19d1ce
          - eval_time: 400
            interval: 1
            values: 0.7-1
            operation: set
            labels:
              icos_agent_id: ocm-staging-2
              icos_app_component: backend
              icos_app_instance: 9997ccb4-3dd9-4f5c-aac9-d69160c373c6
              icos_app_name: fake-gabriele-app
              icos_controller_id: staging-a
              k8s_container_name: app-container-1
              k8s_pod_name: fake-app-demo-6dd587fb59-25j8b
              k8s_namespace_name: gabriele-test
              k8s_node_name: node1
              k8s_pod_uid: 39d20a54-fc4c-485d-8e0d-595aba19d1ce

      - name: SCA_score
        description: "Wazuh security level"
        labels: [agent_hostname, agent_ip, agent_name, agent_uname, icos_agent_id, icos_controller_id, k8s_node_name, k8s_pod_name]
        type: gauge
        sequence:
          - eval_time: 600
            interval: 1
            value: 80
            operation: set
            labels:
              agent_hostname: nuvla-edge-ne
              agent_ip: 10.171.1.16
              agent_name: matteo
              agent_uname: "Darwin |miceli-wf-mac.dipinfo.di.unito.it |24.3.0 |Darwin Kernel Version 24.3.0: Thu Jan 2 20:24:22 PST 2025; root:xnu-11215.81.4~3/RELEASE_ARM64_T6041 |arm64"
              icos_agent_id: self
              icos_controller_id: staging-a
              k8s_node_name: node1
              k8s_pod_name: contrl1-security-coordination-module-778cc64c94-mhqlp
          - eval_time: 600
            interval: 1
            value: 42
            operation: set
            labels:
              agent_hostname: nuvla-edge-ne
              agent_ip: 10.171.1.16
              agent_name: matteo
              agent_uname: "Darwin |miceli-wf-mac.dipinfo.di.unito.it |24.3.0 |Darwin Kernel Version 24.3.0: Thu Jan 2 20:24:22 PST 2025; root:xnu-11215.81.4~3/RELEASE_ARM64_T6041 |arm64"
              icos_agent_id: self
              icos_controller_id: staging-a
              k8s_node_name: node1
              k8s_pod_name: contrl1-security-coordination-module-778cc64c94-mhqlp


      - name: tlum_host_info
        description: "Telemetruum Host Info"
        labels: [arch, host_name, hostname, icos_agent_id, icos_cluster_id, icos_controller_id, icos_host_id, icos_host_name, ip, latitude, longitude, os]
        type: gauge
        sequence:
          - eval_time: 600
            interval: 1
            value: 1
            operation: set
            labels:
              arch: amd64
              host_name: nuvla-edge-ne
              hostname: nuvla-edge-ne
              icos_agent_id: staging-nuvla-1
              icos_cluster_id: 3xhoe4v4j79caxzgnm8jl40e1
              icos_controller_id: staging-a
              icos_host_id: 28a338253f31430897e32c5a3bb33c3f
              icos_host_name: 28a33825:nuvla-edge-ne
              ip: 10.171.1.16
              latitude: 37.9842
              longitude: 23.7353
              os: linux

      - name: tlum_workload_info
        description: "Telemetruum Workload Info"
        labels: [icos_agent_id, icos_app_component, icos_app_instance, icos_app_managed_by, icos_app_name, icos_cluster_id, icos_controller_id, icos_host_id, icos_host_name, icos_label_use_case, id, name]
        type: gauge
        sequence:
          - eval_time: 600
            interval: 1
            value: 1
            operation: set
            labels:
              icos_agent_id: staging-ocm-1
              icos_app_component: compss-app
              icos_app_instance: demo-app-999
              icos_app_managed_by: jobmanager
              icos_app_name: compss-demo-1
              icos_cluster_id: 08c66cd5-ae67-4336-99c8-9016cb2b5546
              icos_controller_id: staging-a
              icos_host_id: 28a338253f31430897e32c5a3bb33c3f
              icos_host_name: 28a33825:nuvla-edge-ne
              icos_label_use_case: uc4
              id: 2104db48-e612-4b55-8bbd-76b4319521f2
              name: helloworldclusterlink-1743582709698__curl-665b88987-h89vn
  '';
  
  prometheusConfig  = pkgs.writeText "config" ''
    global:
      scrape_interval:     15s
      evaluation_interval: 15s

    alerting:
      alertmanagers:
        - static_configs:
          - targets:
            - localhost:9093
          scheme: http
          path_prefix: ""
          timeout: 10s
          api_version: v2

    rule_files:
      - "${rulesDir}/*yml"

    scrape_configs:
      - job_name: "fake-data-generator"
        metrics_path: /metrics/
        scrape_interval: 10s
        static_configs:
          - targets: ["localhost:9000"]
      - job_name: "polman-metrics"
        metrics_path: /metrics/
        scrape_interval: 10s
        static_configs:
          - targets: ["localhost:9464"]
  '';
in
{
  env.PYTHONPATH = "src";

  packages = [ pkgs.prometheus pkgs.prometheus-alertmanager pkgs-unstable.ruff ];

  languages.python.enable = true;
  languages.python.version = "3.11.3";
  languages.python.venv.enable = true;
  languages.python.venv.requirements = ./requirements.txt;

  services.mongodb.enable = true;
  services.mongodb.initDatabaseUsername = "admin";
  services.mongodb.initDatabasePassword = "admin";

  processes.prometheus.exec = "prometheus --config.file=${prometheusConfig} --storage.tsdb.path=${prometheusDir} --web.enable-lifecycle --web.enable-admin-api";



  processes.alertmanager.exec = "alertmanager --config.file=${alertManagerConfig} --storage.path=${alertManagerDir}";


  processes.prometheus-api.exec = ''
    docker run --rm --name prometheus-api -v "${rulesDir}:/app/rules" -p "5000:5000" hayk96/prometheus-api:v0.4.2 --prom.addr=http://${ip}:9090 --rule.path=/app/rules --web.enable-ui=true
  '';
  process-managers.process-compose.settings.processes.prometheus-api.shutdown.command = "docker stop prometheus-api";

  processes.data-generator.exec = ''
    docker run --rm --name data-generator -v "${prometheusDataGeneratorConfig}:/config.yml" -e "PDG_CONFIG=/config.yml" -p "9000:9000" littleangryclouds/prometheus-data-generator:0.2
  '';
  process-managers.process-compose.settings.processes.data-generator.shutdown.command = "docker stop data-generator";
  
  processes.keycloak.exec = ''
    docker run --rm --name keycloak -v "${keycloakDir}:/opt/keycloak/data" -p "8080:8080" -e "KEYCLOAK_ADMIN=admin" -e "KEYCLOAK_ADMIN_PASSWORD=admin" quay.io/keycloak/keycloak:25.0.4 start-dev
  '';
  process-managers.process-compose.settings.processes.keycloak.shutdown.command = "docker stop keycloak";


  processes.echo-server.exec = ''
    docker run --rm --name echo-server -e HTTP_PORT=8888 -p 3456:8888 mendhak/http-https-echo:34
  '';

  process-managers.process-compose.settings.processes.echo-server.shutdown.command = "docker stop echo-server";

  scripts.clean-policies.exec = "rm -rf ${config.env.DEVENV_STATE}/mongodb";
  scripts.clean-prometheus.exec = "rm -rf ${rulesDir} ${alertManagerDir} ${prometheusDir}";

  scripts.update-openapi-schema.exec = "python -m polman.cli.main dump-openapi --output docs/openapi.json";

  scripts.start-polman-dev.exec = "python -m polman.cli.main --verbosity 3 --db-type mongodb --authn-skip --authz-skip --api-enable-debug-calls --prometheus-rules-api-url http://localhost:5000/api/v1/rules --icos-job-manager-base-url http://localhost:3456 app";

  scripts.start-polman-dev-auth.exec = "python -m polman.cli.main --verbosity 3 --db-type mongodb --prometheus-rules-api-url http://localhost:5000/api/v1/rules --authn-server http://localhost:8080/ --authn-realm local-dev --authn-client-id polman --authn-client-secret $(dotenv -f .env.local get authn_client_secret | tr -d '\n') --icos-job-manager-base-url http://localhost:3456 app";
}
