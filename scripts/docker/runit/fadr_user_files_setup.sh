#!/bin/bash
# This script is first to run due to this: https://github.com/phusion/baseimage-docker#running_startup_scripts.
#
# It updates the UIG or GID of the included fadr user to whatever value the user
# passes at runtime, if the value set is not the default value of 1000
#
# If the container is run again without specifying UID and GID, this script
# resets the UID and GID of all files in FADR directories to the defaults

set -euo pipefail

export FADR_HOME="/home/fadr"
DEFAULT_UID=1000
DEFAULT_GID=1000


# Function to check if the FADR user has ownership of the requested folder
check_folder_ownership() {
    local check_dir="$1"  # Get the folder path from the first argument
    local folder_uid=$(stat -c "%u" "$check_dir")
    local folder_gid=$(stat -c "%g" "$check_dir")

    echo "Checking ownership of $check_dir"

    if [ "$folder_uid" != "$FADR_UID" ] || [ "$folder_gid" != "$FADR_GID" ]; then
        echo "---------------------------------------------"
        echo "[ERROR]: FADR does not have permissions to $check_dir using $FADR_UID:$FADR_GID"
        echo "Check your user permissions and restart FADR. Folder permissions--> $folder_uid:$folder_gid"
        echo "---------------------------------------------"
        exit 1
    fi

    echo "[OK]: FADR UID and GID set correctly, FADR has access to '$check_dir' using $FADR_UID:$FADR_GID"
}

### Setup User
if [[ $FADR_UID -ne $DEFAULT_UID ]]; then
  echo -e "Updating fadr user id from $DEFAULT_UID to $FADR_UID..."
  usermod -u "$FADR_UID" fadr
elif [[ $FADR_UID -eq $DEFAULT_UID ]]; then
  echo -e "Updating fadr group id $FADR_UID to default (1000)..."
  usermod -u $DEFAULT_UID fadr
fi

if [[ $FADR_GID -ne $DEFAULT_GID ]]; then
  echo -e "Updating fadr group id from $DEFAULT_GID to $FADR_GID..."
  groupmod -og "$FADR_GID" fadr
elif [[ $FADR_GID -eq $DEFAULT_GID ]]; then
  echo -e "Updating fadr group id $FADR_GID to default (1000)..."
  groupmod -og $DEFAULT_GID fadr
fi
echo "Adding fadr user to 'render' group"
usermod -a -G render fadr

### Setup Files
chown -R fadr:fadr /opt/fadr

# Check ownership of the FADR home folder
check_folder_ownership "/home/fadr"

# setup needed/expected dirs if not found
SUBDIRS="media media/completed media/raw media/movies media/transcode logs logs/progress db music .MakeMKV"
for dir in $SUBDIRS ; do
  thisDir="$FADR_HOME/$dir"
  if [[ ! -d "$thisDir" ]] ; then
    echo "Creating dir: $thisDir"
    mkdir -p "$thisDir"
    # Set the default ownership to fadr instead of root
    chown -R fadr:fadr "$thisDir"
  fi
done

echo "Removing any link between music and Music"
if [ -h /home/fadr/Music ]; then
  echo "Music symbolic link found, removing link"
  unlink /home/fadr/Music
fi

##### Setup FADR-specific config files if not found
# Check ownership of the FADR config folder
check_folder_ownership "/etc/fadr/config"

mkdir -p /etc/fadr/config
CONFS="fadr.yaml apprise.yaml"
for conf in $CONFS; do
  thisConf="/etc/fadr/config/${conf}"
  if [[ ! -f "${thisConf}" ]] ; then
    echo "Config not found! Creating config file: ${thisConf}"
    # Don't overwrite with defaults during reinstall
    cp --no-clobber "/opt/fadr/setup/${conf}" "${thisConf}"
  fi
done

##### abcde config setup
# abcde.conf is expected in /etc by the abcde installation
echo "Checking location of abcde configuration files"
# Test if abcde.conf is a hyperlink, if so remove it
if [ -h /etc/fadr/config/abcde.conf ]; then
  echo "Old hyper link exists removing!"
  unlink /etc/fadr/config/abcde.conf
fi
# check if abcde is in config main location - only copy if it doesnt exist
if ! [ -f /etc/fadr/config/abcde.conf ]; then
  echo "abcde.conf doesnt exist"
  cp /opt/fadr/setup/.abcde.conf /etc/fadr/config/abcde.conf
  # chown fadr:fadr /etc/fadr/config/abcde.conf
fi
# The system link to the fake default file -not really needed but as a precaution to the -C variable being blank
if ! [ -h /etc/abcde.conf ]; then
  echo "/etc/abcde.conf link doesnt exist"
  ln -sf /etc/fadr/config/abcde.conf /etc/abcde.conf
fi

# symlink $FADR_HOME/Music to $FADR_HOME/music because the config for abcde doesn't match the docker compose docs
# separate rm and ln commands because "ln -sf" does the wrong thing if dest is a symlink to a directory
# rm -rf $FADR_HOME/music
# ln -s $FADR_HOME/Music $FADR_HOME/music
