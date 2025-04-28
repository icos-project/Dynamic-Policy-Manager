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

from jinja2 import BaseLoader, Environment, StrictUndefined
from jinja2.exceptions import UndefinedError

from polman.common.errors import PolicyRenderingError, PolicyRenderingTestError
from polman.common.model import PolicyCreate, PolicySpec, PolicySpecTelemetry, PolicySpecTemplate
from polman.registry.templates_catalog import POLICY_SPEC_TEMPLATES_CATALOG
from polman.watcher.prometheus_rule_engine import subject_to_labels_list, subject_to_labels_selector



def test_spec_rendering(policy: PolicyCreate, extra_variables: dict = {}):
    # test if the new variable introduces rendering errors
    test_policy = policy.model_copy(deep=True)
    for name, value in extra_variables.items():
        if not value:
            del test_policy.variables[name]
        else:
            test_policy.variables[name] = value

    try:
        render_policy_spec(test_policy)
    except Exception as ex:
        raise PolicyRenderingTestError(str(ex)) from ex
        

def render_policy_spec(policy: PolicyCreate) -> PolicySpec: # type: ignore
    """Render the template tokens in the policy expression."""

    new_spec = policy.spec.model_copy(deep=True)

    if isinstance(new_spec, PolicySpecTemplate):
        new_spec = POLICY_SPEC_TEMPLATES_CATALOG[new_spec.templateName].model_copy()

    # rendering specific to telemetry specs
    if isinstance(new_spec, PolicySpecTelemetry):
        full_expr_tpl = new_spec.expr
        if new_spec.violatedIf:
            full_expr_tpl += f" {new_spec.violatedIf}"
            new_spec.violatedIf = None

        ctxt = {
            "subject": policy.subject.model_dump(mode="python"),
            "subject_label_selector": subject_to_labels_selector(policy.subject),
            "subject_label_list": subject_to_labels_list(policy.subject),
        }

        ctxt |= policy.variables

        # since prometheus uses "{}" to specify the metric labels and jinja2 uses
        # {{}} for template expressions, it might happen to have expressions like
        # "container_cpu_utilization_ratio{{{subject_label_selector}}}" that is not
        # well parsed by jinja2. If we change it to
        # "container_cpu_utilization_ratio{ {{subject_label_selector}} }" it is
        # parsed correctly by jinja
        full_expr_tpl = full_expr_tpl.replace("{{{", "{ {{").replace("}}}", "}} }")

        rtemplate = Environment(loader=BaseLoader(), undefined=StrictUndefined).from_string(full_expr_tpl)

        try:
            new_spec.expr = rtemplate.render(**ctxt)
            return new_spec
        except UndefinedError as ex:
            raise PolicyRenderingError(f"Cannot render the policy spec '{full_expr_tpl}': {str(ex)}")


    
