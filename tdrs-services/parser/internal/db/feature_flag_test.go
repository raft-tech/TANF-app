package db

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5"
)

type fakeFeatureFlagQuerier struct {
	enabled bool
	err     error
	name    string
}

func (q *fakeFeatureFlagQuerier) QueryRow(_ context.Context, _ string, args ...any) pgx.Row {
	q.name = args[0].(string)
	return fakeFeatureFlagRow{enabled: q.enabled, err: q.err}
}

type fakeFeatureFlagRow struct {
	enabled bool
	err     error
}

func (r fakeFeatureFlagRow) Scan(dest ...any) error {
	if r.err != nil {
		return r.err
	}
	*(dest[0].(*bool)) = r.enabled
	return nil
}

func TestFeatureFlagEnabled(t *testing.T) {
	tests := []struct {
		name    string
		enabled bool
		err     error
		want    bool
	}{
		{name: "enabled", enabled: true, want: true},
		{name: "disabled", enabled: false, want: false},
		{name: "missing", err: pgx.ErrNoRows, want: false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			querier := &fakeFeatureFlagQuerier{enabled: tt.enabled, err: tt.err}
			got, err := FeatureFlagEnabled(context.Background(), querier, "go_parser_shadow_mode")
			if err != nil {
				t.Fatalf("FeatureFlagEnabled() unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("FeatureFlagEnabled() = %v, want %v", got, tt.want)
			}
			if querier.name != "go_parser_shadow_mode" {
				t.Errorf("feature name = %q, want go_parser_shadow_mode", querier.name)
			}
		})
	}
}

func TestFeatureFlagEnabledReturnsQueryError(t *testing.T) {
	querier := &fakeFeatureFlagQuerier{err: errors.New("database unavailable")}

	_, err := FeatureFlagEnabled(context.Background(), querier, "go_parser_shadow_mode")

	if err == nil || !strings.Contains(err.Error(), "database unavailable") {
		t.Fatalf("error = %v, want database unavailable", err)
	}
}
