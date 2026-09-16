"""Generate test data for Data files."""

import factory

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import Program, Section
from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.test.factories import UserFactory


CANONICAL_PROGRAMS = {
    "TAN": {"slug": "tanf", "name": "TANF"},
    "SSP": {"slug": "ssp", "name": "SSP"},
    "TRIBAL": {"slug": "tribal", "name": "Tribal TANF"},
    "FRA": {"slug": "fra", "name": "FRA"},
}


def canonical_section_for(program_code, section_name):
    """Create canonical program/section rows if a transactional test flushed them."""
    program_data = CANONICAL_PROGRAMS[program_code]
    program, _ = Program.objects.update_or_create(
        code=program_code,
        defaults={
            "slug": program_data["slug"],
            "name": program_data["name"],
        },
    )
    section, _ = Section.objects.get_or_create(
        program=program,
        name=section_name,
    )
    return section


class DataFileFactory(factory.django.DjangoModelFactory):
    """Generate test data for data files."""

    class Meta:
        """Hardcoded meta data for data files."""

        model = "data_files.DataFile"

    original_filename = "data_file.txt"
    slug = "data_file-txt-slug"
    extension = "txt"
    section = "Active Case Data"
    program_type = "TAN"
    quarter = "Q1"
    year = 2020
    version = 1
    state = SubmissionState.UPLOADED
    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)
    file = factory.django.FileField(data=b"test", filename="my_data_file.txt")
    s3_versioning_id = 0

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Build with an unsaved canonical relation without querying the database."""
        program_code = kwargs.pop("program_type")
        section = kwargs["section"]
        if not isinstance(section, Section):
            program = Program(code=program_code, **CANONICAL_PROGRAMS[program_code])
            kwargs["section"] = Section(program=program, name=section)
        return super()._build(model_class, *args, **kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create with a persisted canonical relation."""
        program_code = kwargs.pop("program_type")
        section = kwargs["section"]
        if not isinstance(section, Section):
            kwargs["section"] = canonical_section_for(program_code, section)
        return super()._create(model_class, *args, **kwargs)
