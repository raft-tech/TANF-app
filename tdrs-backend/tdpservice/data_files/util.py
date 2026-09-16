"""Utility file for DataFiles."""


def get_datafile_classification(datafile):
    """Return parser metadata from the authoritative source for this table family."""
    if datafile._meta.db_table.startswith("shadow_"):
        return str(datafile.program_type), str(datafile.section)
    return datafile.section.program.code, datafile.section.name


def create_s3_log_file_path(datafile):
    """Create a unique S3 log file path per parse using the DataFile ID."""
    program_type, section = get_datafile_classification(datafile)
    return f"{datafile.year}/{datafile.quarter}/{datafile.stt}/{program_type}/{section}/{datafile.id}"


def create_legacy_s3_log_file_path(datafile):
    """Create the old-format S3 log path for backwards compatibility with pre-existing logs."""
    program_type, section = get_datafile_classification(datafile)
    key = f"{datafile.year}/{datafile.quarter}/{datafile.stt}/"
    if program_type in ["FRA", "TAN"]:
        key += section
    elif program_type == "TRIBAL":
        key += f"{program_type.title()} {section}"
    else:
        key += f"{program_type} {section}"
    return key
