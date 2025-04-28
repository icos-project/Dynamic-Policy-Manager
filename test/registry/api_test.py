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

# ruff: noqa: S101

from http import HTTPStatus
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette.testclient import TestClient
from polman.common.model import PolicyEventType, PolicyPhase
from polman.registry.main import PolmanRegistry
from test.utils import get_registry_from_http_client, get_storage_from_http_client


def test_get_existing_policy(test_http_client, test_policy_factory):
    person_instance = test_policy_factory.build()

    get_storage_from_http_client(test_http_client).insert(person_instance)

    response = test_http_client.get(f"/polman/registry/api/v1/policies/{person_instance.id}")
    assert response.status_code == 200
    assert response.json()["name"] == person_instance.name


def test_get_not_existing_policy(test_http_client):
    response = test_http_client.get("/polman/registry/api/v1/policies/123")
    assert response.status_code == 404


def test_delete_not_existing_policy(test_http_client: TestClient) -> None:
    """When deleting a not-existing policy, 404 should be returned."""
    response = test_http_client.delete("/polman/registry/api/v1/policies/123")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_policy(test_http_client_mongo: TestClient, policy_c1) -> None:
    """Test deletion of a policy with mongodb backend."""
    response = test_http_client_mongo.post("/polman/registry/api/v1/policies", json=policy_c1)

    ps = get_storage_from_http_client(test_http_client_mongo)

    assert len(ps.list()) == 1

    policy_id = response.json()["id"]
    response = test_http_client_mongo.delete(f"/polman/registry/api/v1/policies/{policy_id}")

    assert response.status_code == 204

    assert len(ps.list()) == 0

def test_activate_policy(test_http_client_mongo: TestClient, policy_c1) -> None:
    """Test activation of a policy with mongodb backend."""
    response = test_http_client_mongo.post("/polman/registry/api/v1/policies", json=policy_c1)

    pr : PolmanRegistry = get_registry_from_http_client(test_http_client_mongo)

    assert len(pr.list_all_policies()) == 1
    p1 = pr.list_all_policies()[0]
    assert p1.status.phase == PolicyPhase.Enforced

    response = test_http_client_mongo.post(f"/polman/registry/api/v1/policies/{p1.id}/deactivate")
    p1 = pr.list_all_policies()[0]
    assert p1.status.phase == PolicyPhase.Inactive

    response = test_http_client_mongo.post(f"/polman/registry/api/v1/policies/{p1.id}/activate")
    p1 = pr.list_all_policies()[0]
    assert p1.status.phase == PolicyPhase.Enforced


def test_get_set_variable(test_http_client_mongo: TestClient, policy_c1) -> None:
    """Test change of a policy variable with mongodb backend."""

    response = test_http_client_mongo.post("/polman/registry/api/v1/policies", json=policy_c1)

    pr : PolmanRegistry = get_registry_from_http_client(test_http_client_mongo)

    assert len(pr.list_all_policies()) == 1
    p1 = pr.list_all_policies()[0]
    assert p1.status.phase == PolicyPhase.Enforced
    assert p1.variables["maxCpu"] == 0.8


    response = test_http_client_mongo.get(f"/polman/registry/api/v1/policies/{p1.id}/variables/")
    assert response.json() == {"maxCpu": 0.8}

    response = test_http_client_mongo.post(f"/polman/registry/api/v1/policies/{p1.id}/variables/maxCpu/0.2")
    p1 = pr.list_all_policies()[0]
    assert p1.variables["maxCpu"] == 0.2
    assert [evt.type for evt in p1.status.events[-4:]] == [
        PolicyEventType.Deactivated,
        PolicyEventType.VariableSet,
        PolicyEventType.Rendered,
        PolicyEventType.Activated]

    response = test_http_client_mongo.get(f"/polman/registry/api/v1/policies/{p1.id}/variables/")
    assert response.json() == {"maxCpu": 0.2}

    # add a new variable and verify that is returned
    response = test_http_client_mongo.post(f"/polman/registry/api/v1/policies/{p1.id}/variables/newVar/testVal")
    response = test_http_client_mongo.get(f"/polman/registry/api/v1/policies/{p1.id}/variables/")
    assert response.json() == {"maxCpu": 0.2, "newVar": "testVal"}

    # delete the new variable and verify
    response = test_http_client_mongo.delete(f"/polman/registry/api/v1/policies/{p1.id}/variables/newVar")
    response = test_http_client_mongo.get(f"/polman/registry/api/v1/policies/{p1.id}/variables/")
    assert response.json() == {"maxCpu": 0.2}

    # delete the variable needed for the rendering
    response = test_http_client_mongo.delete(f"/polman/registry/api/v1/policies/{p1.id}/variables/maxCpu")
    assert response.status_code == 406
    p1 = pr.list_all_policies()[0]
    assert p1.status.phase == PolicyPhase.Enforced
    
    # verify that the variable has not been deleted
    response = test_http_client_mongo.get(f"/polman/registry/api/v1/policies/{p1.id}/variables/")
    assert response.json() == {"maxCpu": 0.2}


def test_get_stats(test_http_client, test_policy_factory):

    phases = [
        PolicyPhase.Enforced, PolicyPhase.Inactive, PolicyPhase.Unknown,
        PolicyPhase.Violated, PolicyPhase.Enforced, PolicyPhase.Enforced, 
        PolicyPhase.Inactive, PolicyPhase.Violated, PolicyPhase.Enforced]

    # add policies with the phases listed above
    for ph in phases:
        p1 = test_policy_factory.build()
        p1.status.phase = ph
        get_storage_from_http_client(test_http_client).insert(p1)

    response = test_http_client.get(f"/polman/registry/api/v1/stats")
    assert response.status_code == 200
    assert response.json()["total"] == 9
    assert response.json()["active"] == 6
    assert response.json()["inactive"] == 2
    assert response.json()["enforced"] == 4
    assert response.json()["violated"] == 2
    assert response.json()["unknown"] == 1