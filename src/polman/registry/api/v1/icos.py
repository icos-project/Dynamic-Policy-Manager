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

from typing import List
from fastapi import APIRouter, HTTPException, Security
from polman.common.api import PolmanConfigInstance, PolmanRegistryInstance, get_authorized_user

from polman.common.logging import log_object
from polman.common.model import PolicyActionWebhook, PolicyRead, User
from polman.registry.icos.app_lifecycle import process_app_created, process_app_deleted, process_app_started, process_app_stopped
from polman.registry.icos.models import ICOSAppCreatedEvent, ICOSAppDeletedEvent, ICOSAppDeployedRequest, ICOSAppEvent, ICOSAppStartedEvent, ICOSAppStoppedEvent
from polman.registry.icos.process_app_descriptor import process_app_descriptor
from polman.registry.icos.errors import ICOSAppRequestError

logger = logging.getLogger(__name__)


router = APIRouter(
  prefix="/icos",
  tags=["icos"],
  #dependencies=[Security(get_authorized_user)],
  responses={404: {"description": "Not found"}},
)

@router.post("/app", response_model=List[PolicyRead],
  summary="Notify events for ICOS Apps",
  openapi_extra={
        "requestBody": {
            "content": {"application/json": {"examples": {
              "created":  {
                "value": {
                  "app_instance": "demo-app-999",
                  "event": "created",
                  "service": "job-manager",
                  "app_descriptor": "name: mjpeg-ffmpeg-app\ndescription: \"the description\"\ncomponents:\n- name: ffmpeg\n  type: manifest\n  manifests:\n  - name: ffmpeg-pod\n- name: mjpeg\n  type: manifest\n  manifests:\n  - name: mjpeg-service\n  - name: mjpeg-pod\npolicies:\n- component: \"*\"\n  fromTemplate: app-host-cpu-usage\n  remediation: migrate\n  variables:\n    maxCpu: 0.8\n---\napiVersion: v1\nkind: Pod\nmetadata:\n  name: ffmpeg-pod\n  namespace: demo\nspec:\n  containers:\n  - name: ffmpeg-container\n    image: santojim/ffmpeg:arm64\n    command:\n    - \"ffmpeg\"\n    args:\n    - \"-i\"\n    - \"http://10.150.0.133:30674/mjpeg\"\n    - \"-fs\"\n    - \"100M\"\n    - \"-c:v\"\n    - \"copy\"\n    - \"video.mp4\"\n---\napiVersion: v1\nkind: Pod\nmetadata:\n  name: mjpeg-pod\n  namespace: demo\n  labels:\n    app.kubernetes.io/name: mjpeg\nspec:\n  containers:\n  - name: kceu\n    image: santojim/camera_to_ip:arm64\n    command:\n    - /cam2ip\n    args:\n    - --bind-addr=:8080\n    ports:\n    - containerPort: 8080\n      name: http\n    resources:\n      limits:\n        squat.ai/video: 1\n---\napiVersion: v1\nkind: Service\nmetadata:\n  name: mjpeg-service\n  namespace: demo\nspec:\n  selector:\n    app.kubernetes.io/name: mjpeg\n  ports:\n  - protocol: TCP\n    port: 8080\n    targetPort: 8080\n    nodePort: 30674\n  type: NodePort\n\n",
                  "callback": {
                    "uri": "/jobmanager/policies/incompliance/create",
                    "http_method": "POST",
                    "extra_params": {
                        "customParam": "test-1"
                    }
                  },
                }
              },
              "started": {
                "value": {
                  "app_instance": "demo-app-999",
                  "event": "started",
                  "service": "job-manager"
                }
              },
              "stopped": {
                "value": {
                  "app_instance": "demo-app-999",
                  "event": "stopped",
                  "service": "job-manager"
                }
              },
              "deleted": {
                "value": {
                  "app_instance": "demo-app-999",
                  "event": "deleted",
                  "service": "job-manager"
                }
              },
            }}},
            "required": True,
        },
    },)
def icos_app_update(req: ICOSAppEvent, 
                  pr: PolmanRegistryInstance,
                  config: PolmanConfigInstance,
                  user: User = Security(get_authorized_user, scopes=["icos-app:write"])):
  """
  Notify lifecycle events of ICOS Applications. This allows Polman to react to 
  the events by configuring the policies accordingly. Currently, the following 
  events are supported: **created**, **started**, **stopped**, **deleted**.

  The payload should be a json file with these mandatory fields:

  ```
  {
    "app_instance":   <id-of-the-application>
    "event":          created|started|stopped|deleted
    "service":        <service-that-is-making-the-notification>
  }
  ```

  For the **created** event only, the following additional fields are considered:

  ```
  {
    ...
    "app_descriptor": <app-descriptor-as-yaml-string>
    "callback": {
        "type": "icos-service"
        "uri": <path-that-polman-will-call-when-policies-are-violated>,
        "http_method": GET|POST|PUT|DELETE,
        "include_access_token": true|false,
        "extra_params": {
            "customParam": "test-1"
        }
    }
    ...
  ]
  ```
  For further examples, see below.
  """

  logger.debug("Received request:\n%s", log_object(req))

  if isinstance(req, ICOSAppCreatedEvent):
    return process_app_created(req, pr, config)
  
  if isinstance(req, ICOSAppStartedEvent):
    return process_app_started(req, pr, config)

  if isinstance(req, ICOSAppStoppedEvent):
    return process_app_stopped(req, pr, config)

  if isinstance(req, ICOSAppDeletedEvent):
    return process_app_deleted(req, pr, config)

  raise ICOSAppRequestError("Only events for app start/stop are allowed")


@router.post("/", response_model=list[PolicyRead],
  summary="Create policies for an ICOS App",
  deprecated=True)
def icos_process_app_descriptor(req: ICOSAppDeployedRequest, 
                  pr: PolmanRegistryInstance,
                  config: PolmanConfigInstance,
                  do_not_activate: bool = False,
                  user: User = Security(get_authorized_user, scopes=["icos-app:write"])):
 
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
