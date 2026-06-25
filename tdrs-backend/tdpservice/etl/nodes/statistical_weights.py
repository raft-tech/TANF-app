"""TANF statistical weights ETL node implementations."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import Count, F, Max, OuterRef, Subquery, Sum
from django.utils import timezone

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.etl.models import (
    ETLIntermediateOutput,
    ETLOutput,
    ETLQAResult,
    StatisticalWeight,
)
from tdpservice.etl.notifications import send_statistical_weights_notification
from tdpservice.etl.registry import NodeResult
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T6, TANF_T7
from tdpservice.stts.models import STT

PROGRAM = "TANF"
DATAFILE_PROGRAM = DataFile.ProgramType.TANF
SECTION = "1"
WEIGHT_OUTPUT_KEY = "statistical_weights"
SOURCE_DATAFILE_IDS_KEY = "source_datafile_ids"
T1_SOURCE_KEY = "t1"
T6_SOURCE_KEY = "t6"
T7_SOURCE_KEY = "t7"
S1_OUTPUT_KEY = "weights.s1"
S3_OUTPUT_KEY = "weights.s3"
S4_OUTPUT_KEY = "weights.s4"
WEIGHT_CANDIDATES_KEY = "statistical_weights.candidates"


@dataclass(frozen=True)
class WeightCandidate:
    """Computed statistical weight candidate row."""

    fiscal_year: int
    reporting_month: int
    program: str
    section: str
    stt_code: str
    stratum: str
    case_count: int
    cases: int
    weight: Decimal


def _fiscal_year(context) -> int:
    """Return the fiscal year parameter."""
    return int(context.parameters["fiscal_year"])


def _normalize_code(value) -> str:
    """Normalize STT and stratum codes for joins with legacy integer SQL."""
    if value is None:
        return ""

    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value).strip()


def _latest_datafile_ids(fiscal_year: int, section: str) -> list[int]:
    """Return latest accepted DataFile ids by STT and quarter for a section."""
    accepted_files = DataFile.objects.filter(
        year=fiscal_year,
        program_type=DATAFILE_PROGRAM,
        section=section,
        is_program_audit=False,
        state=SubmissionState.PARSE_COMPLETED,
    )

    latest_version = (
        DataFile.objects.filter(
            year=fiscal_year,
            program_type=DATAFILE_PROGRAM,
            section=section,
            is_program_audit=False,
            state=SubmissionState.PARSE_COMPLETED,
            stt_id=OuterRef("stt_id"),
            quarter=OuterRef("quarter"),
        )
        .order_by("-version")
        .values("version")[:1]
    )

    return list(
        accepted_files.annotate(latest_version=Subquery(latest_version))
        .filter(version=F("latest_version"))
        .values_list("id", flat=True)
    )


def _snapshot_source_datafile_ids(fiscal_year: int) -> dict[str, list[int]]:
    """Return the source DataFile snapshot for one weights run."""
    # If an STT submits a file during a run, later nodes should not pick it up.
    return {
        T1_SOURCE_KEY: _latest_datafile_ids(
            fiscal_year, DataFile.Section.ACTIVE_CASE_DATA
        ),
        T6_SOURCE_KEY: _latest_datafile_ids(
            fiscal_year, DataFile.Section.AGGREGATE_DATA
        ),
        T7_SOURCE_KEY: _latest_datafile_ids(fiscal_year, DataFile.Section.STRATUM_DATA),
    }


def _source_datafile_ids(context) -> dict[str, list[int]]:
    """Return a run's source DataFile snapshot, creating it once when needed."""
    metadata = dict(context.pipeline_run.metadata or {})
    source_ids = metadata.get(SOURCE_DATAFILE_IDS_KEY)
    if source_ids:
        return {
            T1_SOURCE_KEY: [int(value) for value in source_ids.get(T1_SOURCE_KEY, [])],
            T6_SOURCE_KEY: [int(value) for value in source_ids.get(T6_SOURCE_KEY, [])],
            T7_SOURCE_KEY: [int(value) for value in source_ids.get(T7_SOURCE_KEY, [])],
        }

    source_ids = _snapshot_source_datafile_ids(_fiscal_year(context))
    metadata[SOURCE_DATAFILE_IDS_KEY] = source_ids
    context.pipeline_run.metadata = metadata
    context.pipeline_run.save(update_fields=["metadata", "updated_at"])
    return source_ids


def _write_intermediate_output(pipeline_run, output_key: str, payload: list[dict]):
    """Persist a run-scoped intermediate output payload."""
    return ETLIntermediateOutput.objects.update_or_create(
        pipeline_run=pipeline_run,
        output_key=output_key,
        defaults={
            "payload": payload,
            "row_count": len(payload),
        },
    )[0]


def _intermediate_payload(context, output_key: str) -> list[dict]:
    """Return a declared intermediate output payload."""
    return context.intermediate_outputs[output_key].payload


def _candidate_payload(candidates: list[WeightCandidate]) -> list[dict]:
    """Return candidates as a JSON-stable payload."""
    return [
        {
            "fiscal_year": candidate.fiscal_year,
            "reporting_month": candidate.reporting_month,
            "program": candidate.program,
            "section": candidate.section,
            "stt_code": candidate.stt_code,
            "stratum": candidate.stratum,
            "case_count": candidate.case_count,
            "cases": candidate.cases,
            "weight": str(candidate.weight),
        }
        for candidate in candidates
    ]


def _candidates_from_payload(payload: list[dict]) -> list[WeightCandidate]:
    """Return candidate dataclasses from a JSON-stable payload."""
    return [
        WeightCandidate(
            fiscal_year=int(row["fiscal_year"]),
            reporting_month=int(row["reporting_month"]),
            program=row["program"],
            section=row["section"],
            stt_code=row["stt_code"],
            stratum=row["stratum"],
            case_count=int(row["case_count"]),
            cases=int(row["cases"]),
            weight=Decimal(str(row["weight"])),
        )
        for row in payload
    ]


def _t1_queryset(datafile_ids: list[int]):
    """Return TANF T1 rows in scope."""
    return TANF_T1.objects.filter(datafile_id__in=datafile_ids)


def _t6_queryset(datafile_ids: list[int]):
    """Return TANF T6 rows in scope."""
    return TANF_T6.objects.filter(datafile_id__in=datafile_ids)


def _t7_queryset(datafile_ids: list[int]):
    """Return TANF T7 rows in scope."""
    return TANF_T7.objects.filter(datafile_id__in=datafile_ids)


def t1_family_counts(datafile_ids: list[int]) -> list[dict]:
    """Build s1: unique families by STT, reporting month, and stratum."""
    rows = (
        _t1_queryset(datafile_ids)
        .values("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
        .annotate(case_count=Count("CASE_NUMBER", distinct=True))
        .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
    )
    return [
        {
            "stt_code": _normalize_code(row["datafile__stt__stt_code"]),
            "reporting_month": row["RPT_MONTH_YEAR"],
            "stratum": _normalize_code(row["STRATUM"]),
            "case_count": int(row["case_count"] or 0),
        }
        for row in rows
    ]


def t6_case_counts(datafile_ids: list[int]) -> list[dict]:
    """Build s3: aggregate cases by STT and reporting month."""
    rows = (
        _t6_queryset(datafile_ids)
        .values("datafile__stt__stt_code", "RPT_MONTH_YEAR")
        .annotate(case_count=Sum("NUM_FAMILIES"))
        .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR")
    )
    return [
        {
            "stt_code": _normalize_code(row["datafile__stt__stt_code"]),
            "reporting_month": row["RPT_MONTH_YEAR"],
            "case_count": int(row["case_count"] or 0),
        }
        for row in rows
    ]


def t7_section_case_counts(datafile_ids: list[int]) -> list[dict]:
    """Build s4: stratum cases by STT, reporting month, and stratum."""
    rows = (
        _t7_queryset(datafile_ids)
        .filter(TDRS_SECTION_IND=SECTION, FAMILIES_MONTH__gt=0)
        .values("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
        .annotate(cases=Sum("FAMILIES_MONTH"))
        .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
    )
    return [
        {
            "stt_code": _normalize_code(row["datafile__stt__stt_code"]),
            "reporting_month": row["RPT_MONTH_YEAR"],
            "stratum": _normalize_code(row["STRATUM"]),
            "cases": int(row["cases"] or 0),
        }
        for row in rows
    ]


def build_candidates(
    fiscal_year: int,
    s1_rows: list[dict],
    s3_rows: list[dict],
    s4_rows: list[dict],
) -> list[WeightCandidate]:
    """Build final statistical weight candidates."""
    s3_cases_by_pair = {
        (row["stt_code"], row["reporting_month"]): row["case_count"] for row in s3_rows
    }
    s4_cases_by_stratum = {
        (row["stt_code"], row["reporting_month"], row["stratum"]): row["cases"]
        for row in s4_rows
    }

    candidates: list[WeightCandidate] = []
    for row in s1_rows:
        case_count = row["case_count"]
        if case_count <= 0:
            continue

        s4_cases = s4_cases_by_stratum.get(
            (row["stt_code"], row["reporting_month"], row["stratum"])
        )
        s3_cases = s3_cases_by_pair.get((row["stt_code"], row["reporting_month"]))
        source_cases = s4_cases if s4_cases is not None else s3_cases
        if not source_cases:
            continue

        cases = max(case_count, int(source_cases))
        if cases <= 0:
            continue

        weight = (Decimal(cases) / Decimal(case_count)).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        candidates.append(
            WeightCandidate(
                fiscal_year=fiscal_year,
                reporting_month=row["reporting_month"],
                program=PROGRAM,
                section=SECTION,
                stt_code=row["stt_code"],
                stratum=row["stratum"],
                case_count=case_count,
                cases=cases,
                weight=weight,
            )
        )

    return candidates


def validate_parameters(context) -> NodeResult:
    """Validate statistical-weights parameters."""
    fiscal_year = _fiscal_year(context)
    if fiscal_year < 2000:
        raise ValueError("fiscal_year must be 2000 or later.")

    source_ids = _source_datafile_ids(context)
    return NodeResult(
        metadata={
            "fiscal_year": fiscal_year,
            SOURCE_DATAFILE_IDS_KEY: source_ids,
        }
    )


def extract_t1_family_counts(context) -> NodeResult:
    """Build and count s1 rows."""
    datafile_ids = _source_datafile_ids(context)[T1_SOURCE_KEY]
    source_count = _t1_queryset(datafile_ids).count()
    rows = t1_family_counts(datafile_ids)
    _write_intermediate_output(context.pipeline_run, S1_OUTPUT_KEY, rows)
    return NodeResult(
        input_row_count=source_count,
        output_row_count=len(rows),
        metadata={"dataset": "s1", "source_datafile_ids": datafile_ids},
    )


def extract_t6_case_counts(context) -> NodeResult:
    """Build and count s3 rows."""
    datafile_ids = _source_datafile_ids(context)[T6_SOURCE_KEY]
    source_count = _t6_queryset(datafile_ids).count()
    rows = t6_case_counts(datafile_ids)
    _write_intermediate_output(context.pipeline_run, S3_OUTPUT_KEY, rows)
    return NodeResult(
        input_row_count=source_count,
        output_row_count=len(rows),
        metadata={"dataset": "s3", "source_datafile_ids": datafile_ids},
    )


def extract_t7_section_case_counts(context) -> NodeResult:
    """Build and count s4 rows."""
    datafile_ids = _source_datafile_ids(context)[T7_SOURCE_KEY]
    source_count = _t7_queryset(datafile_ids).count()
    rows = t7_section_case_counts(datafile_ids)
    _write_intermediate_output(context.pipeline_run, S4_OUTPUT_KEY, rows)
    return NodeResult(
        input_row_count=source_count,
        output_row_count=len(rows),
        metadata={"dataset": "s4", "source_datafile_ids": datafile_ids},
    )


def build_weight_candidates(context) -> NodeResult:
    """Build candidate statistical weight rows."""
    candidates = build_candidates(
        _fiscal_year(context),
        _intermediate_payload(context, S1_OUTPUT_KEY),
        _intermediate_payload(context, S3_OUTPUT_KEY),
        _intermediate_payload(context, S4_OUTPUT_KEY),
    )
    _write_intermediate_output(
        context.pipeline_run,
        WEIGHT_CANDIDATES_KEY,
        _candidate_payload(candidates),
    )
    return NodeResult(
        output_row_count=len(candidates),
        metadata={"candidate_count": len(candidates)},
    )


def _review_month(*datasets: list[dict]) -> int | None:
    """Return the highest reporting month present in QA datasets."""
    reporting_months = [
        row["reporting_month"]
        for dataset in datasets
        for row in dataset
        if row.get("reporting_month")
    ]
    return max(reporting_months) if reporting_months else None


def _numeric_stt_codes(queryset) -> set[int]:
    """Return numeric STT codes from an STT queryset."""
    codes = (
        queryset.exclude(stt_code__isnull=True)
        .exclude(stt_code="")
        .values_list("stt_code", flat=True)
    )
    return {int(code) for code in codes if str(code).isdigit()}


def _required_stt_codes() -> set[int]:
    """Return TANF state and territory STT codes expected in T1/T6 QA."""
    return _numeric_stt_codes(
        STT.objects.filter(
            type__in=[
                STT.EntityType.STATE,
                STT.EntityType.TERRITORY,
            ]
        )
    )


def _sample_stt_codes() -> set[int]:
    """Return sample STT codes as integers."""
    return _numeric_stt_codes(STT.objects.filter(sample=True))


def _create_qa_result(
    pipeline_run, check_key, status, summary, payload, blocking=False
):
    """Persist one QA result."""
    return ETLQAResult.objects.create(
        pipeline_run=pipeline_run,
        check_key=check_key,
        status=status,
        summary=summary,
        result_payload=payload,
        blocking=blocking,
    )


def _tuple_payload(values: list[tuple]) -> list[list]:
    """Convert tuple sets to JSON-stable list payloads."""
    return [list(value) for value in values]


def run_weights_qa(context) -> NodeResult:
    """Persist statistical weights QA results."""
    s1_rows = _intermediate_payload(context, S1_OUTPUT_KEY)
    s3_rows = _intermediate_payload(context, S3_OUTPUT_KEY)
    s4_rows = _intermediate_payload(context, S4_OUTPUT_KEY)
    candidates = _candidates_from_payload(
        _intermediate_payload(context, WEIGHT_CANDIDATES_KEY)
    )
    review_month = _review_month(s1_rows, s3_rows, s4_rows)

    ETLQAResult.objects.filter(pipeline_run=context.pipeline_run).delete()

    row_count_payload = {
        "s1": len(s1_rows),
        "s3": len(s3_rows),
        "s4": len(s4_rows),
        "candidate_output": len(candidates),
    }
    _create_qa_result(
        context.pipeline_run,
        "weights_row_counts",
        ETLQAResult.Status.PASSED,
        "Captured statistical weights row counts.",
        row_count_payload,
    )

    if review_month:
        s1_present = {
            int(row["stt_code"])
            for row in s1_rows
            if row["reporting_month"] == review_month and row["stt_code"].isdigit()
        }
        s3_present = {
            int(row["stt_code"])
            for row in s3_rows
            if row["reporting_month"] == review_month and row["stt_code"].isdigit()
        }
        s4_present = {
            int(row["stt_code"])
            for row in s4_rows
            if row["reporting_month"] == review_month and row["stt_code"].isdigit()
        }
    else:
        s1_present = set()
        s3_present = set()
        s4_present = set()

    required_codes = _required_stt_codes()
    sample_codes = _sample_stt_codes()
    missing_payload = {
        "review_month": review_month,
        "s1_missing": sorted(required_codes - s1_present),
        "s3_missing": sorted(required_codes - s3_present),
        "s4_missing": sorted(sample_codes - s4_present),
    }
    missing_count = sum(
        len(values) for values in missing_payload.values() if isinstance(values, list)
    )
    _create_qa_result(
        context.pipeline_run,
        "weights_missing_stts",
        ETLQAResult.Status.WARNING if missing_count else ETLQAResult.Status.PASSED,
        f"Found {missing_count} missing STT entries for review month.",
        missing_payload,
    )

    s1_pairs = {(row["stt_code"], row["reporting_month"]) for row in s1_rows}
    s3_pairs = {(row["stt_code"], row["reporting_month"]) for row in s3_rows}
    pair_mismatches = sorted(s1_pairs.symmetric_difference(s3_pairs))
    _create_qa_result(
        context.pipeline_run,
        "weights_t1_t6_pair_mismatch",
        ETLQAResult.Status.WARNING if pair_mismatches else ETLQAResult.Status.PASSED,
        f"Found {len(pair_mismatches)} T1/T6 pair mismatches.",
        {"mismatches": _tuple_payload(pair_mismatches)},
    )

    sample_code_strings = {str(code) for code in sample_codes}
    s1_strata = {
        (row["stt_code"], row["reporting_month"], row["stratum"])
        for row in s1_rows
        if row["stt_code"] in sample_code_strings
    }
    s4_strata = {
        (row["stt_code"], row["reporting_month"], row["stratum"])
        for row in s4_rows
        if row["stt_code"] in sample_code_strings
    }
    stratum_mismatches = sorted(s1_strata.symmetric_difference(s4_strata))
    _create_qa_result(
        context.pipeline_run,
        "weights_t1_t7_stratum_mismatch",
        ETLQAResult.Status.WARNING if stratum_mismatches else ETLQAResult.Status.PASSED,
        f"Found {len(stratum_mismatches)} T1/T7 stratum mismatches.",
        {"mismatches": _tuple_payload(stratum_mismatches)},
    )

    return NodeResult(output_row_count=4, metadata={"review_month": review_month})


def _scope_filter(fiscal_year: int) -> dict:
    """Return the StatisticalWeight filter for a fiscal-year output scope."""
    return {"fiscal_year": fiscal_year, "program": PROGRAM, "section": SECTION}


def publish_weights(context) -> NodeResult:
    """Publish a new immutable statistical weights version."""
    blocking_failure_exists = ETLQAResult.objects.filter(
        pipeline_run=context.pipeline_run,
        blocking=True,
        status=ETLQAResult.Status.FAILED,
    ).exists()
    if blocking_failure_exists:
        raise ValueError(
            "Blocking QA failure prevents statistical weights publication."
        )

    fiscal_year = _fiscal_year(context)
    candidates = _candidates_from_payload(
        _intermediate_payload(context, WEIGHT_CANDIDATES_KEY)
    )
    now = timezone.now()
    retention_expires_at = now + timedelta(days=31)

    with transaction.atomic():
        existing_rows = StatisticalWeight.objects.select_for_update().filter(
            **_scope_filter(fiscal_year)
        )
        current_version = existing_rows.aggregate(latest=Max("version"))["latest"] or 0
        next_version = current_version + 1

        if current_version:
            existing_rows.filter(
                version=current_version, retention_expires_at__isnull=True
            ).update(retention_expires_at=retention_expires_at)

        StatisticalWeight.objects.bulk_create(
            [
                StatisticalWeight(
                    fiscal_year=candidate.fiscal_year,
                    reporting_month=candidate.reporting_month,
                    program=candidate.program,
                    section=candidate.section,
                    stt_code=candidate.stt_code,
                    stratum=candidate.stratum,
                    version=next_version,
                    case_count=candidate.case_count,
                    cases=candidate.cases,
                    weight=candidate.weight,
                    pipeline_run=context.pipeline_run,
                    published_at=now,
                )
                for candidate in candidates
            ]
        )
        ETLOutput.objects.create(
            pipeline_run=context.pipeline_run,
            output_key=WEIGHT_OUTPUT_KEY,
            output_kind=ETLOutput.OutputKind.TABLE,
            reference=StatisticalWeight._meta.db_table,
            output_version=next_version,
            row_count=len(candidates),
            published=True,
            metadata=context.output_scope,
        )

    return NodeResult(
        output_row_count=len(candidates),
        metadata={"version": next_version, "row_count": len(candidates)},
    )


def notify_weights_run(context) -> NodeResult:
    """Notify operational users that a statistical weights run completed."""
    return NodeResult(
        metadata=send_statistical_weights_notification(context.pipeline_run)
    )
