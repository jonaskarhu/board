#!/bin/bash

set -e

if grep 'display_rotate' /boot/config.txt; then
    echo "Screen rotation already exists. Exiting."
    exit 1
else
    echo "Adding display_rotate=2 to /boot/config.txt"
    sudo echo "" >> /boot/config.txt
    sudo echo "display_rotate=2" >> /boot/config.txt
    echo "Done."
    exit 0
fi

exit 0

