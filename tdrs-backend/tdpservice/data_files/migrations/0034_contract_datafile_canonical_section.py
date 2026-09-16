import django.db.models.deletion
from django.db import migrations, models


CANONICAL_SECTIONS = {
    "TAN": {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    },
    "SSP": {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    },
    "TRIBAL": {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    },
    "FRA": {
        "Work Outcomes of TANF Exiters",
        "Secondary School Attainment",
        "Supplemental Work Outcomes",
    },
}

GENERATED_GRAFANA_VIEWS = {
    f"{prefix}{program}_{section}"
    for prefix in ("", "admin_")
    for program, sections in {
        "ssp": ("m1", "m2", "m3", "m4", "m5", "m6", "m7"),
        "tanf": ("t1", "t2", "t3", "t4", "t5", "t6", "t7"),
        "tribal_tanf": ("t1", "t2", "t3", "t4", "t5", "t6", "t7"),
    }.items()
    for section in sections
}
KNOWN_DEPENDENT_VIEWS = GENERATED_GRAFANA_VIEWS | {
    "latest_tanf_exiters_view_prod",
    "mr_record_counts_by_tableview",
    "stt_section_to_type_mapping",
}


def _examples(queryset, *fields):
    return list(queryset.values_list(*fields)[:10])


def validate_datafiles(apps, schema_editor):
    """Reject classification drift before removing the legacy columns."""
    DataFile = apps.get_model("data_files", "DataFile")
    schema_editor.execute("LOCK TABLE data_files_datafile IN ACCESS EXCLUSIVE MODE")

    failures = []
    null_sections = DataFile.objects.filter(section_ref_id__isnull=True)
    if null_sections.exists():
        failures.append(
            f"null section_ref: count={null_sections.count()}, "
            f"example_ids={_examples(null_sections, 'id')}"
        )

    mismatches = DataFile.objects.exclude(
        program_type=models.F("section_ref__program__code"),
        section=models.F("section_ref__name"),
    )
    if mismatches.exists():
        failures.append(
            f"legacy/canonical mismatch: count={mismatches.count()}, "
            f"examples={_examples(mismatches, 'id', 'program_type', 'section')}"
        )

    canonical_pairs = [
        models.Q(section_ref__program__code=program, section_ref__name=section)
        for program, sections in CANONICAL_SECTIONS.items()
        for section in sections
    ]
    canonical_filter = canonical_pairs[0]
    for pair_filter in canonical_pairs[1:]:
        canonical_filter |= pair_filter
    noncanonical = DataFile.objects.exclude(canonical_filter)
    if noncanonical.exists():
        failures.append(
            f"noncanonical section: count={noncanonical.count()}, "
            f"examples={_examples(noncanonical, 'id', 'section_ref_id')}"
        )

    invalid_audits = DataFile.objects.filter(
        is_program_audit=True,
        section_ref__program__code__in=("SSP", "FRA"),
    )
    if invalid_audits.exists():
        failures.append(
            f"invalid program audit: count={invalid_audits.count()}, "
            f"examples={_examples(invalid_audits, 'id', 'program_type')}"
        )

    duplicate_groups = (
        DataFile.objects.values(
            "section_ref_id",
            "version",
            "quarter",
            "year",
            "stt_id",
            "is_program_audit",
        )
        .annotate(row_count=models.Count("id"))
        .filter(row_count__gt=1)
    )
    if duplicate_groups.exists():
        failures.append(
            f"canonical duplicates: count={duplicate_groups.count()}, "
            f"examples={list(duplicate_groups[:10])}"
        )

    if failures:
        raise RuntimeError("Cannot contract DataFile classification: " + "; ".join(failures))


def drop_known_dependent_views(apps, schema_editor):
    """Drop allowlisted views that transitively depend on legacy columns."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            WITH RECURSIVE dependent_views AS (
                SELECT dependent.oid, dependent.relnamespace, dependent.relname,
                    dependent.relkind, 0 AS depth
                FROM pg_depend dependency
                INNER JOIN pg_rewrite rewrite ON rewrite.oid = dependency.objid
                INNER JOIN pg_class dependent ON dependent.oid = rewrite.ev_class
                INNER JOIN pg_attribute referenced_attribute
                    ON referenced_attribute.attrelid = dependency.refobjid
                    AND referenced_attribute.attnum = dependency.refobjsubid
                WHERE dependency.refobjid = 'data_files_datafile'::regclass
                    AND referenced_attribute.attname IN ('section', 'program_type')
                    AND dependent.relkind IN ('v', 'm')
                UNION ALL
                SELECT downstream.oid, downstream.relnamespace, downstream.relname,
                    downstream.relkind, upstream.depth + 1
                FROM dependent_views upstream
                INNER JOIN pg_depend dependency ON dependency.refobjid = upstream.oid
                INNER JOIN pg_rewrite rewrite ON rewrite.oid = dependency.objid
                INNER JOIN pg_class downstream ON downstream.oid = rewrite.ev_class
                WHERE downstream.relkind IN ('v', 'm')
                    AND downstream.oid != upstream.oid
            )
            SELECT namespace.nspname, view_name.relname, view_name.relkind,
                MAX(view_name.depth)
            FROM dependent_views view_name
            INNER JOIN pg_namespace namespace ON namespace.oid = view_name.relnamespace
            GROUP BY namespace.nspname, view_name.relname, view_name.relkind
            ORDER BY MAX(view_name.depth) DESC
            """
        )
        dependent_views = cursor.fetchall()

    unknown_views = sorted(
        f"{schema}.{name}"
        for schema, name, _kind, _depth in dependent_views
        if schema != "public" or name not in KNOWN_DEPENDENT_VIEWS
    )
    if unknown_views:
        raise RuntimeError(
            "Cannot remove legacy DataFile columns; unknown dependent views: "
            f"{unknown_views}"
        )

    quote = schema_editor.connection.ops.quote_name
    for schema, name, kind, _depth in dependent_views:
        object_type = "MATERIALIZED VIEW" if kind == "m" else "VIEW"
        schema_editor.execute(
            f"DROP {object_type} IF EXISTS {quote(schema)}.{quote(name)}"
        )


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("data_files", "0033_alter_shadowdatafile_file_and_more"),
    ]

    operations = [
        migrations.RunPython(validate_datafiles, migrations.RunPython.noop),
        migrations.RunPython(drop_known_dependent_views, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="datafile",
            constraint=models.UniqueConstraint(
                fields=(
                    "section_ref",
                    "version",
                    "quarter",
                    "year",
                    "stt",
                    "is_program_audit",
                ),
                name="datafile_uniq_section_version_period_stt_audit",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="datafile",
            name="constraint_name",
        ),
        migrations.AlterField(
            model_name="datafile",
            name="section_ref",
            field=models.ForeignKey(
                db_column="section_ref_id",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="data_files",
                to="data_files.section",
            ),
        ),
        migrations.RemoveField(model_name="datafile", name="program_type"),
        migrations.RemoveField(model_name="datafile", name="section"),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name="datafile",
                    old_name="section_ref",
                    new_name="section",
                ),
                migrations.RemoveConstraint(
                    model_name="datafile",
                    name="datafile_uniq_section_version_period_stt_audit",
                ),
                migrations.AddConstraint(
                    model_name="datafile",
                    constraint=models.UniqueConstraint(
                        fields=(
                            "section",
                            "version",
                            "quarter",
                            "year",
                            "stt",
                            "is_program_audit",
                        ),
                        name="datafile_uniq_section_version_period_stt_audit",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
