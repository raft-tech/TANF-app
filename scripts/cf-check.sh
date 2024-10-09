#!/bin/sh
set -e
if command -v cfx /dev/null 2>&1; then
    echo The command cf is available
else
    # using curl, i want to download from our nexus host at https://tdp-nexus.dev.raftlabs.tech with
    # path /#browse/browse:tdp-bin:cloudfoundry-cli to download this file: "cloudfoundry-cli/cf7-cli_7.7.13_linux_x86-64.tgz"
    # using the credentials $NEXUS_USER and $NEXUS_PASS 
    # and then extract the file and move it to /usr/local/bin/cf
    # and then make it executable
    NEXUS_ARCHIVE="cf7-cli_7.7.13_linux_x86-64.tgz"
    NEXUS_URL="https://tdp-nexus.dev.raftlabs.tech/repository/tdp-bin/cloudfoundry-cli/$NEXUS_ARCHIVE"
    #curl -u $NEXUS_USER:$NEXUS_PASS $NEXUS_URL -o $NEXUS_ARCHIVE
    curl $NEXUS_URL -o $NEXUS_ARCHIVE
    tar xzf $NEXUS_ARCHIVE #&& rm -f $NEXUS_ARCHIVE
    mv ./cf /usr/local/bin/
    chmod +x /usr/local/bin/cf

    # apt-get update
    # apt-get install wget gnupg2 apt-transport-https

    # wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -

    # echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list

    # apt-get update
    # apt-get install cf7-cli

fi
