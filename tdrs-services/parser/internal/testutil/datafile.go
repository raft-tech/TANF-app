package testutil

import (
	"context"
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
)

const canonicalSectionIDQuery = `
	SELECT section.id
	FROM data_files_section AS section
	JOIN data_files_program AS program ON program.id = section.program_id
	WHERE section.name = $1 AND program.code = $2
`

func dataFileTableNameFromEnv() string {
	if strings.EqualFold(os.Getenv("GO_PARSER_SHADOW_MODE"), "true") {
		return config.DataFileTableName(config.DefaultTablePrefix)
	}
	return config.DataFileTableName("")
}

// CreateTestDatafile creates a datafile record for testing purposes.
// It queries for an existing STT and user to satisfy foreign key constraints.
// Returns the created datafile ID.
func CreateTestDatafile(ctx context.Context, pool *pgxpool.Pool, quarter string, year int, sectionName string, programType string) (int32, error) {
	return CreateTestDatafileInTable(ctx, pool, dataFileTableNameFromEnv(), quarter, year, sectionName, programType)
}

// CreateTestDatafileInTable creates a datafile record in the specified table.
func CreateTestDatafileInTable(ctx context.Context, pool *pgxpool.Pool, tableName string, quarter string, year int, sectionName string, programType string) (int32, error) {
	productionTable := config.DataFileTableName("")
	shadowTable := config.DataFileTableName(config.DefaultTablePrefix)
	if tableName != productionTable && tableName != shadowTable {
		return 0, fmt.Errorf("unsupported datafile table %q", tableName)
	}
	sanitizedTableName := pgx.Identifier{tableName}.Sanitize()

	// Get an existing STT ID
	var sttID int
	err := pool.QueryRow(ctx, "SELECT id FROM stts_stt LIMIT 1").Scan(&sttID)
	if err != nil {
		return 0, fmt.Errorf("failed to get STT: %w (ensure stts_stt table has data)", err)
	}

	// Get an existing user ID
	// TODO: this might fail on fresh DB
	var userID string
	err = pool.QueryRow(ctx, "SELECT id FROM users_user LIMIT 1").Scan(&userID)
	if err != nil {
		return 0, fmt.Errorf("failed to get user: %w (ensure users_user table has data)", err)
	}

	sectionRefID := 0
	if tableName == productionTable {
		err = pool.QueryRow(ctx, canonicalSectionIDQuery, sectionName, programType).Scan(&sectionRefID)
		if err != nil {
			return 0, fmt.Errorf("failed to resolve canonical section %q/%q: %w", programType, sectionName, err)
		}
	}

	query := productionDataFileInsert(sanitizedTableName)
	args := []any{
		"test_file.txt",
		fmt.Sprintf("test-%d", time.Now().UnixNano()),
		"txt",
		quarter,
		year,
		rand.Intn(10000000),
		sttID,
		userID,
		time.Now(),
		false,
		"uploaded",
		sectionRefID,
	}
	if tableName == shadowTable {
		query = shadowDataFileInsert(sanitizedTableName)
		args = []any{
			"test_file.txt",
			fmt.Sprintf("test-%d", time.Now().UnixNano()),
			"txt",
			quarter,
			year,
			sectionName,
			rand.Intn(10000000),
			sttID,
			userID,
			time.Now(),
			programType,
			false,
			"uploaded",
		}
	}

	var datafileID int32
	err = pool.QueryRow(ctx, query, args...).Scan(&datafileID)

	if err != nil {
		return 0, fmt.Errorf("failed to create datafile: %w", err)
	}

	return datafileID, nil
}

func shadowDataFileInsert(sanitizedTableName string) string {
	return fmt.Sprintf(`
		INSERT INTO %s (
			original_filename, slug, extension, quarter, year, section,
			version, stt_id, user_id, created_at, program_type,
			is_program_audit, state
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
		RETURNING id
	`, sanitizedTableName)
}

func productionDataFileInsert(sanitizedTableName string) string {
	return fmt.Sprintf(`
		INSERT INTO %s (
			original_filename, slug, extension, quarter, year, version,
			stt_id, user_id, created_at, is_program_audit, state, section_ref_id
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
		RETURNING id
	`, sanitizedTableName)
}

// DeleteTestDatafile removes a test datafile and its associated records.
func DeleteTestDatafile(ctx context.Context, pool *pgxpool.Pool, datafileID int32) error {
	return DeleteTestDatafileFromTable(ctx, pool, dataFileTableNameFromEnv(), datafileID)
}

// DeleteTestDatafileFromTable removes a test datafile from the specified table.
func DeleteTestDatafileFromTable(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32) error {
	if tableName != config.DataFileTableName("") && tableName != config.DataFileTableName(config.DefaultTablePrefix) {
		return fmt.Errorf("unsupported datafile table %q", tableName)
	}
	sanitizedTableName := pgx.Identifier{tableName}.Sanitize()
	_, err := pool.Exec(ctx, fmt.Sprintf("DELETE FROM %s WHERE id = $1", sanitizedTableName), datafileID)
	return err
}
