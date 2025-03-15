#!/usr/bin/env bash
set -eo pipefail

RED='\033[1;31m'
NC='\033[0m' # No Color
FORK=automaticrippingmachine
TAG=latest
function usage() {
    echo -e "\nUsage: docker_setup.sh [OPTIONS]"
    echo -e " -f <fork>\tSpecify the fork to pull from on DockerHub. \n\t\tDefault is \"$FORK\""
    echo -e " -t <tag>\tSpecify the tag to pull from on DockerHub. \n\t\tDefault is \"$TAG\""
}

while getopts 'f:t:' OPTION
do
    case $OPTION in
    f)    FORK=$OPTARG
          ;;
    t)    TAG=$OPTARG
          ;;
    ?)    usage
          exit 2
          ;;
    esac
done
IMAGE="$FORK/automatic-ripping-machine:$TAG"

function install_reqs() {
    apt update -y && apt upgrade -y
    apt install -y curl lsscsi
}

function add_fadr_user() {
    echo -e "${RED}Adding fadr user${NC}"
    # create fadr group if it doesn't already exist
    if ! [[ "$(getent group fadr)" ]]; then
        groupadd fadr
    else
        echo -e "${RED}fadr group already exists, skipping...${NC}"
    fi

    # create fadr user if it doesn't already exist
    if ! id fadr >/dev/null 2>&1; then
        useradd -m fadr -g fadr
        passwd fadr
    else
        echo -e "${RED}fadr user already exists, skipping...${NC}"
    fi
    usermod -aG cdrom,video fadr
}

function launch_setup() {
    # install docker
    if [ -e /usr/bin/docker ]; then
        echo -e "${RED}Docker installation detected, skipping...${NC}"
        echo -e "${RED}Adding user fadr to docker user group${NC}"
        usermod -aG docker fadr
    else
        echo -e "${RED}Installing Docker${NC}"
        # the convenience script auto-detects OS and handles install accordingly
        curl -sSL https://get.docker.com | bash
        echo -e "${RED}Adding user fadr to docker user group${NC}"
        usermod -aG docker fadr
    fi
}

function pull_image() {
    echo -e "${RED}Pulling image from $IMAGE${NC}"
    sudo -u fadr docker pull "$IMAGE"
}

function setup_mountpoints() {
    echo -e "${RED}Creating mount points${NC}"
    for dev in /dev/sr?; do
        mkdir -p "/mnt$dev"
    done
    chown fadr:fadr /mnt/dev/sr*
}

function save_start_command() {
    url="https://raw.githubusercontent.com/automatic-ripping-machine/automatic-ripping-machine/main/scripts/docker/start_fadr_container.sh"
    cd ~fadr
    if [ -e start_fadr_container.sh ]
    then
        echo -e "'start_fadr_container.sh' already exists. Backing up..."
        sudo mv ./start_fadr_container.sh ./start_fadr_container.sh.bak
    fi
    sudo -u fadr curl -fsSL "$url" -o start_fadr_container.sh
    chmod +x start_fadr_container.sh
    sed -i "s|IMAGE_NAME|${IMAGE}|" start_fadr_container.sh
}


# start here
install_reqs
add_fadr_user
launch_setup
pull_image
setup_mountpoints
save_start_command

echo -e "${RED}Installation complete. A template command to run the FADR container is located in: $(echo ~fadr) ${NC}"
