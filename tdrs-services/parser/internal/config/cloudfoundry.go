package config

import (
	"encoding/json"
	"fmt"
	"net"
	"net/url"
	"os"
	"strings"
)

type cloudFoundryService struct {
	Name         string         `json:"name"`
	InstanceName string         `json:"instance_name"`
	Credentials  map[string]any `json:"credentials"`
}

type cloudFoundryApplication struct {
	SpaceName string `json:"space_name"`
}

func ApplyCloudFoundryBindings() error {
	servicesJSON := os.Getenv("VCAP_SERVICES")
	if servicesJSON == "" {
		return nil
	}

	values, err := cloudFoundryEnvironment(
		[]byte(servicesJSON),
		[]byte(os.Getenv("VCAP_APPLICATION")),
		os.Getenv("CGAPPNAME_BACKEND"),
	)
	if err != nil {
		return err
	}

	for name, value := range values {
		if os.Getenv(name) == "" {
			if err := os.Setenv(name, value); err != nil {
				return fmt.Errorf("setting %s from Cloud Foundry bindings: %w", name, err)
			}
		}
	}

	return nil
}

func cloudFoundryEnvironment(servicesJSON, applicationJSON []byte, backendAppName string) (map[string]string, error) {
	if backendAppName == "" {
		return nil, fmt.Errorf("CGAPPNAME_BACKEND is required in Cloud Foundry")
	}

	var services map[string][]cloudFoundryService
	if err := json.Unmarshal(servicesJSON, &services); err != nil {
		return nil, fmt.Errorf("parsing VCAP_SERVICES: %w", err)
	}

	var application cloudFoundryApplication
	if err := json.Unmarshal(applicationJSON, &application); err != nil {
		return nil, fmt.Errorf("parsing VCAP_APPLICATION: %w", err)
	}

	spaceName := strings.TrimPrefix(application.SpaceName, "tanf-")
	environmentName := strings.TrimPrefix(backendAppName, "tdp-backend-")
	if spaceName == "" || environmentName == "" || environmentName == backendAppName {
		return nil, fmt.Errorf("invalid Cloud Foundry application context")
	}

	database, err := findCloudFoundryService(services["aws-rds"], "tdp-db-"+spaceName)
	if err != nil {
		return nil, err
	}
	datafiles, err := findCloudFoundryService(services["s3"], "tdp-datafiles-"+spaceName)
	if err != nil {
		return nil, err
	}
	redis, err := findCloudFoundryService(services["aws-elasticache-redis"], "tdp-redis-"+spaceName)
	if err != nil {
		return nil, err
	}

	databaseEnvironmentName := environmentName
	if environmentName == "raft" {
		databaseEnvironmentName = "test"
	}
	databaseName := "tdp_db_" + databaseEnvironmentName
	if spaceName == "prod" {
		databaseName, err = credential(database.Credentials, "db_name")
		if err != nil {
			return nil, err
		}
	}

	databaseURL, err := buildDatabaseURL(database.Credentials, databaseName)
	if err != nil {
		return nil, err
	}
	redisURL, err := buildRedisURL(redis.Credentials, environmentName)
	if err != nil {
		return nil, err
	}

	accessKey, err := credential(datafiles.Credentials, "access_key_id")
	if err != nil {
		return nil, err
	}
	secretKey, err := credential(datafiles.Credentials, "secret_access_key")
	if err != nil {
		return nil, err
	}
	bucket, err := credential(datafiles.Credentials, "bucket")
	if err != nil {
		return nil, err
	}
	region, err := credential(datafiles.Credentials, "region")
	if err != nil {
		return nil, err
	}

	return map[string]string{
		"AWS_ACCESS_KEY_ID":     accessKey,
		"AWS_DEFAULT_REGION":    region,
		"AWS_SECRET_ACCESS_KEY": secretKey,
		"DATABASE_URL":          databaseURL,
		"REDIS_URL":             redisURL,
		"S3_BUCKET":             bucket,
		"S3_KEY_PREFIX":         backendAppName,
	}, nil
}

func findCloudFoundryService(services []cloudFoundryService, name string) (cloudFoundryService, error) {
	for _, service := range services {
		if service.Name == name || service.InstanceName == name {
			return service, nil
		}
	}
	return cloudFoundryService{}, fmt.Errorf("Cloud Foundry service %s is not bound", name)
}

func buildDatabaseURL(credentials map[string]any, databaseName string) (string, error) {
	host, err := credential(credentials, "host")
	if err != nil {
		return "", err
	}
	port, err := credential(credentials, "port")
	if err != nil {
		return "", err
	}
	username, err := credential(credentials, "username")
	if err != nil {
		return "", err
	}
	password, err := credential(credentials, "password")
	if err != nil {
		return "", err
	}

	databaseURL := url.URL{
		Scheme: "postgres",
		User:   url.UserPassword(username, password),
		Host:   net.JoinHostPort(host, port),
		Path:   databaseName,
	}
	return databaseURL.String(), nil
}

func buildRedisURL(credentials map[string]any, environmentName string) (string, error) {
	host, err := credential(credentials, "host")
	if err != nil {
		return "", err
	}
	port, err := credential(credentials, "port")
	if err != nil {
		return "", err
	}
	password, err := credential(credentials, "password")
	if err != nil {
		return "", err
	}
	databaseNumber, err := celeryDatabaseNumber(environmentName)
	if err != nil {
		return "", err
	}

	redisURL := url.URL{
		Scheme: "rediss",
		User:   url.UserPassword("", password),
		Host:   net.JoinHostPort(host, port),
		Path:   databaseNumber,
	}
	return redisURL.String(), nil
}

func celeryDatabaseNumber(environmentName string) (string, error) {
	databaseNumbers := map[string]string{
		"test":    "0",
		"raft":    "0",
		"qasp":    "3",
		"a11y":    "6",
		"develop": "0",
		"staging": "3",
		"prod":    "0",
	}
	databaseNumber, ok := databaseNumbers[environmentName]
	if !ok {
		return "", fmt.Errorf("no Celery Redis database is configured for %s", environmentName)
	}
	return databaseNumber, nil
}

func credential(credentials map[string]any, name string) (string, error) {
	value, ok := credentials[name]
	if !ok || value == nil {
		return "", fmt.Errorf("Cloud Foundry service credential %s is missing", name)
	}
	return fmt.Sprint(value), nil
}
