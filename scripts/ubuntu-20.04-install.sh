#!/bin/bash

set -eo pipefail

RED='\033[1;31m'
NC='\033[0m' # No Color
PORT=8080

function usage() {
    echo -e "\nUsage: ubuntu-20.04-install.sh [OPTIONS]"
    echo -e " -p <port>\tSpecify the port fadr will serve on. \n\t\tDefault is \"$PORT\""
}

port_flag=
while getopts 'p:' OPTION
do
    case $OPTION in
    p)    port_flag=1
          PORT=$OPTARG
          # test if port is valid (DOES NOT WORK WITH `set -u` DECLARED)
          if ! [[ $PORT -gt 0 && $PORT -le 65535 ]]; then
              echo -e "\nERROR: ${PORT} is not a port"
              usage
              exit 2
          fi
          ;;
    ?)    usage
          exit 1
          ;;
    esac
done

function install_os_tools() {
    sudo apt update -y && sudo apt upgrade -y
    sudo apt install alsa -y # this will install sound drivers on ubuntu server, preventing a crash
    sudo apt install lsscsi net-tools -y
    sudo apt install avahi-daemon -y && sudo systemctl restart avahi-daemon
    sudo apt install ubuntu-drivers-common -y && sudo ubuntu-drivers install
    sudo apt install git curl shellcheck -y
}

function add_fadr_user() {
    echo -e "${RED}Adding fadr user${NC}"
    # create fadr group if it doesn't already exist
    if ! [[ "$(getent group fadr)" ]]; then
        sudo groupadd fadr
    else
        echo -e "${RED}fadr group already exists, skipping...${NC}"
    fi

    # create fadr user if it doesn't already exist
    if ! id fadr >/dev/null 2>&1; then
        sudo useradd -m fadr -g fadr
        sudo passwd fadr
    else
        echo -e "${RED}fadr user already exists, skipping creation...${NC}"
    fi
    sudo usermod -aG cdrom,video fadr
}

function install_fadr_requirements() {
    echo -e "${RED}Installing FADR requirments${NC}"
    sudo add-apt-repository ppa:mc3man/focal6 -y
    sudo add-apt-repository ppa:heyarje/makemkv-beta -y
    sudo apt update -y

    sudo apt install -y \
        build-essential \
        libcurl4-openssl-dev libssl-dev \
        libudev-dev \
        udev \
        python3 \
        python3-dev \
        python3-pip \
        python3-wheel \
        python-psutil \
        python3-pyudev \
        python3-testresources \
        abcde \
        eyed3 \
        atomicparsley \
        cdparanoia \
        eject \
        ffmpeg \
        flac \
        glyrc \
        default-jre-headless \
        libavcodec-extra

    sudo apt install -y \
        handbrake-cli makemkv-bin makemkv-oss \
        imagemagick \
        at \
        libdvd-pkg lsdvd

    sudo dpkg-reconfigure libdvd-pkg

    # create folders required to run the FADR service
    sudo -u fadr mkdir -p /home/fadr/logs
}

function remove_existing_fadr() {
    ##### Check if the FADRUI service exists in any state and remove it
    if sudo systemctl list-unit-files --type service | grep -F fadrui.service; then
        echo -e "${RED}Previous installation of FADR service found. Removing...${NC}"
        service=fadrui.service
        sudo systemctl stop $service && sudo systemctl disable $service
        sudo find /etc/systemd/system/$service -delete
        sudo systemctl daemon-reload && sudo systemctl reset-failed
    fi
}

function clone_fadr() {
    cd /opt
    if [ -d fadr ]; then
        echo -e "${RED}Existing FADR installation found, removing...${NC}"
        sudo rm -rf fadr
    fi

    git clone --recurse-submodules https://github.com/automatic-ripping-machine/automatic-ripping-machine --branch "main" fadr

    cd fadr
    git submodule update --init --recursive
    git submodule update --recursive --remote
    cd ..

    sudo chown -R fadr:fadr /opt/fadr
    sudo find /opt/fadr/scripts/ -type f -iname "*.sh" -exec chmod +x {} \;
}

function install_fadr_dev_env() {
    ##### Install FADR development stack
    echo -e "${RED}Installing FADR for Development${NC}"
    clone_fadr

    # install docker
    if [ -e /usr/bin/docker ]; then
        echo -e "${RED}Docker installation detected, skipping...${NC}"
    else
        echo -e "${RED}Installing Docker${NC}"
        # the convenience script auto-detects OS and handles install accordingly
        curl -sSL https://get.docker.com | bash
        sudo usermod -aG docker fadr
    fi

    # install pychfadr community, if professional not installed already
    # shellcheck disable=SC2230
    if [[ -z $(which pychfadr-professional) ]]; then
        sudo snap install pychfadr-community --classic
    fi
}

function setup_config_files() {
    ##### Setup FADR-specific config files if not found
    sudo mkdir -p /etc/fadr/config
    CONFS="fadr.yaml apprise.yaml"
    for conf in $CONFS; do
        thisConf="/etc/fadr/config/${conf}"
        if [[ ! -f "${thisConf}" ]] ; then
            echo "creating config file ${thisConf}"
            # Don't overwrite with defaults during reinstall
            cp --no-clobber "/opt/fadr/setup/${conf}" "${thisConf}"
        fi
    done
    chown -R fadr:fadr /etc/fadr/

    # abcde.conf is expected in /etc by the abcde installation
    cp --no-clobber "/opt/fadr/setup/.abcde.conf" "/etc/.abcde.conf"
    chown fadr:fadr "/etc/.abcde.conf"
    # link to the new install location so runui.py doesn't break
    sudo -u fadr ln -sf /etc/.abcde.conf /etc/fadr/config/abcde.conf

    if [[ $port_flag ]]; then
        echo -e "${RED}Non-default port specified, updating fadr config...${NC}"
        # replace the default 8080 port with the specified port
        sed -E s"/(^WEBSERVER_PORT:) 8080/\1 ${PORT}/" -i /etc/fadr/config/fadr.yaml
    else
        # reset the port number in the config since it's no longer being
        # overwritten which each run of this installer
        sed -E s"/(^WEBSERVER_PORT:) [0-9]+/\1 8080/" -i /etc/fadr/config/fadr.yaml
    fi
}

function setup_autoplay() {
    ##### Add new line to fstab, needed for the autoplay to work.
    echo -e "${RED}Adding fstab entry and creating mount points${NC}"
    for dev in /dev/sr?; do
        if grep -q "${dev}  /mnt${dev}  udf,iso9660  users,noauto,exec,utf8  0  0" /etc/fstab; then
            echo -e "${RED}fstab entry for ${dev} already exists. Skipping...${NC}"
        else
            echo -e "\n${dev}  /mnt${dev}  udf,iso9660  users,noauto,exec,utf8  0  0 \n" | sudo tee -a /etc/fstab
        fi
        sudo mkdir -p "/mnt$dev"
        sudo chown fadr:fadr "/mnt$dev"
    done
}

function setup_syslog_rule() {
    ##### Add syslog rule to route all FADR system logs to /var/log/fadr.log
    if [ -f /etc/rsyslog.d/30-fadr.conf ]; then
        echo -e "${RED}FADR syslog rule found. Overwriting...${NC}"
        sudo rm /etc/rsyslog.d/30-fadr.conf
    fi
    sudo cp /opt/fadr/setup/30-fadr.conf /etc/rsyslog.d/30-fadr.conf
    sudo chown fadr:fadr /etc/rsyslog.d/30-fadr.conf
}

function install_fadrui_service() {
    ##### Install the FADRUI service
    echo -e "${RED}Installing FADR service${NC}"
    sudo mkdir -p /etc/systemd/system
    sudo cp /opt/fadr/setup/fadrui.service /etc/systemd/system/fadrui.service
    sudo chmod 644 /etc/systemd/system/fadrui.service

    # reload the daemon and then start service
    sudo systemctl daemon-reload
    sudo systemctl start fadrui.service
    sudo systemctl enable fadrui.service
    sudo sysctl -p
}

function launch_setup() {
    echo -e "${RED}Launching FADRUI first-time setup${NC}"
    echo "Giving FADRUI a moment to start, standby..."
    sleep 30
    site_addr=$(sudo netstat -tlpn | awk '{ print $4 }' | grep ".*:${PORT}") || true
    if [[ -z "$site_addr" ]]; then
        echo -e "${RED}ERROR: FADRUI site is not running. Run \"sudo systemctl status fadrui\" to find out why${NC}"
    else
        echo -e "${RED}FADRUI site is running on http://$site_addr. Launching setup...${NC}"
        sudo -u fadr nohup xdg-open "http://$site_addr/setup" > /dev/null 2>&1 &
    fi
}

function create_folders() {
    echo -e "${RED}Creating FADR folders${NC}"
    fadr_mkdir "/home/fadr/media/transcode"
    fadr_mkdir "/home/fadr/media/completed"
    fadr_mkdir "/home/fadr/media/raw"
    fadr_mkdir "/home/fadr/logs/progress"
}

function fadr_mkdir() {
    echo -e "Creating $1"
    su - fadr -c "mkdir -p -v $1"
}

# start here
install_os_tools
add_fadr_user
install_fadr_requirements
remove_existing_fadr

install_fadr_dev_env

setup_config_files
setup_autoplay
setup_syslog_rule
install_fadrui_service
create_folders
launch_setup

#advise to reboot
echo
echo -e "${RED}We recommend rebooting your system at this time.${NC}"
echo
