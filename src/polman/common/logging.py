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
import sys
from http.client import HTTPConnection

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text

logger = logging.getLogger(__name__)

logging_ctx = {"execution": None, "step": None, "workload": None}
messages_recording_handler_instance = None
main_handler_instance = None

class SystemLogFilter(logging.Filter):
    def filter(self, record):
        ctxstr = ""
        if logging_ctx["workload"]:
            ctxstr = "[{workload}:{step}]".format(**logging_ctx)
        setattr(record, "context", ctxstr)
        record.name_and_lineno = f"{record.name}:{record.lineno}"
        return True


class MessagesRecordingHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET):
        super().__init__(level=level)
        self.is_recording = False
        self.recorded_records = []

    def emit(self, record):
        if self.is_recording:
            fmt = self.format(record)
            self.recorded_records.append(fmt)

    def start_recording(self):
        self.is_recording = True
        self.recorded_records = []

    def stop_recording(self):
        self.is_recording = False
        return self.recorded_records


def init_logging(
    verbosity,
    app_toplevel_logger_name=None,
    use_rich_output=False,
    only_fatal_loggers=[],
):
    """Configure logging

    ┌─────────────────┬───────────┬─────────────────────────────────────────────────────────────────────┐
    │ Console option  │ verbosity │                               Logging                               │
    ├─────────────────┼───────────┼─────────────────────────────────────────────────────────────────────┤
    │ -q or --quiet   │     -1    │ Disable all loggers                                                 │
    │ (none)          │      0    │ ERROR messages from all loggers                                     │
    │ -v              │      1    │ WARNING messages from app logger and ERROR from the others          │
    │ -vv             │      2    │ INFO messages from app logger and ERROR from the others             │
    │ -vvv            │      3    │ DEBUG messages from app logger and ERROR from the others            │
    │ -vvvv           │      4    │ DEBUG messages from all loggers                                     │
    │ -vvvvv          │      5    │ DEBUG messages from all loggers + log all http requests/responses   │
    └─────────────────┴───────────┴─────────────────────────────────────────────────────────────────────┘

    :param verbosity: the verbosity level set in the cli
    :param app_toplevel_logger_name: name of the top logger. Leave to None to get the current one
    :param only_fatal_loggers: a list of loggers that will show only fatal messages


    """
    global messages_recording_handler_instance
    global main_handler_instance

    logging_format = "%(asctime)s - [%(threadName)-10s] [%(name_and_lineno)s] - %(levelname)s: %(message)s"
    formatter = logging.Formatter(logging_format)
    filter = SystemLogFilter()

    root_logger = logging.getLogger()

    if main_handler_instance:
        root_logger.removeHandler(main_handler_instance)

    main_handler_instance = (
        RichHandler() if use_rich_output else logging.StreamHandler(sys.stdout)
    )
    if not use_rich_output:
        main_handler_instance.setFormatter(formatter)
    main_handler_instance.addFilter(filter)

    if messages_recording_handler_instance:
        root_logger.removeHandler(messages_recording_handler_instance)

    messages_recording_handler_instance = MessagesRecordingHandler()
    messages_recording_handler_instance.setFormatter(formatter)
    messages_recording_handler_instance.addFilter(filter)

    root_logger.addHandler(main_handler_instance)
    root_logger.addHandler(messages_recording_handler_instance)

    app_logger = logging.getLogger(__name__.split(".")[0])

    if verbosity <= -1:
        root_logger.disabled = True
        app_logger.disabled = True
    elif verbosity == 0:
        root_logger.setLevel(logging.ERROR)
        app_logger.setLevel(logging.ERROR)
    elif verbosity == 1:
        root_logger.setLevel(logging.ERROR)
        app_logger.setLevel(logging.WARNING)
    elif verbosity == 2:
        root_logger.setLevel(logging.ERROR)
        app_logger.setLevel(logging.INFO)
    elif verbosity == 3:
        root_logger.setLevel(logging.ERROR)
        app_logger.setLevel(logging.DEBUG)
    elif verbosity >= 4:
        root_logger.setLevel(logging.DEBUG)
        app_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.NOTSET)

    if verbosity >= 5:
        HTTPConnection.debuglevel = 1

    for logger_name in only_fatal_loggers:
        logging.getLogger(logger_name).setLevel(logging.FATAL)
        logger.debug(f"Disabled (only FATAL messages) logger {logger_name}")

    logger.info("Logging initialized")


def set_logging_context(**kwargs):
    logging_ctx.update(kwargs)


def start_logs_recording():
    if messages_recording_handler_instance:
        messages_recording_handler_instance.start_recording()


def stop_logs_recording():
    if messages_recording_handler_instance:
        return messages_recording_handler_instance.stop_recording()


def log_object(obj):
    panel = Panel(Pretty(obj, expand_all=True))
    console = Console(width=150)
    with console.capture() as capture:
        console.print(panel)

    return Text.from_ansi(capture.get())
