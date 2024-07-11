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
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import uvicorn
from polman.common.api import validation_exception_handler
from polman.common.config import PolmanConfig
from polman.common.service import PolmanService
from polman.registry.api.main import router as registry_router
from polman.registry.main import PolmanRegistry
from polman.watcher.api.main import router as watcher_router
from polman.gui.status import router as status_router
from fastapi.middleware.cors import CORSMiddleware

from polman.watcher.main import PolmanWatcher
logger = logging.getLogger(__name__)



class PolmanApi(PolmanService):
  
  
  def __init__(self, config: PolmanConfig, pr: PolmanRegistry, pw: PolmanWatcher):
    super().__init__(config)
    logger.info('Initializing Polman API')
     
    self.__api_root = config.api.root
    self.__cors_origins = config.api.allowed_cors_origins
    self.__host = config.api.host
    self.__port = config.api.port
    
    self.__init_fastapi_app(config, pr, pw)
     
  
  def __init_fastapi_app(self, config: PolmanConfig, pr: PolmanRegistry, pw: PolmanWatcher):
    app = FastAPI(
        root_path=self.__api_root,
        title="Polman API",
        servers=[
                {"url": f"http://localhost:8000{self.__api_root}", "description": "Local Development"},
                {"url": f"http://10.160.3.20:30700{self.__api_root}", "description": "ICOS Staging Testbed"},
            ],
        root_path_in_servers=False
        )

    if self.__cors_origins:
        logger.info('CORS enabled (--api-allowed-cors-origins): %s', self.__cors_origins)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.__cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        logger.debug('CORS not enabled. Use the --allowed-cors-origins to set them')

    app.state.polman_registry = pr
    app.state.polman_watcher = pw
    app.state.polman_config = config

    app.mount("/static", StaticFiles(directory="web/static"), name="static")

    app.include_router(registry_router, prefix="/registry")
    app.include_router(watcher_router, prefix="/watcher")
    app.include_router(status_router, prefix="/status")
    
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    #dpmApi = APIRouter()
    #dpmApi.include_router(policies.router)
    #dpmApi.include_router(webhooks.router)
    #dpmApi.include_router(icos_router)
    #if dpm.config.api.enable_admin_api:
    #    dpmApi.include_router(admin.router)
    #app.include_router(dpmApi, prefix='/api/v1')

    self.__root = FastAPI(openapi_url=None)
    self.__root.mount(self.__api_root, app)
    self.app = self.__root
    
  async def start(self, dry_run=False):
    config = uvicorn.Config(app=self.__root, host=self.__host, port=self.__port)
    server = uvicorn.Server(config)
    
    if dry_run:
      logger.warning('Exiting now because --dry-run flag is set')
    else:
      await server.serve()
      logger.info("API Server started")