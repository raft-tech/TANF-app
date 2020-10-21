"""stts fixtures."""

from django.core.management import call_command

import pytest
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@pytest.fixture
def stts():
    """Populate STTs."""
    logger.info("%%%%%%%%CALLING POPULATE%%%%%%%%%%%%")
    call_command("populate_stts")
