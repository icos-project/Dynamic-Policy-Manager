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

import logging
from typing import List
from polman.common.api import PolmanConfigInstance, PolmanRegistryInstance
from polman.common.model import PolicyActionWebhook, PolicyCreate, PolicyRead
from polman.registry.icos.errors import ICOSAppRequestError
from polman.registry.icos.models import ICOSAppCreatedEvent, ICOSAppDeletedEvent, ICOSAppStartedEvent, ICOSAppStoppedEvent
from polman.registry.icos.process_app_descriptor import process_app_descriptor
from polman.registry.main import PolmanRegistry


logger = logging.getLogger(__name__)


def _find_all_policies_by_app(pr: PolmanRegistry, app_instance):
    return pr.find_policies(filters={
        "subject.type": "app",
        "subject.appInstance": app_instance})

def process_app_started(
    event: ICOSAppStartedEvent,
    pr: PolmanRegistry, 
    config: PolmanConfigInstance) -> List[PolicyRead]:

    app_policies = _find_all_policies_by_app(pr, event.app_instance)

    logger.debug("Found %s policies matching the request", len(app_policies))

    res = []
    for p in app_policies:
        res.append(pr.activate_policy(p))
    
    return res

def process_app_stopped(
    event: ICOSAppStoppedEvent,
    pr: PolmanRegistryInstance, 
    config: PolmanConfigInstance) -> List[PolicyRead]:
    
    app_policies = _find_all_policies_by_app(pr, event.app_instance)

    logger.debug("Found %s policies matching the request", len(app_policies))

    res = []
    for p in app_policies:
        res.append(pr.deactivate_policy(p))
    
    return res

def process_app_deleted(
    event: ICOSAppDeletedEvent,
    pr: PolmanRegistryInstance, 
    config: PolmanConfigInstance) -> List[PolicyRead]:
    
    app_policies = _find_all_policies_by_app(pr, event.app_instance)

    logger.debug("Found %s policies matching the request", len(app_policies))

    res = []
    for p in app_policies:
        res.append(pr.process_policy_delete_request(p.id))
    
    return res

def process_app_created(
    event: ICOSAppCreatedEvent,
    pr: PolmanRegistryInstance, 
    config: PolmanConfigInstance) -> List[PolicyCreate]:

    if event.callback:
        if event.service == 'job-manager':
            webhookUrl = config.icos.job_manager_base_url + event.callback.uri
        else:
            raise ICOSAppRequestError("Unknown service name in the event")
        
        action = PolicyActionWebhook(
            url=webhookUrl,
            httpMethod=event.callback.http_method,
            extraParams=event.callback.extra_params,
            includeAccessToken=event.callback.include_access_token
        )
    else:
        action = None
  
    
    policies = process_app_descriptor(event.app_descriptor, event.app_instance, action)
  
    created_policies = []
    
    for policy in policies:
        p = pr.process_policy_create_request(policy, activate_created_policy=False)
        created_policies.append(p)
        
    return created_policies
