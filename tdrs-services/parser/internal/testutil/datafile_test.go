package testutil

import (
	"strings"
	"testing"
)

func TestProductionDataFileInsertSynchronizesCanonicalAndScalarClassification(t *testing.T) {
	for _, fragment := range []string{
		"data_files_section AS section",
		"data_files_program AS program",
		"program.id = section.program_id",
		"section.name = $1 AND program.code = $2",
	} {
		if !strings.Contains(canonicalSectionIDQuery, fragment) {
			t.Errorf("canonical section lookup does not contain %q", fragment)
		}
	}

	query := productionDataFileInsert(`"data_files_datafile"`)
	for _, field := range []string{"section", "program_type", "section_ref_id"} {
		if !strings.Contains(query, field) {
			t.Errorf("production insert does not contain %q", field)
		}
	}
	if !strings.Contains(query, "$14") {
		t.Error("production insert does not bind section_ref_id")
	}
}

func TestShadowDataFileInsertRemainsScalar(t *testing.T) {
	query := shadowDataFileInsert(`"shadow_data_files_datafile"`)
	if !strings.Contains(query, "section") || !strings.Contains(query, "program_type") {
		t.Fatal("shadow insert does not contain scalar classification")
	}
	if strings.Contains(query, "section_ref_id") {
		t.Fatal("shadow insert unexpectedly contains section_ref_id")
	}
}
