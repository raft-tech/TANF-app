package config

import (
	"os"
	"strings"
	"testing"
)

const testCloudFoundryServices = `{
  "aws-rds": [{
    "name": "tdp-db-staging",
    "credentials": {
      "host": "db.example.gov",
      "port": "5432",
      "username": "db-user",
      "password": "db/password",
      "db_name": "managed-db"
    }
  }],
  "s3": [{
    "name": "tdp-datafiles-staging",
    "credentials": {
      "access_key_id": "access-key",
      "secret_access_key": "secret-key",
      "bucket": "data-bucket",
      "region": "us-gov-west-1"
    }
  }],
  "aws-elasticache-redis": [{
    "name": "tdp-redis-staging",
    "credentials": {
      "host": "redis.example.gov",
      "port": "6379",
      "password": "redis/password"
    }
  }]
}`

func TestCloudFoundryEnvironment(t *testing.T) {
	values, err := cloudFoundryEnvironment(
		[]byte(testCloudFoundryServices),
		[]byte(`{"space_name":"tanf-staging"}`),
		"tdp-backend-develop",
	)
	if err != nil {
		t.Fatalf("cloudFoundryEnvironment returned an error: %v", err)
	}

	expected := map[string]string{
		"AWS_ACCESS_KEY_ID":     "access-key",
		"AWS_DEFAULT_REGION":    "us-gov-west-1",
		"AWS_SECRET_ACCESS_KEY": "secret-key",
		"S3_BUCKET":             "data-bucket",
		"S3_KEY_PREFIX":         "tdp-backend-develop",
	}
	for name, expectedValue := range expected {
		if values[name] != expectedValue {
			t.Errorf("%s = %q, want %q", name, values[name], expectedValue)
		}
	}

	if !strings.Contains(values["DATABASE_URL"], "tdp_db_develop") {
		t.Errorf("DATABASE_URL = %q, want environment database name", values["DATABASE_URL"])
	}
	if !strings.Contains(values["DATABASE_URL"], "db%2Fpassword") {
		t.Errorf("DATABASE_URL = %q, want escaped password", values["DATABASE_URL"])
	}
	if values["REDIS_URL"] != "rediss://:redis%2Fpassword@redis.example.gov:6379/0" {
		t.Errorf("REDIS_URL = %q", values["REDIS_URL"])
	}
}

func TestCloudFoundryEnvironmentUsesManagedProductionDatabase(t *testing.T) {
	services := strings.ReplaceAll(testCloudFoundryServices, "staging", "prod")
	values, err := cloudFoundryEnvironment(
		[]byte(services),
		[]byte(`{"space_name":"tanf-prod"}`),
		"tdp-backend-prod",
	)
	if err != nil {
		t.Fatalf("cloudFoundryEnvironment returned an error: %v", err)
	}

	if !strings.Contains(values["DATABASE_URL"], "managed-db") {
		t.Errorf("DATABASE_URL = %q, want managed production database name", values["DATABASE_URL"])
	}
}

func TestCloudFoundryEnvironmentMapsRaftToTestDatabase(t *testing.T) {
	services := strings.ReplaceAll(testCloudFoundryServices, "staging", "dev")
	values, err := cloudFoundryEnvironment(
		[]byte(services),
		[]byte(`{"space_name":"tanf-dev"}`),
		"tdp-backend-raft",
	)
	if err != nil {
		t.Fatalf("cloudFoundryEnvironment returned an error: %v", err)
	}

	if !strings.Contains(values["DATABASE_URL"], "tdp_db_test") {
		t.Errorf("DATABASE_URL = %q, want test database name", values["DATABASE_URL"])
	}
	if !strings.HasSuffix(values["REDIS_URL"], "/0") {
		t.Errorf("REDIS_URL = %q, want Redis database 0", values["REDIS_URL"])
	}
}

func TestApplyCloudFoundryBindingsPreservesExplicitEnvironment(t *testing.T) {
	t.Setenv("VCAP_SERVICES", testCloudFoundryServices)
	t.Setenv("VCAP_APPLICATION", `{"space_name":"tanf-staging"}`)
	t.Setenv("CGAPPNAME_BACKEND", "tdp-backend-develop")
	t.Setenv("DATABASE_URL", "postgres://explicit")

	if err := ApplyCloudFoundryBindings(); err != nil {
		t.Fatalf("ApplyCloudFoundryBindings returned an error: %v", err)
	}

	if value := os.Getenv("DATABASE_URL"); value != "postgres://explicit" {
		t.Errorf("DATABASE_URL = %q, want explicit value", value)
	}
}

func TestCloudFoundryEnvironmentRejectsUnknownEnvironment(t *testing.T) {
	_, err := cloudFoundryEnvironment(
		[]byte(testCloudFoundryServices),
		[]byte(`{"space_name":"tanf-staging"}`),
		"tdp-backend-unknown",
	)
	if err == nil || !strings.Contains(err.Error(), "no Celery Redis database") {
		t.Fatalf("cloudFoundryEnvironment error = %v", err)
	}
}
