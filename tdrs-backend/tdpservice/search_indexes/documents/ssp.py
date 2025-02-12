"""Elasticsearch document mappings for SSP submission models."""
from ..models.ssp import SSP_M1, SSP_M2, SSP_M3, SSP_M4, SSP_M5, SSP_M6, SSP_M7

class SSP_M1DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M1 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M1

class SSP_M2DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M2 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M2

class SSP_M3DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M3 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M3
class SSP_M4DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M4 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M4
class SSP_M5DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M5 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M5
class SSP_M6DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M6 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M6
class SSP_M7DataSubmissionDocument():
    """Elastic search model mapping for a parsed SSP M7 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M7
