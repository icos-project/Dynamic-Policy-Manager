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

import json
import logging
from http import HTTPMethod

from pydantic import TypeAdapter
import yaml

from polman.common.model import PolicyActionWebhook
from polman.registry.icos.models import ICOSAppDescriptor, ICOSPolmanTemplatePolicy
from polman.registry.icos.process_app_descriptor import process_app_descriptor
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine
from test.utils import get_storage_from_http_client


def test_post_icos_app_descriptor_compss_2(test_http_client_mongo, app_deployed_request_compss_2_json):
    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/",
        json=json.loads(app_deployed_request_compss_2_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_post_icos_app_descriptor_compss_1(test_http_client_mongo, app_deployed_request_compss_1_json):
    print(app_deployed_request_compss_1_json)
    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/",
        json=json.loads(app_deployed_request_compss_1_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    # p = test_mongo_storage.list()[0]

    # assert p.name == 'mjpeg-ffmpeg-app-demo-app-002-policy-0'

def test_post_icos_unknown_bad_action(test_http_client, app_deployed_request_1_json):
    new_app_deployment = app_deployed_request_1_json.replace("job-manager", "not-existing-service")

    response = test_http_client.post("/polman/registry/api/v1/icos/", json=json.loads(new_app_deployment))
    assert response.status_code == 500
    assert response.json()["detail"] == "Unknown service name in action: 'not-existing-service'"


def test_post_icos(test_http_client, app_deployed_request_1_json, mocker):
    mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")

    response = test_http_client.post("/polman/registry/api/v1/icos/", json=json.loads(app_deployed_request_1_json))
    assert response.status_code == 200
    assert len(response.json()) == 2

    policies = get_storage_from_http_client(test_http_client).list()
    
    assert policies[0].action.url == "http://job-manager-url:8082/jobmanager/policies/incompliance/create"
    assert policies[0].variables["threshold"] == 50
    assert policies[0].status.renderedSpec.expr.startswith("tlum_workload_info{")


    assert policies[1].action.url == "http://job-manager-url:8082/jobmanager/policies/incompliance/create"
    assert policies[1].variables["threshold"] == 67


def test_icos_app_descriptor(app_descriptor_all_yaml, caplog):

    caplog.set_level(logging.DEBUG)

    ad = TypeAdapter(ICOSAppDescriptor).validate_python(yaml.safe_load(app_descriptor_all_yaml))

    policies = process_app_descriptor(
        ad,
        "999",
        PolicyActionWebhook(url="http://localhost:1234/", httpMethod=HTTPMethod.GET),
    )

    component_1_policies_index_start = 5
    component_2_policies_index_start = 0

    assert policies[0].spec.templateName == "app-sca-score"
    assert policies[0].subject.appComponent == "ffmpeg"
    assert policies[0].variables["threshold"] == 0

    assert policies[1].spec.templateName == "app-sca-score"
    assert policies[1].subject.appComponent == "/ffmpeg|mjpeg/"
    assert policies[1].variables["threshold"] == 0

    assert policies[2].spec.templateName == "app-sca-score"
    assert policies[2].subject.appComponent == "*"
    assert policies[2].variables["threshold"] == 0
    assert policies[2].action.extraParams["remediation"] == "redeploy"

    assert policies[3].name == "mjpeg-ffmpeg-app-999-securitypolicyexample2"
    assert policies[3].spec.templateName == "app-sca-score"
    assert policies[3].subject.appComponent == "ffmpeg"
    assert policies[3].variables["threshold"] == 67
    assert policies[3].action.extraParams["remediation"] == "migrate"

    assert policies[4].spec.templateName == "app-sca-score"
    assert policies[4].subject.appComponent == "mjpeg"
    assert policies[4].variables["threshold"] == 34

    assert policies[component_1_policies_index_start + 0].spec.templateName == "app-sca-score"
    assert policies[component_1_policies_index_start + 0].subject.appComponent == "ffmpeg"
    assert policies[component_1_policies_index_start + 0].variables["threshold"] == 67

    assert policies[component_1_policies_index_start + 1].spec.templateName == "compss-under-allocation"
    assert policies[component_1_policies_index_start + 1].subject.appComponent == "ffmpeg"
    assert policies[component_1_policies_index_start + 1].variables["thresholdTimeSeconds"] == 120
    assert policies[component_1_policies_index_start + 1].action.extraParams["remediation"] == "scale-up"

    assert policies[component_1_policies_index_start + 2].spec.expr == "my-metric > 10"
    assert policies[component_1_policies_index_start + 2].subject.appComponent == "ffmpeg"
    assert policies[component_1_policies_index_start + 2].variables["compssTask"] == "provesOtel.example_task"
    assert policies[component_1_policies_index_start + 2].action.extraParams["remediation"] == "scale-down"

def test_icos_descriptor_parsing(app_descriptor_all_yaml):
    ad = TypeAdapter(ICOSAppDescriptor).validate_python(yaml.safe_load(app_descriptor_all_yaml))

def test_icos_descriptor_parsing_compss(app_descriptor_compss_1_yaml, app_descriptor_compss_2_yaml):
    ad1 = TypeAdapter(ICOSAppDescriptor).validate_python(yaml.safe_load(app_descriptor_compss_1_yaml))
    ad2 = TypeAdapter(ICOSAppDescriptor).validate_python(yaml.safe_load(app_descriptor_compss_2_yaml))
    
    assert ad2 is not None
    assert type(ad2.components[0].policies[1]) == ICOSPolmanTemplatePolicy  # type: ignore