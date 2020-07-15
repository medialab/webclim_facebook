#!/bin/bash

DATE="2020-07-15"
ITERATION=$1

output_file="./data_crowdtangle_group/posts_group_${DATE}_${ITERATION}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

minet ct posts --token $token_crowdtangle --list-ids 1401873 --start-date 2019-09-01 \
  --rate-limit 50 --partition-strategy 500 > $output_file

## 218 : https://www.facebook.com/groups/698141807656499 (0h53)
## 148 : https://www.facebook.com/groups/346378325942318 (1h17) stoppée à date=2020-04-06T17:55:38
## collect between  XX and  XX fake news shared : X groups (XhXX)
