"""Settings for the live Go parser integration suite."""

import os
from copy import deepcopy
from distutils.util import strtobool

from .local import Local


class GoParserIntegration(Local):
    """Use the live local database so the Go parser worker sees committed changes."""

    DATABASES = deepcopy(Local.DATABASES)
    DATABASES["default"]["TEST"] = {"MIRROR": "default"}

    GO_PARSER_SHADOW_MODE = bool(
        strtobool(os.getenv("GO_PARSER_SHADOW_MODE", "false"))
    )
