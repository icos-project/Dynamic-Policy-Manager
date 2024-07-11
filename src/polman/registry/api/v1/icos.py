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
from polman.common.api import PolmanConfigInstance, PolmanRegistryInstance, get_authorized_user

from polman.common.model import PolicyActionWebhook, PolicyRead, User
from polman.registry.icos.models import ICOSAppDeployedRequest
from polman.registry.icos.process_app_descriptor import process_app_descriptor


logger = logging.getLogger(__name__)


router = APIRouter(
  prefix="/icos",
  tags=["icos"],
  #dependencies=[Security(get_authorized_user)],
  responses={404: {"description": "Not found"}},
)



@router.post("/", response_model=list[PolicyRead])
def icos_process_app_descriptor(req: ICOSAppDeployedRequest, 
                  pr: PolmanRegistryInstance,
                  config: PolmanConfigInstance,
                  do_not_activate: bool = False,
                  user: User = Security(get_authorized_user, scopes=["policies:create"])):
 
  logger.debug('Received request: %s', req) 
  # TODO: consider when the action is not a webhook
  
  # build the Webhook url from the service name
  
  if req.service == 'job-manager':
    webhookUrl = config.icos.job_manager_base_url + req.common_action.uri
  else:
    raise HTTPException(status_code=500, detail=f"Unknown service name in action: '{req.service}'")
  
  action = PolicyActionWebhook(
    url=webhookUrl,
    httpMethod=req.common_action.http_method,
    extraParams=req.common_action.extra_params,
    includeAccessToken=req.common_action.include_access_token
  )
  
  policies = process_app_descriptor(req.app_descriptor, req.app_instance, action)
  
  created_policies = []
  
  for policy in policies:
    p = pr.process_policy_create_request(policy, activate_created_policy=not do_not_activate)
    created_policies.append(p)
    
  return created_policies

