#!/bin/bash
docker run -d \
    -p "8080:8080" \
    -e FADR_UID="<id -u fadr>" \
    -e FADR_GID="<id -g fadr>" \
    -v "<path_to_fadr_user_home_folder>:/home/fadr" \
    -v "<path_to_music_folder>:/home/fadr/music" \
    -v "<path_to_logs_folder>:/home/fadr/logs" \
    -v "<path_to_media_folder>:/home/fadr/media" \
    -v "<path_to_config_folder>:/etc/fadr/config" \
    --device="/dev/sr0:/dev/sr0" \
    --device="/dev/sr1:/dev/sr1" \
    --device="/dev/sr2:/dev/sr2" \
    --device="/dev/sr3:/dev/sr3" \
    --privileged \
    --restart "always" \
    --name "fadr-rippers" \
    --cpuset-cpus='2,3,4,5,6,7...' \
    IMAGE_NAME
