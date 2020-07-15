#!/bin/bash

if [ $# -ge 1 ] ; then
        DATE=$1
else
        DATE="2020-06-29"
        echo "The date '${DATE}' has been chosen by default."
fi

INPUT_FILE="./data_sciencefeedback/appearances_${DATE}_clean.csv"
OUTPUT_FILE="./data_crowdtangle_url/posts_url_${DATE}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

if [ ! -f $OUTPUT_FILE ]; 
then
    minet ct summary url $INPUT_FILE --token $token_crowdtangle \
     --posts $OUTPUT_FILE --sort-by total_interactions --start-date 2019-01-01
else
    echo "Nothing to do, the output file already exists"
fi

## 576 url (only COVID): 1h57 (29 June 2020)
