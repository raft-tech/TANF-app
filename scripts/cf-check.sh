#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else

    apt-get update
    apt-get install wget gnupg2 apt-transport-https

    wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -

    echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list

    apt-get update
    apt-get install cf7-cli

    wget -q https://github.com/cloudfoundry/stack-auditor/releases/download/v0.1.0/stack-auditor-linux-64
    cf install-plugin stack-auditor-linux-64 
fi
