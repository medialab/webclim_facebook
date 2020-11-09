#!/bin/bash

LIST=$1
TODAY_DATE=$(date +"%Y-%m-%d")

minet ct posts --list-ids $LIST --start-date 2016-11-01 --end-date 2020-10-31 > \
  "./data/data_crowdtangle_group/posts_group_${TODAY_DATE}.csv"
