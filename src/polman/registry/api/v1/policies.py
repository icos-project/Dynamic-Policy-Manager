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

import logging

from fastapi import APIRouter, HTTPException, Security
from pydantic import TypeAdapter

from polman.common.api import PolmanRegistryInstance, get_authorized_user
from polman.common.errors import PolmanError
from polman.common.model import PolicyCreate, PolicyRead, PolicyVariableType, User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/policies",
    tags=["policies"],
    # dependencies=[Security(get_authorized_user)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{pid}", response_model=PolicyRead)
def get_policy(
    pid: str,
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:read"]),
):
    try:
        p = pr.get_policy_by_id(pid)
    except PolmanError:
        raise HTTPException(status_code=404, detail="Item not found")

    return p


@router.delete("/{pid}", status_code=204)
def delete_policy(
    pid: str,
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:write"]),
):
    pr.process_policy_delete_request(pid)

@router.post("/{pid}/activate", status_code=204, summary="Activate a Policy")
def activate_policy(
    pid: str, 
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:write"])
):
    pr.activate_policy(pr.get_policy_by_id(pid))

@router.post("/{pid}/deactivate", status_code=204, summary="Deactivate a Policy")
def deactivate_policy(
    pid: str, 
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:write"])
):
    pr.deactivate_policy(pr.get_policy_by_id(pid))


@router.get("/", response_model=list[PolicyRead])
def list_policies(
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:read"]),
):
    return pr.list_all_policies()


@router.post("/", response_model=PolicyRead)
def create_policy(
    policy: PolicyCreate,
    pr: PolmanRegistryInstance,
    do_not_activate: bool = False,
    user: User = Security(get_authorized_user, scopes=["policies:write"]),
):
    return pr.process_policy_create_request(
        policy, activate_created_policy=not do_not_activate
    )




@router.get("/{pid}/variables/", response_model= dict[str, PolicyVariableType],
summary="List policy variables")
def get_policy_variables(
    pid: str, 
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:read"])
):
    """
    Returns all variables currently set for the given policy.
    """
    return pr.get_policy_by_id(pid).variables


@router.post("/{pid}/variables/{name}/{value}", status_code=204, summary="Set a variable")
def set_policy_variables(
    pid: str, 
    name: str,
    value: str,
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:write"])
):

    """
    Sets a policy variable. The variable name and values are both taken from the 
    request's path.

    A conversion of {value} to `int` and to `float` are attempt. If they fail,
    values will be considered of type `str`.

    This operation also re-render the policy and might activate/deactivate it.

    The steps performed during this operation are:
    1. Deactivate the policy if it is active
    2. Set the variable
    3. Re-render the policy
    4. Activate the policy if it was active
    """

    casted_value = value
    try:
        casted_value = int(value)
    except:
        try:
            casted_value = float(value)
        except:
            pass


    pr.process_set_policy_variable(pr.get_policy_by_id(pid), name, casted_value)


@router.delete("/{pid}/variables/{name}", status_code=204, summary="Delete a policy variable")
def unset_policy_variables(
    pid: str, 
    name: str,
    pr: PolmanRegistryInstance,
    user: User = Security(get_authorized_user, scopes=["policies:write"])
):

    """
    Deletes a variable.

    If the variable does not exists, returns `404`
    If the variable is necessary for the policy rendering, returns `406`.

    In case of exception, the policy is not modified.
    """
    
    pr.process_set_policy_variable(pr.get_policy_by_id(pid), name, None)
