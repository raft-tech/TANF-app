#!/usr/bin/sh

cat base_config.yml > generated_config.yml
echo 'commands:' >> generated_config.yml

cat build-and-test/commands.yml >> generated_config.yml
cat infrastructure/commands.yml >> generated_config.yml
cat deployment/commands.yml >> generated_config.yml

echo 'jobs:' >> generated_config.yml
cat build-and-test/jobs.yml >> generated_config.yml
cat infrastructure/jobs.yml >> generated_config.yml
cat deployment/jobs.yml >> generated_config.yml

cat generated_config.yml
