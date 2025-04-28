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

from fastapi import APIRouter, HTTPException, Security
from pydantic import BaseModel, TypeAdapter

from polman.common.api import PolmanRegistryInstance, get_authorized_user
from polman.common.errors import PolmanError
from polman.common.model import PolicyCreate, PolicyPhase, PolicyRead, PolicyVariableType, User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    # dependencies=[Security(get_authorized_user)],
    responses={404: {"description": "Not found"}},
)

class PolicyStatsResponseModel(BaseModel):
    total: int
    active: int
    inactive: int
    enforced: int
    violated: int
    unknown: int

@router.get("/", response_model=PolicyStatsResponseModel,
    summary="Stats on the policies currently managed by Polman Registry")
def get_stats(pr: PolmanRegistryInstance):  # THIS IS A PUBLIC ENDPOINT, we do not add the Security dependency 
    """
    Returns the number of policies managed by the Polman Registry grouped by
    their status.

    This is a public endpoint: no authentication and authorization are required.
    """
    all_phases = [p.status.phase for p in pr.list_all_policies()]

    enforced = len([p for p in all_phases if p == PolicyPhase.Enforced])
    violated = len([p for p in all_phases if p == PolicyPhase.Violated])
    inactive = len([p for p in all_phases if p == PolicyPhase.Inactive])
    unknown  = len([p for p in all_phases if p == PolicyPhase.Unknown])

    return PolicyStatsResponseModel(
        total=len(all_phases),
        active=enforced+violated,
        enforced=enforced,
        violated=violated,
        inactive=inactive,
        unknown=unknown
    )


