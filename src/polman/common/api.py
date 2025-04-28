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
from typing import Annotated

import jose
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import SecurityScopes
from keycloak import KeycloakPostError

from polman.common.config import PolmanConfig
from polman.common.errors import PolicyNotFoundError, PolmanError
from polman.common.keycloak import KeycloakClient
from polman.common.model import User
from polman.registry.main import PolmanRegistry
from polman.watcher.main import PolmanWatcher

logger = logging.getLogger(__name__)


async def get_polman_config(request: Request):
    return request.app.state.polman_config


PolmanConfigInstance = Annotated[PolmanConfig, Depends(get_polman_config)]

keycloak_client_instance = None


async def get_keycloak_client(config: PolmanConfigInstance):
    global keycloak_client_instance
    if not keycloak_client_instance:
        keycloak_client_instance = KeycloakClient(config)
    return keycloak_client_instance


async def get_polman_registry(request: Request):
    # return get_instance().registry
    return request.app.state.polman_registry


async def get_polman_watcher(request: Request):
    # return get_instance().watcher
    return request.app.state.polman_watcher


PolmanRegistryInstance = Annotated[PolmanRegistry, Depends(get_polman_registry)]
PolmanWatcherInstance = Annotated[PolmanWatcher, Depends(get_polman_watcher)]
KeycloakClientInstance = Annotated[KeycloakClient, Depends(get_keycloak_client)]


async def get_validate_token(
    keycloak_client: KeycloakClientInstance,
    config: PolmanConfigInstance,
    authorization: Annotated[str | None, Header()] = None,
):
    if config.authn.skip:
        logger.debug("Not validating token because auth.enabled is False")
        return

    if not authorization:
        raise HTTPException(status_code=401, detail="Token not provided")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token header invalid")

    logger.debug("Validating token")

    token = authorization.removeprefix("Bearer ")

    try:
        keycloak_client.validate_token(token)
        return token
    except jose.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as ex:
        logger.error("Token validation error: %s", str(ex))
        raise HTTPException(status_code=503, detail="Exception validating the token. See server logs for details.")


async def get_authenticated_user(
    keycloak_client: KeycloakClientInstance, config: PolmanConfigInstance, token=Depends(get_validate_token)
):
    if config.authn.skip:
        return User(name="anonymous", email="anonymous@example.org", username="anonymous", scopes=[])

    token_info = keycloak_client.validate_token(token)
    logger.debug("Claims in token: %s", list(token_info.keys()))


    user = User(
        name=token_info.get("name", ""),
        email=token_info.get("email", ""),
        username=token_info["preferred_username"],
        scopes=token_info["scope"].split(" "),
    )
    return user


async def get_authorized_user(
    request: Request,
    security_scopes: SecurityScopes,
    config: PolmanConfigInstance,
    keycloak_client: KeycloakClientInstance,
    token=Depends(get_validate_token),
    user: User = Depends(get_authenticated_user),
):
    if config.authz.skip:
        logger.debug("Not authorizing the request because authz.enabled is False")
        return user

    if config.authz.fallback_scope and len(security_scopes.scopes) == 0:
        logger.warn("Operation %s does not require any authorization scope, but '--authz-fallback-scope=%s'", request.url.path, config.authz.fallback_scope)
        security_scopes.scopes = [config.authz.fallback_scope]

    try:
        permissions = {}
        for s in security_scopes.scopes:
            resource, scope = s.split(":", 2)
            if resource not in permissions:
                permissions[resource] = []
            permissions[resource].append(scope)

        res = keycloak_client.is_authorized(token, permissions)
        if res:
            return user
        else:
            raise HTTPException(status_code=403, detail="Not Authorized")
    except KeycloakPostError as ex:
        print(ex)
        raise HTTPException(status_code=403, detail="Not Authorized")

    # authz based on token scopes
    # for s in security_scopes.scopes:
    #    if s not in user.scopes:
    #        raise HTTPException(status_code=403, detail="Not Authorized")

    return user


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 422, "detail": exc.args[0]}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

async def policy_variable_not_found_error_handler(request: Request, exc: PolicyNotFoundError):
    exc_str = str(exc)
    content = {"status_code": 404, "detail": exc_str}
    return JSONResponse(content=content, status_code=status.HTTP_404_NOT_FOUND)

async def policy_rendering_test_error_handler(request: Request, exc: PolicyNotFoundError):
    exc_str = str(exc)
    content = {"status_code": 406, "detail": exc_str}
    return JSONResponse(content=content, status_code=status.HTTP_406_NOT_ACCEPTABLE)

async def policy_not_found_error_handler(request: Request, exc: PolicyNotFoundError):
    exc_str = f'Policy with id "{str(exc)}" couldn\'t be found'
    content = {"status_code": 404, "detail": exc_str}
    return JSONResponse(content=content, status_code=status.HTTP_404_NOT_FOUND)

async def generic_polman_error_handler(request: Request, exc: PolmanError):
    exc_str = str(exc)
    content = {"status_code": 500, "detail": exc_str}
    return JSONResponse(content=content, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
