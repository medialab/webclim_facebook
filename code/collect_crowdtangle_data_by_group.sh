#!/bin/bash

LIST=$1
TODAY_DATE=$(date +"%Y-%m-%d")

minet ct posts --list-ids $LIST --start-date 2019-01-01 --end-date 2020-12-31 > \
  "./data/crowdtangle_group/posts_group_${TODAY_DATE}.csv"

# minet ct posts --list-ids $LIST --start-date 2019-01-01 --end-date 2020-12-31 \
#   --resume --output "./data/crowdtangle_group/posts_group_${TODAY_DATE}.csv"