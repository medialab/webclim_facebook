#!/bin/bash

DATE=$1

if [ $# -eq 1 ]; then TOPIC=""
else TOPIC=$2; fi

TODAY_DATE=$(date +"%Y-%m-%d")

INPUT_FILE="./data/data_sciencefeedback/appearances_${DATE}_${TOPIC}.csv"
OUTPUT_FILE="./data/data_crowdtangle_url/posts_url_${TODAY_DATE}_${TOPIC}.csv"

minet ct summary url $INPUT_FILE --posts $OUTPUT_FILE \
 --sort-by total_interactions --start-date 2019-01-01 --platforms facebook
