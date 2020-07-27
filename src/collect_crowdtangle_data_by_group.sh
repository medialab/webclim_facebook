#!/bin/bash

LIST=$1
DATE=$2
ITERATION=$3

output_file="./data_crowdtangle_group/posts_group_${DATE}_${ITERATION}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

# minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 \
#   --rate-limit 50 --partition-strategy 500 > $output_file

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 \
  --rate-limit 50 --partition-strategy 500 --resume --output $output_file