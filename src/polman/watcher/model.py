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

import datetime
from typing import Optional
from pydantic import BaseModel

#
#  Webhook object sent by the Alertmanager (from https://prometheus.io/docs/alerting/latest/configuration/#webhook_config)
#
#  {
#    "version": "4",
#    "groupKey": <string>,              // key identifying the group of alerts (e.g. to deduplicate)
#    "truncatedAlerts": <int>,          // how many alerts have been truncated due to "max_alerts"
#    "status": "<resolved|firing>",
#    "receiver": <string>,
#    "groupLabels": <object>,
#    "commonLabels": <object>,
#    "commonAnnotations": <object>,
#    "externalURL": <string>,           // backlink to the Alertmanager.
#    "alerts": [
#      {
#        "status": "<resolved|firing>",
#        "labels": <object>,
#        "annotations": <object>,
#        "startsAt": "<rfc3339>",
#        "endsAt": "<rfc3339>",
#        "generatorURL": <string>,      // identifies the entity that caused the alert
#        "fingerprint": <string>        // fingerprint to identify the alert
#      },
#      ...
#    ]
#  }

class AlertmanagerAlert(BaseModel):
  status: Optional[str] = None
  labels: dict[str,str]
  annotations: dict[str,str]
  startsAt: datetime.datetime
  endsAt: datetime.datetime
  generatorURL: str
  fingerprint: Optional[str] = None
  
class AlertmanagerWebhook(BaseModel):
  version: str
  groupKey: str
  truncatedAlerts: int
  status: str
  receiver: str
  groupLabels: dict[str,str]
  commonLabels: dict[str,str]
  commonAnnotations: dict[str,str]
  externalURL: str
  alerts: list[AlertmanagerAlert]

# {
#   "status": "success",
#   "data": {
#     "groups": [
#       {
#         "name": "ServiceHealthAlerts",
#         "file": "/rules/oofavanfpawlfrt.yml",
#         "rules": [
#           {
#             "state": "pending",
#             "name": "MySeondRule",
#             "query": "sum(node_cpu_seconds_total{cpu=\"0\",mode=\"idle\",node=\"master\"}) > 968370",
#             "duration": 300,
#             "keepFiringFor": 0,
#             "labels": {
#               "severity": "warning"
#             },
#             "annotations": {
#               "description": "The CPU usage for the web server is {{ $value }}% for the last 5 minutes.",
#               "summary": "My Second Policy Violated"
#             },
#             "alerts": [
#               {
#                 "labels": {
#                   "alertname": "MySeondRule",
#                   "severity": "warning"
#                 },
#                 "annotations": {
#                   "description": "The CPU usage for the web server is 9.6929513e+06% for the last 5 minutes.",
#                   "summary": "My Second Policy Violated"
#                 },
#                 "state": "pending",
#                 "activeAt": "2024-02-09T19:15:05.443543388Z",
#                 "value": "9.6929513e+06"
#               }
#             ],
#             "health": "ok",
#             "evaluationTime": 0.001558467,
#             "lastEvaluation": "2024-02-09T19:15:05.444714158Z",
#             "type": "alerting"
#           }
#         ],
#         "interval": 60,
#         "limit": 0,
#         "evaluationTime": 0.001613706,
#         "lastEvaluation": "2024-02-09T19:15:05.444670036Z"
#       }
#     ]
#   }
# }

class PrometheusAlert(BaseModel):
  state: Optional[str] = None
  labels: dict[str,str]
  annotations: dict[str,str]
  activeAt: datetime.datetime
  value: str
  partialResponseStrategy: str
  
class PrometheusRule(BaseModel):
  state: str
  name: str
  query: str
  duration: int
  labels: dict[str, str]
  annotations: dict[str, str]
  alerts: list[PrometheusAlert]
  health: str
  evaluationTime: float
  lastEvaluation: datetime.datetime
  type: str

class PrometheusRuleGroup(BaseModel):
  name: str
  file: str
  rules: list[PrometheusRule]
  interval: int
  evaluationTime: float
  lastEvaluation: datetime.datetime
  limit: int
  partialResponseStrategy: str