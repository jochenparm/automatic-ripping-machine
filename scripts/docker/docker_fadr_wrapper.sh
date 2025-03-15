#!/bin/bash

DEVNAME=$1
FADRLOG="/home/fadr/logs/fadr.log"
echo "[FADR] Entering docker wrapper" | logger -t FADR -s
echo "$(date) Entering docker wrapper" >> $FADRLOG

#######################################################################################
# YAML Parser to read Config
#
# From: https://stackoverflow.com/questions/5014632/how-can-i-parse-a-yaml-file-from-a-linux-shell-script
#######################################################################################

function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}
eval $(parse_yaml /etc/fadr/config/fadr.yaml "CONFIG_")

#######################################################################################
# Log Discovered Type and Start Rip
#######################################################################################

# ID_CDROM_MEDIA_BD = Bluray
# ID_CDROM_MEDIA_CD = CD
# ID_CDROM_MEDIA_DVD = DVD
if [ "$ID_CDROM_MEDIA_DVD" == "1" ]; then
    if [ "$CONFIG_PREVENT_99" != "false" ]; then
        numtracks=$(lsdvd /dev/"${DEVNAME}" 2> /dev/null | sed 's/,/ /' | cut -d ' ' -f 2 | grep -E '[0-9]+' | sort -r | head -n 1)
        if [ "$numtracks" == "99" ]; then
            echo "[FADR] ${DEVNAME} has 99 Track Protection. Bailing out and ejecting." | logger -t FADR -s
            echo "$(date) [FADR] ${DEVNAME} has 99 Track Protection. Bailing out and ejecting." >> $FADRLOG
            eject "${DEVNAME}"
            exit
        fi
    fi
    echo "$(date) [FADR] Starting FADR for DVD on ${DEVNAME}" >> $FADRLOG
    echo "[FADR] Starting FADR for DVD on ${DEVNAME}" | logger -t FADR -s
elif [ "$ID_CDROM_MEDIA_BD" == "1" ]; then
	  echo "[FADR] Starting FADR for Bluray on ${DEVNAME}" >> $FADRLOG
	  echo "$(date) [[FADR] Starting FADR for Bluray on ${DEVNAME}" | logger -t FADR -s
elif [ "$ID_CDROM_MEDIA_CD" == "1" ]; then
	  echo "[FADR] Starting FADR for CD on ${DEVNAME}" | logger -t FADR -s
	  echo "$(date) [[FADR] Starting FADR for CD on ${DEVNAME}" >> $FADRLOG
elif [ "$ID_FS_TYPE" != "" ]; then
	  echo "[FADR] Starting FADR for Data Disk on ${DEVNAME} with File System ${ID_FS_TYPE}" | logger -t FADR -s
	  echo "$(date) [[FADR] Starting FADR for Data Disk on ${DEVNAME} with File System ${ID_FS_TYPE}" >> $FADRLOG
else
	  echo "[FADR] Not CD, Blu-ray, DVD or Data. Bailing out on ${DEVNAME}" | logger -t FADR -s
	  echo "$(date) [FADR] Not CD, Blu-ray, DVD or Data. Bailing out on ${DEVNAME}" >> $FADRLOG
      if [ "$CONFIG_UNIDENTIFIED_EJECT" != "false" ]; then
	    eject "${DEVNAME}"
      fi
	  exit #bail out
fi
cd /home/fadr
/usr/bin/python3 /opt/fadr/fadr/ripper/main.py -d "${DEVNAME}" | logger -t FADR -s
