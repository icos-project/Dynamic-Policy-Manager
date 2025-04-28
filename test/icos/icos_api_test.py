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

from polman.common.model import PolicyPhase
from polman.watcher.violation import build_violation

def test_icos_app_lifecycle_events(test_http_client_mongo, app_delete_compss_2_json, app_stop_compss_2_json, app_create_event_compss_2_json, app_start_compss_2_json, test_mongo_backend):
    
    # 1. create event
    
    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/app",
        json=json.loads(app_create_event_compss_2_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    p = test_mongo_backend.list()[0]

    assert p.name == "compss-demo-1-demo-compss-2-xxx-1"
    assert p.status.phase == PolicyPhase.Inactive


    # 2. start event

    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/app",
        json=json.loads(app_start_compss_2_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    for rp in response.json():
        assert rp["status"]["phase"] == "enforced"

    p = test_mongo_backend.list()[0]
    assert p.name == "compss-demo-1-demo-compss-2-xxx-1"
    assert p.status.phase == PolicyPhase.Enforced


    # 3. stop event

    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/app",
        json=json.loads(app_stop_compss_2_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    for rp in response.json():
        assert rp["status"]["phase"] == "inactive"

    p = test_mongo_backend.list()[0]
    assert p.name == "compss-demo-1-demo-compss-2-xxx-1"
    assert p.status.phase == PolicyPhase.Inactive


    # 4. delete event
    
    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/app",
        json=json.loads(app_delete_compss_2_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    assert 0 == len(test_mongo_backend.list())
    

def test_icos_app_lifecycle_events_compss1(test_http_client_mongo, app_create_event_compss_1_json, app_start_compss_1_json, policy_compss_1_alert, test_mongo_backend):
    
    # 1. create event
    
    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/app",
        json=json.loads(app_create_event_compss_1_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    p = test_mongo_backend.list()[0]

    assert p.name == "compss-demo-1-demo-compss-1-xxx-1"
    assert p.status.phase == PolicyPhase.Inactive

    response = test_http_client_mongo.post(
        "/polman/registry/api/v1/icos/app",
        json=json.loads(app_start_compss_1_json),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
