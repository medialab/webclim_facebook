#!/bin/bash

DATE=$1
ITERATION=$2

output_file="./data_crowdtangle_group/posts_group_${DATE}_${ITERATION}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

minet ct posts --token $token_crowdtangle --list-ids 1422061 --start-date 2019-09-01 \
  --rate-limit 50 --partition-strategy 500 > $output_file
