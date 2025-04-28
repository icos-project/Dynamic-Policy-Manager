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
from io import BytesIO

import requests

from polman.common.events import PolicyEventsFactory
from polman.common.model import PolicyEventType, PolicyPhase, PolicySubjectHost
from polman.watcher.violation import build_violation
from test.utils import get_storage_from_http_client


# use the in-memory storage because we need to know the ip in advence since
# it is harcoded in the alert json "policy_2_alerts"
def test_alert_api_422(policy_2_db, test_http_client, policy_2_alerts, mocker):
    storage = get_storage_from_http_client(test_http_client)
    # add the policy to the db
    storage.insert(policy_2_db)

    # setup a mock to requests.post to intercept the webhook sending
    res = requests.Response()
    res.status_code = 422
    res.reason = "Unprocessable Entity"
    res.raw = BytesIO(b"Missing Parameter X")
    m = mocker.patch.object(requests, "post", return_value=res)

    # simulate the alert
    test_http_client.post("polman/watcher/api/v1/webhooks/alertmanager", json=policy_2_alerts)

    # look at the webhook sent
    assert len(m.mock_calls) == 2


# use the in-memory storage because we need to know the ip in advence since
# it is harcoded in the alert json "policy_2_alerts"
def test_alert_api(policy_2_db, test_http_client, policy_2_alerts, mocker):
    storage = get_storage_from_http_client(test_http_client)
    # add the policy to the db
    storage.insert(policy_2_db)

    # setup a mock to requests.post to intercept the webhook sending
    res = requests.Response()
    res.status_code = 200
    m = mocker.patch.object(requests, "post", return_value=res)

    # simulate the alert
    test_http_client.post("polman/watcher/api/v1/webhooks/alertmanager", json=policy_2_alerts)

    # look at the webhook sent
    assert len(m.mock_calls) == 1
    kall = m.mock_calls[0]
    name, args, kwargs = kall
    assert args[0] == policy_2_db.action.url
    payload = kwargs["json"]
    assert payload["policyId"] == policy_2_db.id
    assert payload["remediation"] == "scale-up"

    # look at the policy event created
    evt = storage.get(policy_2_db.id).status.events[0]
    assert evt.type == PolicyEventType.Violated
    assert evt.details["id"] == payload["id"]
    assert evt.details["currentValue"] == policy_2_alerts["alerts"][0]["annotations"]["plm_expr_value"]

    assert storage.get(policy_2_db.id).status.phase == PolicyPhase.Violated


def test_alerts_without_subject_labels(policy_2_db, test_http_client, policy_2_alerts, mocker):
    storage = get_storage_from_http_client(test_http_client)
    # add the policy to the db
    storage.insert(policy_2_db)

    # setup a mock to requests.post to intercept the webhook sending
    res = requests.Response()
    res.status_code = 200
    m = mocker.patch.object(requests, "post", return_value=res)


    modified_alert = dict(policy_2_alerts)
    del modified_alert["alerts"][0]["labels"]["icos_app_name"]

    # simulate the alert
    test_http_client.post("polman/watcher/api/v1/webhooks/alertmanager", json=modified_alert)

    # look at the webhook sent
    assert len(m.mock_calls) == 0

    # look at the policy event created
    evt = storage.get(policy_2_db.id).status.events[0]
    assert evt.type == PolicyEventType.RenderingError
    assert evt.details["error"] == "Not enough labels ('icos_app_name' is missing) in the alert to build the subject. All the labels mapped to subject fields are required. Modify the query to keep al subject labels"

    assert storage.get(policy_2_db.id).status.phase == PolicyPhase.Violated
    