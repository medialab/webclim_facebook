#!/bin/bash

LIST=$1

TODAY_DATE=$(date +"%Y-%m-%d")
token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

echo "starting data collection..."

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2019-11-01 --end-date 2020-10-27 \
  --rate-limit 50 --partition-strategy 500 > "./data/data_crowdtangle_group/posts_group_${TODAY_DATE}_0.csv"
echo "2020 DONE!"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2018-11-01 --end-date 2019-11-01 \
  --rate-limit 50 --partition-strategy 500 > "./data/data_crowdtangle_group/posts_group_${TODAY_DATE}_1.csv"
echo "2019 DONE!"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2017-11-01 --end-date 2018-11-01 \
  --rate-limit 50 --partition-strategy 500 > "./data/data_crowdtangle_group/posts_group_${TODAY_DATE}_2.csv"
echo "2018 DONE!"

minet ct posts --token $token_crowdtangle --list-ids $LIST --start-date 2016-11-01 --end-date 2017-11-01 \
  --rate-limit 50 --partition-strategy 500 > "./data/data_crowdtangle_group/posts_group_${TODAY_DATE}_3.csv"
echo "2017 DONE!"