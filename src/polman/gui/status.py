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

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from polman.common.api import PolmanRegistryInstance
from polman.main import get_polman_version

router = APIRouter(
    tags=["debug"],
    # dependencies=[Security(get_authorized_user)],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="web/templates")


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request, pr: PolmanRegistryInstance):
    """A simple HTTP interface with the status of the policies"""
    policies = pr.list_all_policies(sort_by="creation_time", order="desc")
    version = get_polman_version()
    return templates.TemplateResponse(name="status.html", context={"request": request, "policies": policies, "version": version})
