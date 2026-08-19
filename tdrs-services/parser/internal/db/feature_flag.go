package db

import (
	"context"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
)

const selectFeatureFlagEnabled = `
	SELECT enabled
	FROM core_featureflag
	WHERE feature_name = $1
`

type rowQuerier interface {
	QueryRow(ctx context.Context, sql string, args ...any) pgx.Row
}

// FeatureFlagEnabled returns only the master enabled state for a feature flag.
// A missing flag is treated as disabled.
func FeatureFlagEnabled(ctx context.Context, querier rowQuerier, featureName string) (bool, error) {
	var enabled bool
	err := querier.QueryRow(ctx, selectFeatureFlagEnabled, featureName).Scan(&enabled)
	if errors.Is(err, pgx.ErrNoRows) {
		return false, nil
	}
	if err != nil {
		return false, fmt.Errorf("query feature flag %q: %w", featureName, err)
	}
	return enabled, nil
}
