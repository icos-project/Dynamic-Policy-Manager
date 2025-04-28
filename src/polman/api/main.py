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

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from polman.common.api import generic_polman_error_handler, policy_not_found_error_handler, policy_rendering_test_error_handler, policy_variable_not_found_error_handler, validation_exception_handler
from polman.common.config import PolmanConfig
from polman.common.errors import PolicyNotFoundError, PolicyRenderingTestError, PolicyVariableNotExist, PolmanError
from polman.common.service import PolmanService
from polman.gui.status import router as status_router
from polman.registry.api.main import router as registry_router
from polman.registry.main import PolmanRegistry
from polman.watcher.api.main import get_watcher_router
from polman.watcher.main import PolmanWatcher

logger = logging.getLogger(__name__)


class PolmanApi(PolmanService):
    def __init__(self, config: PolmanConfig, pr: PolmanRegistry, pw: PolmanWatcher):
        super().__init__(config)
        logger.info("Initializing Polman API")

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
            root_path_in_servers=False,
        )

        if self.__cors_origins:
            logger.info("CORS enabled (--api-allowed-cors-origins): %s", self.__cors_origins)
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.__cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        else:
            logger.debug("CORS not enabled. Use the --allowed-cors-origins to set them")

        app.state.polman_registry = pr
        app.state.polman_watcher = pw
        app.state.polman_config = config

        app.mount("/static", StaticFiles(directory="web/static"), name="static")

        app.include_router(registry_router, prefix="/registry")
        app.include_router(get_watcher_router(config), prefix="/watcher")
        app.include_router(status_router, prefix="/status")

        
        # Keep generic_polman_error_handler as first since
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(PolmanError, generic_polman_error_handler)
        app.add_exception_handler(PolicyNotFoundError, policy_not_found_error_handler)
        app.add_exception_handler(PolicyVariableNotExist, policy_variable_not_found_error_handler)
        app.add_exception_handler(PolicyRenderingTestError, policy_rendering_test_error_handler)

        self.__root = FastAPI(openapi_url=None)
        self.__root.mount(self.__api_root, app)
        self.app = self.__root

    def get_openapi_schema(self) -> dict:
        """Return the openapi schema for the Polman API."""
        return self.app.routes[0].app.openapi() # type: ignore

    async def start(self, dry_run=False):
        log_config = uvicorn.config.LOGGING_CONFIG  # type: ignore
        log_config["formatters"]["access"]["fmt"] = (
            "%(asctime)s - [%(threadName)-10s] [uvicorn] - %(levelname)s: %(message)s"
        )
        log_config["formatters"]["default"]["fmt"] = (
            "%(asctime)s - [%(threadName)-10s] [uvicorn] - %(levelname)s: %(message)s"
        )
        config = uvicorn.Config(app=self.__root, host=self.__host, port=self.__port, log_config=log_config)
        server = uvicorn.Server(config)

        if dry_run:
            logger.warning("Exiting now because --dry-run flag is set")
        else:
            await server.serve()
            logger.info("API Server started")
