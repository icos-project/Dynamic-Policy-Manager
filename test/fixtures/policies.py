# ICOS Dynamic Policy Manager
# Copyright © 2022-2024 Engineering Ingegneria Informatica S.p.A.
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

import pytest

from polman.common.model import Policy, PolicyCreate
from polman.watcher.model import AlertmanagerAlert
from test.common.policy_factories import PolicyFactory
from test.utils import build
from test.data import policy_host_cpu_144

@pytest.fixture(scope="session")
def test_policy_factory():
  return PolicyFactory


policy1_id = 'c0621b34-d7bc-4891-89a0-fa297c9d4d38'
policy_2_id = "fd745e25-0ca3-418b-b310-257693e3f3bf"

@pytest.fixture(scope='function')
def policy1(policy_create_1):
  return Policy(**policy_create_1.model_dump(), id=policy1_id)
  

@pytest.fixture(scope='function')
def policy_create_1(policy_c1):
  return build(PolicyCreate, policy_c1)

@pytest.fixture(scope='function')
def policy_c1():
  return {
      "name": "cpu_usage-for-agent",
      "subject": {
        "hostId": "*",
        "agentId": "icos-agent-1"
      },
      "spec": {
        "expr": "avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode=\"idle\", {{subject_label_selector}}}[2m]))",
        "violatedIf": "> {{maxCpu}}"
      },
      "variables": {
        "maxCpu": "0.8"
      },
      "action": {
        "url": "https://localhost:3246/",
        "httpMethod": "POST"
      }
    }


@pytest.fixture(scope='session')
def policy_2_create():
  return build(PolicyCreate, {
    "name": "compss-low-performance-20",
    "subject": {
        "appName": "compss-example-app",
        "appComponent": "component1",
        "appInstance": "compss-example-app-002"
    },
    "spec": {
        "expr": "sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_avgTime_ratio{CoreSignature=\"{{ compssTask }}\", icos_app_name=\"{{subject.appName}}\", icos_app_instance=\"{{subject.appInstance}}\", icos_app_component=\"{{subject.appComponent}}\"} * compss_pendTasks_ratio{CoreSignature=\"{{ compssTask }}\", icos_app_name=\"{{subject.appName}}\", icos_app_instance=\"{{subject.appInstance}}\", icos_app_component=\"{{subject.appComponent}}\"}) / sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_node_info{property=\"computing_units\", icos_app_name=\"{{subject.appName}}\", icos_app_instance=\"{{subject.appInstance}}\", icos_app_component=\"{{subject.appComponent}}\"})",
        "violatedIf": "> {{thresholdTimeSeconds}}",
        "thresholds": {
            "warning": 200,
            "critical": 500
        }
    },
    "variables": {
        "compssTask": "provesOtel.example_task",
        "thresholdTimeSeconds": "120"
    },
    "properties": {
        "pendingInterval": "30s"
    },
    "action": {
        "url": "http://example.com/webhook",
        "httpMethod": "POST",
        "extraParams": {"remediation": "scale-up"}
    }
})


@pytest.fixture(scope='session')
def policy_3_create():
  return build(PolicyCreate, {
    "name": "cpu_utilization_on_hosts",
    "subject": {
        "appName": "compss-example-app",
        "appComponent": "component1",
        "appInstance": "compss-example-app-002"
    },
    "spec": {
        "expr": "tlum_workload_info{ {{subject_label_selector}} } *on(icos_host_id) group_left avg without (cpu) (1 - rate(node_cpu_seconds_total{mode=\"idle\"}[2m]))",
        "violatedIf": "> {{maxCpu}}",
        "thresholds": {
            "warning": 0.6,
            "critical": 0.8
        }
    },
    "variables": {
        "maxCpu": "0.8"
    },
    "action": {
        "url": "https://0e77-94-33-209-155.ngrok-free.app",
        "httpMethod": "POST"
    }
})

  
@pytest.fixture(scope='function')
def policy_2_db(policy_2_create):
  return Policy(**policy_2_create.model_dump(), id=policy_2_id)

@pytest.fixture(scope='session')
def policy_2_alerts():
  return {
    "version": "4",
    "groupKey": "{}:{}",
    "truncatedAlerts": 0,
    "status": "firing",
    "receiver": "dpm-webhook",
    "groupLabels": {},
    "commonLabels": {
        "alertname": "compss-low-performance-20:rule-0",
        "icos_app_component": "component1",
        "icos_app_instance": "compss-example-app-002",
        "icos_app_name": "compss-example-app"
    },
    "commonAnnotations": {
        "plm_expr_value": "235.365",
        "plm_id": policy_2_id,
        "plm_measurement_backend": "prom-1"
    },
    "externalURL": "http://contrl1-telemetry-controller-alertmanager-78ddf98bbd-92ccc:9093",
    "alerts": [
        {
            "status": "firing",
            "labels": {
                "alertname": "compss-low-performance-20:rule-0",
                "icos_app_component": "component1",
                "icos_app_instance": "compss-example-app-002",
                "icos_app_name": "compss-example-app"
            },
            "annotations": {
                "plm_expr_value": "235.365",
                "plm_id": policy_2_id,
                "plm_measurement_backend": "prom-1"
            },
            "startsAt": "2024-03-05T16:19:11.736263Z",
            "endsAt": "0001-01-01T00:00:00Z",
            "generatorURL": "http://contrl1-thanos-query.icos-system.svc.cluster.local:9090/graph?g0.expr=sum+by+%28icos_app_component%2C+icos_app_instance%2C+icos_app_name%29+%28compss_avgTime_ratio%7BCoreSignature%3D%22provesOtel.example_task%22%2Cicos_app_component%3D%22component1%22%2Cicos_app_instance%3D%22compss-example-app-002%22%2Cicos_app_name%3D%22compss-example-app%22%7D+%2A+compss_pendTasks_ratio%7BCoreSignature%3D%22provesOtel.example_task%22%2Cicos_app_component%3D%22component1%22%2Cicos_app_instance%3D%22compss-example-app-002%22%2Cicos_app_name%3D%22compss-example-app%22%7D%29+%2F+sum+by+%28icos_app_component%2C+icos_app_instance%2C+icos_app_name%29+%28compss_node_info%7Bicos_app_component%3D%22component1%22%2Cicos_app_instance%3D%22compss-example-app-002%22%2Cicos_app_name%3D%22compss-example-app%22%2Cproperty%3D%22computing_units%22%7D%29+%2F+1000+%3E+120&g0.tab=1",
            "fingerprint": "f84ab44ff4933354"
        }
    ]
}
  

@pytest.fixture(scope='session')
def policy_c1_alert():
  return build(AlertmanagerAlert, {
            "status": "firing",
            "labels": {
                "alertname": "cpu_usage-for-agent:rule-0",
                "http_scheme": "http",
                "icos_agent_id": "icos-agent-1",
                "icos_alpha_latitude": "41.390205",
                "icos_alpha_longitude": "2.154007",
                "icos_container_name": "node-exporter",
                "icos_controller_id": "staging-a",
                "icos_host_id": "57e17cac94714bf6976f1e071d64d586",
                "icos_host_name": "93111014-6276-4c1f-83eb-a5f7aa8386c9:icosedge",
                "instance": "10.150.0.144:9100",
                "job": "icos-annotated-services",
                "k8s_cluster_uid": "93111014-6276-4c1f-83eb-a5f7aa8386c9",
                "k8s_container_name": "node-exporter",
                "k8s_daemonset_name": "telagent-prometheus-node-exporter",
                "k8s_namespace_name": "icos-system",
                "k8s_node_name": "icosedge",
                "k8s_pod_name": "telagent-prometheus-node-exporter-jbd9v",
                "k8s_pod_start_time": "2024-02-04T18:38:08Z",
                "k8s_pod_uid": "b5ea978f-ee4a-44b2-8511-5a38808fbaa4",
                "net_host_name": "10.150.0.144",
                "net_host_port": "9100",
                "receive": "true",
                "service_instance_id": "10.150.0.144:9100",
                "service_name": "icos-annotated-services",
                "tenant_id": "default-tenant"
            },
            "annotations": {
                "plm_expr_value": "1",
                "plm_id": policy1_id,
                "plm_measurement_backend": "prom-1"
            },
            "startsAt": "2024-02-14T09:39:39.775655Z",
            "endsAt": "0001-01-01T00:00:00Z",
            "generatorURL": "http://contrl1-thanos-query.icos-system.svc.cluster.local:9090/graph?g0.expr=avg+without+%28mode%2C+cpu%29+%281+-+rate%28node_cpu_seconds_total%7Bicos_agent_id%3D%22icos-agent-1%22%2Cicos_host_id%3D~%22.%2B%22%2Cmode%3D%22idle%22%7D%5B2m%5D%29%29+%3E+0.8&g0.tab=1",
            "fingerprint": "659b7c60752cae70"
        })

@pytest.fixture
def policy_cpu144_dict():
  return policy_host_cpu_144.policy
        
@pytest.fixture
def policy_cpu144_alerts_dict():
  def __get_alerts_with_policy_id(policy_id):
    d = dict.copy(policy_host_cpu_144.policy_alert)
    d['alerts'][0]['annotations']['plm_id'] = policy_id
    return d
  return __get_alerts_with_policy_id

@pytest.fixture
def policy_cpu144_resolve_dict():
  def __get_resolve_with_policy_id(policy_id):
    d = dict.copy(policy_host_cpu_144.policy_resolve)
    d['alerts'][0]['annotations']['plm_id'] = policy_id
    return d
  return __get_resolve_with_policy_id
   