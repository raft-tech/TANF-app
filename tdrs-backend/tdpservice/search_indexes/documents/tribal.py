"""Elasticsearch document mappings for TRIBAL submission models."""

from ..models.tribal import Tribal_TANF_T1, Tribal_TANF_T2, Tribal_TANF_T3, Tribal_TANF_T4, Tribal_TANF_T5
from ..models.tribal import Tribal_TANF_T6, Tribal_TANF_T7

class Tribal_TANF_T1DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T1 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T1

class Tribal_TANF_T2DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T2 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T2

class Tribal_TANF_T3DataSubmissionDocument():
    """Elastic search model mapping for a parsed TANF T3 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T3

class Tribal_TANF_T4DataSubmissionDocument():
    """Elastic search model mapping for a parsed Tribal TANF T4 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T4

class Tribal_TANF_T5DataSubmissionDocument():
    """Elastic search model mapping for a parsed Tribal TANF T5 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T5

class Tribal_TANF_T6DataSubmissionDocument():
    """Elastic search model mapping for a parsed Tribal TANF T6 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T6

class Tribal_TANF_T7DataSubmissionDocument():
    """Elastic search model mapping for a parsed Tribal TANF T7 data file."""

    class Django:
        """Django model reference and field mapping."""

        model = Tribal_TANF_T7
