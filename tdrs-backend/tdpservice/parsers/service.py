"""Backward-compatible facade for tdpservice.parsers.parsing_service."""

import sys
from tdpservice.parsers.parsing_service import service as _service_module
from tdpservice.parsers.parsing_service.service import *  # noqa: F401, F403
from tdpservice.parsers.parsing_service.service import __all__  # noqa: F401

sys.modules[__name__] = _service_module
