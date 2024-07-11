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


from polman.common.model import PolicySpecTelemetry


POLICY_SPEC_TEMPLATES_CATALOG = {
  'compss-under-allocation': PolicySpecTelemetry(
    expr="sum by ({{subject_label_list}}) (compss_avgTime_ratio{CoreSignature=\"{{ compssTask }}\", {{subject_label_selector}}} * compss_pendTasks_ratio{CoreSignature=\"{{ compssTask }}\", {{subject_label_selector}}}) / sum by ({{subject_label_list}}) (compss_node_info{property=\"computing_units\", {{subject_label_selector}}}) / 1000",
    violatedIf="> {{thresholdTimeSeconds}}",
    thresholds= {
        "warning": 200,
        "critical": 500
      }
  ),
  'cpu-usage-host': PolicySpecTelemetry(
    expr="avg by(icos_host_name, {{subject_label_list}}) (1 - rate(node_cpu_seconds_total{mode=\"idle\", {{subject_label_selector}}}[2m]))",
    violatedIf="> {{maxCpuUsagePercent}}",
  ),
  'app-host-cpu-usage': PolicySpecTelemetry(
    expr="tlum_workload_info{ {{subject_label_selector}} } *on(icos_host_id) group_left avg without (cpu) (1 - rate(node_cpu_seconds_total{mode=\"idle\"}[2m]))",
    violatedIf="> {{maxCpu}}"
  )
}