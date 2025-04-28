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
import time
from http import HTTPMethod

import requests

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_DELAY = 2


def dict_to_list(d):
    res = {}

    for k, v in d.items():
        if isinstance(v, dict):
            entries = dict_to_list(v)
            for sk, sv in entries.items():
                res[f"{k}.{sk}"] = sv
        else:
            res[k] = v

    return res


# TODO: make this async!
def http_request(method: HTTPMethod, url, params, include_access_token=False, keycloak_client=None):
    retries = 0

    headers = {}

    if include_access_token and keycloak_client:
        headers["Authorization"] = f"Bearer {keycloak_client.get_plm_token()}"

    while retries < MAX_RETRIES:
        try:
            if method == HTTPMethod.GET:
                res = requests.get(url, headers=headers, params=dict_to_list(params))
            elif method == HTTPMethod.POST:
                res = requests.post(url, headers=headers, json=params)
            else:
                raise Exception("Unsupported method")

            if res.status_code >= 400:
                logger.warning("Received status %s %s. Retrying", res.status_code, res.reason)
                logger.debug("Response content: %s", res.content)
            else:
                return
        except Exception as ex:
            logger.warn('webhook action failed with "%s". Retrying', str(ex))
        finally:
            retries += 1
            time.sleep(RETRY_DELAY)

    logger.error("Max retry reached! Giving up")
