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

from polman.common.config import PolmanConfig
from .v1.webhooks import router as webhooks_router
from .v1.test import router as test_router

from fastapi import APIRouter

logger = logging.getLogger(__name__)


def get_watcher_router(config: PolmanConfig):

  router = APIRouter(
    prefix="/api",
    #dependencies=[Security(get_authorized_user)],
    responses={404: {"description": "Not found"}},
  )


  router.include_router(webhooks_router, prefix="/v1")

  if config.api.enable_debug_calls:
    logger.info("Enabling watcher debug api calls since --api-enable-debug-calls=true")
    router.include_router(test_router, prefix="/v1")

  return router