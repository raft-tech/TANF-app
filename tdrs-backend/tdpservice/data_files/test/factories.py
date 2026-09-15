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

    @staticmethod
    def _synchronize_classification(kwargs, section_ref):
        """Make the supplied canonical Section authoritative in factory output."""
        kwargs["section_ref"] = section_ref
        kwargs["program_type"] = section_ref.program.code
        kwargs["section"] = section_ref.name
        return kwargs

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Build with an unsaved canonical relation without querying the database."""
        section_ref = kwargs.get("section_ref")
        if section_ref is None:
            program_data = CANONICAL_PROGRAMS[kwargs["program_type"]]
            program = Program(code=kwargs["program_type"], **program_data)
            section_ref = Section(program=program, name=kwargs["section"])
        kwargs = cls._synchronize_classification(kwargs, section_ref)
        return super()._build(model_class, *args, **kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create with a persisted canonical relation."""
        section_ref = kwargs.get("section_ref")
        if section_ref is None:
            section_ref = canonical_section_for(
                kwargs["program_type"],
                kwargs["section"],
            )
        kwargs = cls._synchronize_classification(kwargs, section_ref)
        return super()._create(model_class, *args, **kwargs)
