#!/bin/bash

DATE=$1

if [ $# -eq 1 ]; then TOPIC=""
else TOPIC=$2; fi

TODAY_DATE=$(date +"%Y-%m-%d")

INPUT_FILE="./data_sciencefeedback/appearances_${DATE}_${TOPIC}.csv"
OUTPUT_FILE="./data_crowdtangle_url/posts_url_${TODAY_DATE}_${TOPIC}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

if [ ! -f $OUTPUT_FILE ]; 
then
    minet ct summary url $INPUT_FILE --token $token_crowdtangle \
     --posts $OUTPUT_FILE --sort-by total_interactions --start-date 2019-01-01
else
    echo "Nothing to do, the output file already exists"
fi

## 576 url (only COVID): 1h57 (June 29, 2020)
## 1958 url (all): 5h (October 7, 2020)