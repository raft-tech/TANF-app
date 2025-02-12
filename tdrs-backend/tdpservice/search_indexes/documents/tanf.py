"""Elasticsearch document mappings for TANF submission models."""
from ..models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7

class TANF_T1DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T1 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T1


class TANF_T2DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T2 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T2


class TANF_T3DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T3 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T3

class TANF_T4DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T4 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T4


class TANF_T5DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T5 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T5

class TANF_T6DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T6 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T6

class TANF_T7DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T7 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T7
