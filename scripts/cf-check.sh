 #!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
echo The command cf is available
else
apt-get update
apt-get install -y apt-transport-https wget gnupg git
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | tee /etc/apt/sources.list.d/cloudfoundry-cli.list
apt -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true update
apt-get install --allow-unauthenticated -y cf7-cli
cf --version
fi 
