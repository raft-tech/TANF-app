# Prepared resolution for #5987

This package merges develop `2aef3173da19f9848716cea055fa4a8a52eecaca` into feature
head `43b37ca1e` and resolves all 15 conflicted files. The application checkout has
not been modified, committed, or pushed.

The resolution combines develop's persistent transition history with the
feature branch's lifecycle controller, ownership fencing, timeout handling,
reparse recovery, and notification-failure handling. Audit event IDs remain
separate from ownership tokens in Python and Go task arguments. A new migration
joins both `0032` migrations. Production Go state writes remain prohibited;
shadow state changes retain their separate audit history.

`review.patch` shows the complete result relative to the feature head, including
develop's automatically merged files. `files/` contains the resulting files;
`manifest.json` pins their hashes and both merge parents.

## Apply

From the repository, run:

```sh
python3 .merge-resolution-5987/apply.py
```

The helper requires the original branch and head, a clean checkout (except this
package), and no active merge. It starts the merge, checks that the conflicts
match the reviewed preview, copies the prepared files, and stages the resolution.
It does not commit or push. Do not add this package itself to the commit.

## Validation

Completed:

- The full Go package suite passed with three port-binding tests excluded:
  `go test -count=1 ./... -skip 'TestStartServerExposesMetricsEndpoint|TestStartServerExposesLocalServerModeMetrics|TestMetricsServerStartExposesConfiguredServerMode'`.
- `go vet ./...` passed.
- All 597 backend Python modules parsed under Python 3.14; static symbol checks
  found no undefined global references.
- The data_files migration graph has one leaf joining both migration branches.
- No conflict markers remain. `git apply --check review.patch` passed against the
  original feature checkout.

Not completed:

- Django tests, Django migration execution, and flake8: Docker access was denied;
  automatic approval review rejected execution of existing backend virtual
  environments and creation of a temporary lint environment without a detailed
  reason.
- Three Go tests require a local listening socket, which this session prohibited.
- Go PostgreSQL tests skipped because `TEST_DATABASE_URL` was unset.
- Browser and live Django/Go integration tests were not run.

Before committing, run from the repository in your normal development environment:

```sh
task backend-lint
task backend-pytest PYTEST_ARGS="tdpservice/data_files/test tdpservice/scheduling/test/test_parser_task.py tdpservice/search_indexes/test/test_reparse.py tdpservice/search_indexes/test/test_reparse_command.py tdpservice/core/test/test_models.py tdpservice/etl/test/test_load_statistical_weights_test_data.py"
task backend-pytest-go-integration
git commit
```

The existing browser lifecycle scenarios are unchanged. Run the normal CI checks
before merging the pull request.
