package celery

import (
	"context"
	"fmt"
	"go-parser/internal/config"
	"go-parser/internal/pipeline"
	"go-parser/internal/server"
	"strings"
	"testing"

	"github.com/gocelery/gocelery"
)

type fakeTaskSender struct {
	calls []fakeTaskCall
	err   error
}

type fakeTaskCall struct {
	task string
	args []interface{}
}

func (f *fakeTaskSender) Delay(task string, args ...interface{}) (*gocelery.AsyncResult, error) {
	f.calls = append(f.calls, fakeTaskCall{task: task, args: args})
	return nil, f.err
}

func TestSectionNumber(t *testing.T) {
	tests := []struct {
		name    string
		section string
		want    int
	}{
		{"Active Case Data", "Active Case Data", 1},
		{"Closed Case Data", "Closed Case Data", 2},
		{"Aggregate Data", "Aggregate Data", 3},
		{"Stratum Data", "Stratum Data", 4},
		{"unknown section", "Not A Real Section", 0},
		{"empty string", "", 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := sectionNumber(tt.section)
			if got != tt.want {
				t.Errorf("sectionNumber(%q) = %d, want %d", tt.section, got, tt.want)
			}
		})
	}
}

func TestRun_MissingRedisURL(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Server.Celery.RedisURL = ""

	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}

	err := s.Run(context.Background())
	if err == nil {
		t.Fatal("expected error for missing redis URL")
	}
	if !strings.Contains(err.Error(), "server.celery.redis_url") {
		t.Errorf("error = %q, should mention server.celery.redis_url", err.Error())
	}
}

func TestRecordTotalsForResult(t *testing.T) {
	result := &pipeline.ParsingResult{
		RecordCounts: map[string]int64{
			"shadow_search_indexes_tanf_t1": 5,
			"shadow_search_indexes_tanf_t2": 7,
			"parser_error":                  3,
		},
		DetailRecordCount: 15,
		ErrorCount:        3,
	}

	created, total := recordTotalsForResult(result)
	if created != 12 {
		t.Errorf("created = %d, want 12", created)
	}
	if total != 15 {
		t.Errorf("total = %d, want 15", total)
	}
}

func TestParseModeSelectsTablePrefix(t *testing.T) {
	tests := []struct {
		value      string
		wantPrefix string
	}{
		{value: "shadow", wantPrefix: "shadow_"},
		{value: "production", wantPrefix: ""},
	}

	for _, tt := range tests {
		t.Run(tt.value, func(t *testing.T) {
			mode, err := parseMode(tt.value)
			if err != nil {
				t.Fatalf("parseMode() error = %v", err)
			}
			got, err := mode.tablePrefix("shadow_")
			if err != nil {
				t.Fatalf("tablePrefix() error = %v", err)
			}
			if got != tt.wantPrefix {
				t.Errorf("tablePrefix() = %q, want %q", got, tt.wantPrefix)
			}
		})
	}
}

func TestParseModeRejectsUnknownMode(t *testing.T) {
	if _, err := parseMode("disabled"); err == nil {
		t.Fatal("parseMode() error = nil, want unsupported mode error")
	}
}

func TestShadowModeRejectsEmptyTablePrefix(t *testing.T) {
	if _, err := parserModeShadow.tablePrefix(""); err == nil {
		t.Fatal("tablePrefix() error = nil, want missing shadow prefix error")
	}
}

func TestEnqueuePostParseTask(t *testing.T) {
	cfg := config.DefaultConfig()
	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}
	sender := &fakeTaskSender{}

	if err := s.enqueuePostParseTask(sender, 42, 7, "pipeline failed", parserModeProduction); err != nil {
		t.Fatalf("enqueuePostParseTask() error = %v", err)
	}

	if len(sender.calls) != 1 {
		t.Fatalf("calls = %d, want 1", len(sender.calls))
	}
	call := sender.calls[0]
	if call.task != "tdpservice.scheduling.parser_task.post_parse" {
		t.Errorf("task = %q", call.task)
	}
	wantArgs := []interface{}{int32(42), int32(7), "pipeline failed", "production"}
	for i, want := range wantArgs {
		if call.args[i] != want {
			t.Errorf("arg %d = %#v, want %#v", i, call.args[i], want)
		}
	}
}

func TestEnqueuePostParseTaskUsesNilParseError(t *testing.T) {
	cfg := config.DefaultConfig()
	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}
	sender := &fakeTaskSender{}

	if err := s.enqueuePostParseTask(sender, 42, 0, "", parserModeShadow); err != nil {
		t.Fatalf("enqueuePostParseTask() error = %v", err)
	}

	if got := sender.calls[0].args[2]; got != nil {
		t.Errorf("parse error arg = %#v, want nil", got)
	}
	if got := sender.calls[0].args[3]; got != "shadow" {
		t.Errorf("table mode arg = %#v, want shadow", got)
	}
}

func TestEnqueuePostParseTaskSurfacesDelayError(t *testing.T) {
	cfg := config.DefaultConfig()
	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}
	sender := &fakeTaskSender{err: fmt.Errorf("redis down")}

	err := s.enqueuePostParseTask(sender, 42, 0, "", parserModeShadow)

	if err == nil || !strings.Contains(err.Error(), "redis down") {
		t.Fatalf("error = %v, want redis down", err)
	}
}
