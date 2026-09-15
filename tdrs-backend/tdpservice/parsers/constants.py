"""Constants for parser classes."""

from tdpservice.parsers.dataclasses import Position

HEADER_POSITION = Position(0, 6)
TRAILER_POSITION = Position(0, 7)

SSN_AREA_NUMBER_POSITION = slice(0, 3)
SSN_GROUP_NUMBER_POSITION = slice(3, 5)
SSN_SERIAL_NUMBER_POSITION = slice(5, 9)
INVALID_SSN_AREA_NUMBERS = ["000", "666"]
INVALID_SSN_GROUP_NUMBERS = ["00"]
INVALID_SSN_SERIAL_NUMBERS = ["0000"]


class ProgramType:
    """Program codes carried by parser inputs and file headers."""

    TANF = "TAN"
    SSP = "SSP"
    TRIBAL = "TRIBAL"
    FRA = "FRA"


class Section:
    """Section names carried by parser inputs and file headers."""

    ACTIVE_CASE_DATA = "Active Case Data"
    CLOSED_CASE_DATA = "Closed Case Data"
    AGGREGATE_DATA = "Aggregate Data"
    STRATUM_DATA = "Stratum Data"
    FRA_WORK_OUTCOME_TANF_EXITERS = "Work Outcomes of TANF Exiters"
    FRA_SECONDRY_SCHOOL_ATTAINMENT = "Secondary School Attainment"
    FRA_SUPPLEMENT_WORK_OUTCOMES = "Supplemental Work Outcomes"

    @classmethod
    def is_fra(cls, section):
        """Return whether a section belongs to FRA."""
        return section in {
            cls.FRA_WORK_OUTCOME_TANF_EXITERS,
            cls.FRA_SECONDRY_SCHOOL_ATTAINMENT,
            cls.FRA_SUPPLEMENT_WORK_OUTCOMES,
        }
