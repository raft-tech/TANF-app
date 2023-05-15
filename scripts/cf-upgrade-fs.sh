#!/bin/bash

CF_FS=${1}
CF_SPACE=${2}

cf target -o hhs-acf-ofa -s $CF_SPACE

ALL_APP_NAMES=$(cf curl "v3/apps" | jq '.resources' | jq '.[].name')
SUB1="frontend"
SUB2="backend"
SUB3="clamav"
SUB4="nexus"

for i in $ALL_APP_NAMES; do
    if [[ $i =~ $SUB1|$SUB2|$SUB3|$SUB4 ]]
    then
        continue
    else
        temp="${i%\"}"
        temp="${temp#\"}"
        cf change-stack $temp $CF_FS || true
    fi
done
