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

from fastapi import APIRouter, Request
from polman.common.api import PolmanRegistryInstance, PolmanWatcherInstance
from polman.watcher.model import AlertmanagerWebhook
from polman.watcher.prometheus_rule_engine import subject_field_value_from_labels, subject_to_labels_dict


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)


@router.post("/violate/{policy_id}/{expr_value}")
def test_violation(policy_id, expr_value: float, req: Request, pw: PolmanWatcherInstance, pr: PolmanRegistryInstance):
    """Forces the violation of a policy. It must be used only for debugging 
    purposes. This call is available only if the --api-enable-debug-calls is
    used.

    Any query parameter specified will be interpreted as label of the
    Prometheus alert and, hence, will appear as extraLabel in the callback.
    """
    request_args = dict(req.query_params)
    logger.debug(f"Testing violation -> policy: {policy_id} - value: {expr_value} - labels: {request_args}")

    p = pr.get_policy_by_id(policy_id)

    subject_labels = subject_to_labels_dict(p.subject)

    labels = dict(subject_labels)

    # add labels coming from request. Do it later the subject labels to be able to
    # override also subject labels from the request
    labels.update(request_args)

    pw.violate_policy(p, "debug-api", expr_value, labels)
    

@router.post("/resolve/{policy_id}")
def test_resolution(policy_id, pw: PolmanWatcherInstance, pr: PolmanRegistryInstance):
    """Forces the resolution of a policy. It must be used only for debugging 
    purposes. This call is available only if the --api-enable-debug-calls is
    used.
    """
    logger.debug(f"Testing resolution -> policy: {policy_id}")
    p = pr.get_policy_by_id(policy_id)
    pw.resolve_policy(p)