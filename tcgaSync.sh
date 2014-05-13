#!/bin/bash

rm -f web_error
rm -f check_html.out
rm -f md5.manifest
rm -f error
touch check_html.out md5.manifest web_error error

#open
baseURL="https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/"
baseLocal="/data/TCGA/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/"

python tcgaManifest.py $baseURL open tcga.public.manifest 2>>web_error
rm -rf /data/TCGA/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/*/bcr/biotab/clin/
python checkManifest.py tcga.public.manifest > tcga.public.status
grep missing_dir tcga.public.status | awk '{print $2}' | xargs -i mkdir -p /data/TCGA/{}
grep missing_file tcga.public.status | awk '{print $2}' | xargs -P 4 -i curl https://tcga-data.nci.nih.gov/{} -o /data/TCGA/{}  

find $baseLocal -exec file {} \; | grep HTML >> check_html.out 
python md5CheckDir.py $baseLocal >> md5.manifest


#firehose
baseLocal="/data/TCGA/tcgafiles/tcga4yeo/other/gdacs/gdacbroad/firehose/"
homeDIR="/inside/home/jzhu/JingTcgaSync/"
LATEST=$(/inside/home/jzhu/scripts/firehose_get -r |grep analyses |tail -n 1)

if [ -d $baseLocal$LATEST ]
then
    echo "File $baseLocal$LATEST  exists"
else
    cohort=$(/inside/home/jzhu/scripts/firehose_get -c |tr ' ' '\n' |tr -d "\t" | grep -v ^$ |grep -v PANCAN | tr '\n' ' ')
    cd $baseLocal
    nice /inside/home/jzhu/scripts/firehose_get -b analyses latest $cohort
fi

cd $homeDIR
python md5CheckDir.py $baseLocal >> md5.manifest


#secured FH

#baseURL="https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/other/gdacs/gdacbroad/"
#baseLocal="/inside/depot/tcgafiles/tcga4yeo/other/gdacs/gdacbroad/"

#python tcgaManifest.py $baseURL secure tcga.controlled.manifest `cat /data/TCGA/TCGA_login.dat | tr ":" " "`  2>>web_error
#python checkManifest.py tcga.controlled.manifest  `cat /data/TCGA/TCGA_login.dat | tr ":" " "` > tcga.controlled.status
#grep missing_dir tcga.controlled.status | awk '{print $2}' | xargs -i mkdir -p /inside/depot/{}
#grep missing_file tcga.controlled.status | awk '{print $2}' | xargs -P 4 -i curl -u `cat /data/TCGA/TCGA_login.dat` https://tcga-data-secure.nci.nih.gov/{} -o /inside/depot/{}
#find $baseLocal -exec file {} \; | grep HTML >> check_html.out 
#python md5CheckDir.py $baseLocal >> md5.manifest


cat web_error check_html.out md5.manifest > error
cat error |mail -s 'tcgaSync' jzhu@soe.ucsc.edu

