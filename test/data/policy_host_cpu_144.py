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

policy = {
        "name": "cpu_usage-for-agent",
        "subject": {
            "type": "host",
            "hostId": "57e17cac94714bf6976f1e071d64d586",
            "agentId": "icos-agent-1"
        },
        "spec": {
            "description": "",
            "type": "telemetryQuery",
            "expr": "avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode=\"idle\", icos_agent_id=\"icos-agent-1\", icos_host_id=\"57e17cac94714bf6976f1e071d64d586\"}[2m])) > 0.5",
            "violatedIf": None,
            "thresholds": None
        },
        "action": {
            "type": "webhook",
            "url": "https://localhost:3246/",
            "httpMethod": "POST",
            "extraParams": {},
            "includeAccessToken": False
        },
        "variables": {
            "maxCpu": "0.5"
        },
        "properties": {}
    }

policy_alert = {
    "version": "4",
    "groupKey": "{}:{}",
    "truncatedAlerts": 0,
    "status": "firing",
    "receiver": "dpm-webhook",
    "groupLabels": {},
    "commonLabels": {
        "alertname": "cpu_usage-for-agent:rule-0",
        "http_scheme": "http",
        "icos_agent_id": "icos-agent-1",
        "icos_controller_id": "staging-a",
        "icos_host_id": "57e17cac94714bf6976f1e071d64d586",
        "icos_host_name": "93111014:icosedge",
        "instance": "10.150.0.144:9100",
        "job": "icos-annotated-services",
        "k8s_cluster_uid": "93111014-6276-4c1f-83eb-a5f7aa8386c9",
        "k8s_container_name": "node-exporter",
        "k8s_daemonset_name": "telagent-prometheus-node-exporter",
        "k8s_namespace_name": "icos-system",
        "k8s_node_name": "icosedge",
        "k8s_pod_name": "telagent-prometheus-node-exporter-5rgk7",
        "k8s_pod_uid": "f35c5ff2-b5a3-4abd-93fe-b4947a5acd6a",
        "net_host_name": "10.150.0.144",
        "net_host_port": "9100",
        "receive": "true",
        "service_instance_id": "10.150.0.144:9100",
        "service_name": "icos-annotated-services",
        "tenant_id": "default-tenant"
    },
    "commonAnnotations": {
        "plm_expr_value": "0.8213749999956539",
        "plm_id": "65f5a3ced6ea3f831414a387",
        "plm_measurement_backend": "prom-1"
    },
    "externalURL": "http://contrl1-telemetry-controller-alertmanager-78ddf98bbd-b9wnf:9093",
    "alerts": [
        {
            "status": "firing",
            "labels": {
                "alertname": "cpu_usage-for-agent:rule-0",
                "http_scheme": "http",
                "icos_agent_id": "icos-agent-1",
                "icos_controller_id": "staging-a",
                "icos_host_id": "57e17cac94714bf6976f1e071d64d586",
                "icos_host_name": "93111014:icosedge",
                "instance": "10.150.0.144:9100",
                "job": "icos-annotated-services",
                "k8s_cluster_uid": "93111014-6276-4c1f-83eb-a5f7aa8386c9",
                "k8s_container_name": "node-exporter",
                "k8s_daemonset_name": "telagent-prometheus-node-exporter",
                "k8s_namespace_name": "icos-system",
                "k8s_node_name": "icosedge",
                "k8s_pod_name": "telagent-prometheus-node-exporter-5rgk7",
                "k8s_pod_uid": "f35c5ff2-b5a3-4abd-93fe-b4947a5acd6a",
                "net_host_name": "10.150.0.144",
                "net_host_port": "9100",
                "receive": "true",
                "service_instance_id": "10.150.0.144:9100",
                "service_name": "icos-annotated-services",
                "tenant_id": "default-tenant"
            },
            "annotations": {
                "plm_expr_value": "0.8213749999956539",
                "plm_id": "65f5a3ced6ea3f831414a387",
                "plm_measurement_backend": "prom-1"
            },
            "startsAt": "2024-03-16T14:13:41.959135Z",
            "endsAt": "0001-01-01T00:00:00Z",
            "generatorURL": "http://contrl1-thanos-query.icos-system.svc.cluster.local:9090/graph?g0.expr=avg+without+%28mode%2C+cpu%29+%281+-+rate%28node_cpu_seconds_total%7Bicos_agent_id%3D%22icos-agent-1%22%2Cicos_host_id%3D%2257e17cac94714bf6976f1e071d64d586%22%2Cmode%3D%22idle%22%7D%5B2m%5D%29%29+%3E+0.5&g0.tab=1",
            "fingerprint": "c04fd2082a9b94e9"
        }
    ]
}

policy_resolve = {
    "version": "4",
    "groupKey": "{}:{}",
    "truncatedAlerts": 0,
    "status": "resolved",
    "receiver": "dpm-webhook",
    "groupLabels": {},
    "commonLabels": {
        "alertname": "cpu_usage-for-agent:rule-0",
        "http_scheme": "http",
        "icos_agent_id": "icos-agent-1",
        "icos_controller_id": "staging-a",
        "icos_host_id": "57e17cac94714bf6976f1e071d64d586",
        "icos_host_name": "93111014:icosedge",
        "instance": "10.150.0.144:9100",
        "job": "icos-annotated-services",
        "k8s_cluster_uid": "93111014-6276-4c1f-83eb-a5f7aa8386c9",
        "k8s_container_name": "node-exporter",
        "k8s_daemonset_name": "telagent-prometheus-node-exporter",
        "k8s_namespace_name": "icos-system",
        "k8s_node_name": "icosedge",
        "k8s_pod_name": "telagent-prometheus-node-exporter-5rgk7",
        "k8s_pod_uid": "f35c5ff2-b5a3-4abd-93fe-b4947a5acd6a",
        "net_host_name": "10.150.0.144",
        "net_host_port": "9100",
        "receive": "true",
        "service_instance_id": "10.150.0.144:9100",
        "service_name": "icos-annotated-services",
        "tenant_id": "default-tenant"
    },
    "commonAnnotations": {
        "plm_expr_value": "0.8767499999996895",
        "plm_id": "65f5a3ced6ea3f831414a387",
        "plm_measurement_backend": "prom-1"
    },
    "externalURL": "http://contrl1-telemetry-controller-alertmanager-78ddf98bbd-b9wnf:9093",
    "alerts": [
        {
            "status": "resolved",
            "labels": {
                "alertname": "cpu_usage-for-agent:rule-0",
                "http_scheme": "http",
                "icos_agent_id": "icos-agent-1",
                "icos_controller_id": "staging-a",
                "icos_host_id": "57e17cac94714bf6976f1e071d64d586",
                "icos_host_name": "93111014:icosedge",
                "instance": "10.150.0.144:9100",
                "job": "icos-annotated-services",
                "k8s_cluster_uid": "93111014-6276-4c1f-83eb-a5f7aa8386c9",
                "k8s_container_name": "node-exporter",
                "k8s_daemonset_name": "telagent-prometheus-node-exporter",
                "k8s_namespace_name": "icos-system",
                "k8s_node_name": "icosedge",
                "k8s_pod_name": "telagent-prometheus-node-exporter-5rgk7",
                "k8s_pod_uid": "f35c5ff2-b5a3-4abd-93fe-b4947a5acd6a",
                "net_host_name": "10.150.0.144",
                "net_host_port": "9100",
                "receive": "true",
                "service_instance_id": "10.150.0.144:9100",
                "service_name": "icos-annotated-services",
                "tenant_id": "default-tenant"
            },
            "annotations": {
                "plm_expr_value": "0.8767499999996895",
                "plm_id": "65f5a3ced6ea3f831414a387",
                "plm_measurement_backend": "prom-1"
            },
            "startsAt": "2024-03-16T14:13:41.959135Z",
            "endsAt": "2024-03-16T14:15:41.959135Z",
            "generatorURL": "http://contrl1-thanos-query.icos-system.svc.cluster.local:9090/graph?g0.expr=avg+without+%28mode%2C+cpu%29+%281+-+rate%28node_cpu_seconds_total%7Bicos_agent_id%3D%22icos-agent-1%22%2Cicos_host_id%3D%2257e17cac94714bf6976f1e071d64d586%22%2Cmode%3D%22idle%22%7D%5B2m%5D%29%29+%3E+0.5&g0.tab=1",
            "fingerprint": "c04fd2082a9b94e9"
        }
    ]
}