#!/bin/bash

rm -f web_error
rm -f check_html.out
rm -f md5.manifest
rm -f error
touch check_html.out md5.manifest web_error error

#firehose
baseLocal="/data/TCGA/tcgafiles/tcga4yeo/other/gdacs/gdacbroad/firehose/"
homeDIR="/inside/home/jzhu/JingTcgaSync/"
LATEST=$(/inside/home/jzhu/scripts/firehose_get -r |grep analyses |tail -n 1)

if [ -d $baseLocal$LATEST ]
then
    echo "File $baseLocal$LATEST  exists"
    cat md5.manifest |mail -s 'firehose new version'$LATEST  jzhu@soe.ucsc.edu
else
    cohort=$(/inside/home/jzhu/scripts/firehose_get -c |tr ' ' '\n' |tr -d "\t" | grep -v ^$ |grep -v PANCAN | tr '\n' ' ')
    cd $baseLocal
    nice /inside/home/jzhu/scripts/firehose_get -b analyses latest $cohort
    cd $homeDIR
    python md5CheckDir.py $baseLocal > md5.manifest
    cat md5.manifest |mail -s 'firehose new version'$LATEST  jzhu@soe.ucsc.edu
fi






