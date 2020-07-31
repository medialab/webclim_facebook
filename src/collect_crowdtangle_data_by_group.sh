#!/bin/bash

LIST=$1
DATE=$2
ITERATION1=$3
ITERATION2=$4

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

output_file1="./data_crowdtangle_group/posts_group_${DATE}_${ITERATION1}.csv"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 \
  --rate-limit 50 --partition-strategy 500 > $output_file1

output_file2="./data_crowdtangle_group/posts_group_${DATE}_${ITERATION2}.csv"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-01-01 --end-date 2019-08-31 \
  --rate-limit 50 --partition-strategy 500 > $output_file2

# minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-09-01 \
#   --rate-limit 50 --partition-strategy 500 --resume --output $output_file