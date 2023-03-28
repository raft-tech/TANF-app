#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else

    apt-get update
    apt-get install wget gnupg2 apt-transport-https

    wget -U "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36" -q -O https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -

    echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list

    apt-get update
    apt-get install cf7-cli
fi
