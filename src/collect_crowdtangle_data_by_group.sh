#!/bin/bash

LIST=$1
DATE=$2

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

output_file="./data_crowdtangle_group/posts_group_${DATE}.csv"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 --end-date 2020-08-31 \
  --rate-limit 50 --partition-strategy 500 > $output_file

# minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 --end-date 2020-08-31 \
#   --rate-limit 50 --partition-strategy 500 --resume --output $output_file