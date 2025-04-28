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

policy = {
    "name": "gabriele-app-container-cpu-utilization",
    "subject": {
        "appName": "fake-gabriele-app",
        "appComponent": "backend",
        "appInstance": "9997ccb4-3dd9-4f5c-aac9-d69160c373c6"
    },
    "spec": {
        "expr": "container_cpu_utilization_ratio{{{subject_label_selector}}}",
        "violatedIf": "> {{maxCpu}}"
    },
    "variables": {
        "maxCpu": "0.8"
    },
    "properties": {
        "pendingInterval": "30s"
    },
    "action": {
        "url": "http://localhost:3456/",
        "httpMethod": "POST"
    }
}
