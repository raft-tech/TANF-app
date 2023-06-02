#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else

    apt-get update
    apt-get install wget gnupg2 apt-transport-https

    mkdir $HOME/glibc/ && cd $HOME/glibc
    wget http://ftp.gnu.org/gnu/libc/glibc-2.32.tar.gz
    tar -xvzf glibc-2.32.tar.gz
    mkdir build
    mkdir glibc-2.32-install
    cd build
    ~/glibc/glibc-2.32/configure --prefix=$HOME/glibc/glibc-2.32-install
    make
    make install

    wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -

    echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list

    apt-get update
    apt-get install cf7-cli

    wget -q https://github.com/cloudfoundry/stack-auditor/releases/download/v0.1.0/stack-auditor-linux-64
    cf install-plugin -f stack-auditor-linux-64
fi
