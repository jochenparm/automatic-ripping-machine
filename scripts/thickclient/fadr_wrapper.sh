#!/bin/bash -i

set -eo pipefail

DEVNAME=$1
PROTECTION=""
USER="fadr"

#######################################################################################
# YAML Parser to read Config
#
# From: https://stackoverflow.com/questions/5014632/how-can-i-parse-a-yaml-file-from-a-linux-shell-script
#######################################################################################

function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*'
   local w='[a-zA-Z0-9_]*'
   local fs
   fs=$(echo @ | tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:${s}[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  "$1" |
   awk -F"$fs" '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'"$prefix"'",vn, $2, $3);
      }
   }'
}

eval "$(parse_yaml /etc/fadr/config/fadr.yaml "CONFIG_")"

#######################################################################################
# Log Discovered Type and Start Rip
# ID_CDROM_MEDIA_BD = Blu-ray
# ID_CDROM_MEDIA_CD = CD
# ID_CDROM_MEDIA_DVD = DVD
#######################################################################################

if [ "$ID_CDROM_MEDIA_DVD" == "1" ]; then
 numtracks=$(lsdvd "/dev/${DEVNAME}" 2> /dev/null | sed 's/,/ /' | cut -d ' ' -f 2 | grep -E '[0-9]+' | sort -r | head -n 1)#
	if [ "$numtracks" == "99" ]; then
	  if [ "$CONFIG_PREVENT_99" == "true" ]; then
		  echo "[FADR] ${DEVNAME} has 99 Track Protection...Ripping 99 is disabled.. Ejecting disc." | logger -t FADR -s
			eject "$DEVNAME"
		else
			echo "[FADR] ${DEVNAME} has 99 Track Protection...Trying workaround" | logger -t FADR -s
			PROTECTION="-p 1"
		fi
	fi
	echo "[FADR] Starting FADR for DVD on ${DEVNAME}" | logger -t FADR -s

elif [ "$ID_CDROM_MEDIA_BD" == "1" ]; then
	echo "[FADR] Starting FADR for Blu-ray on ${DEVNAME}" | logger -t FADR -s

elif [ "$ID_CDROM_MEDIA_CD" == "1" ]; then
	echo "[FADR] Starting FADR for CD on ${DEVNAME}" | logger -t FADR -s

elif [ "$ID_FS_TYPE" != "" ]; then
	echo "[FADR] Starting FADR for Data Disk on ${DEVNAME} with File System ${ID_FS_TYPE}" | logger -t FADR -s

else
	echo "[FADR] Not CD, Bluray, DVD or Data. Bailing out on ${DEVNAME}" | logger -t FADR -s
	exit #bail out

fi

/bin/su -l -c "echo /usr/bin/python3 /opt/fadr/fadr/ripper/main.py -d ${DEVNAME} ${PROTECTION} | at now" -s /bin/bash ${USER}

#######################################################################################
# Check to see if the admin page is running, if not, start it
#######################################################################################

if ! pgrep -f "runui.py" > /dev/null; then
	echo "[FADR] FADR Webgui not running; starting it " | logger -t FADR -s
	/bin/su -l -c "/usr/bin/python3 /opt/fadr/fadr/runui.py  " -s /bin/bash ${USER}
fi
