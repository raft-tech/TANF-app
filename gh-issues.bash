#!/bin/bash

id_list=`gh issue list --state OPEN --json number --limit 999| jq ".[].number"`
echo > github-dump.json
for n in $id_list; do 
  echo "Adding issue $n"
  gh issue view $n --json number,author,url,createdAt,title >> github-dump.json 
done
