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
from polman.common.api import PolmanRegistryInstance, get_authorized_user

from polman.common.model import PolicyCreate, PolicyRead, User

logger = logging.getLogger(__name__)

router = APIRouter(
  prefix="/policies",
  tags=["policies"],
  #dependencies=[Security(get_authorized_user)],
  responses={404: {"description": "Not found"}},
)

@router.get("/{id}", response_model=PolicyRead)
def get_policy(id: str, pr: PolmanRegistryInstance,
                  user: User = Security(get_authorized_user, scopes=["policies:read"])):

  p =  pr.get_policy_by_id(id)
  
  if not p:
    raise HTTPException(status_code=404, detail="Item not found")
  
  return p


@router.get("/", response_model=list[PolicyRead])
def list_policies(pr: PolmanRegistryInstance,
                  user: User = Security(get_authorized_user, scopes=["policies:list"])):

  return pr.list_all_policies()


@router.post("/", response_model=PolicyRead)
def create_policy(policy: PolicyCreate, 
                  pr: PolmanRegistryInstance,
                  do_not_activate: bool = False,
                  user: User = Security(get_authorized_user, scopes=["policies:create"])):
 return pr.process_policy_create_request(policy, activate_created_policy=not do_not_activate)

