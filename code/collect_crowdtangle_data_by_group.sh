#!/bin/bash

LIST=$1

TODAY_DATE=$(date +"%Y-%m-%d")
token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)
output_file="./data/data_crowdtangle_group/posts_group_${TODAY_DATE}.csv"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 --end-date 2020-08-31 \
  --rate-limit 50 --partition-strategy 500 > $output_file
