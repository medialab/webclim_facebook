#!/bin/bash

DATE="2020-07-15"
ITERATION=$1

output_file="./data_crowdtangle_group/posts_group_${DATE}_${ITERATION}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

minet ct posts --token $token_crowdtangle --list-ids 1401873 --start-date 2019-09-01 \
  --rate-limit 50 --partition-strategy 500 > $output_file

## 1 : 218 : https://www.facebook.com/groups/698141807656499 (0h53)
## 2 : 148 : https://www.facebook.com/groups/346378325942318 (XhXX)
## 3 : entre 20 et 98 : 15 groupes (5h03)
## 5 : entre 15 et 19 : 12 groupes (2h43)
## 6 : entre 12 et 14 : 16 groupes (1h54)
## 7 : entre 10 et 11 : 20 groupes (2h26)
