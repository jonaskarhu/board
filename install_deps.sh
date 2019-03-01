#!/bin/bash

# Abort script if something goes wrong
set -e

echo "Installing dependencies..."
sudo apt install -y python3-pil.imagetk
sudo apt install -y python3-pip
sudo pip3 install --upgrade requests
echo "Installing dependencies done."

echo ""

if [ ! -e secrets.py ]; then
    echo "No secret.py with key and secret exist for Västtrafik API."
    echo "Go to developer.vasttrafik.se to get your key and secret."
    echo "Enter API KEY"
    read KEY
    echo "Enter API SECRET"
    read SECRET
    echo "Creating secrets.py..."
    touch secrets.py
    echo -e '#!/usr/bin/env python3' >> secrets.py
    echo -e '# coding=utf-8' >> secrets.py
    echo -e "" >> secrets.py
    echo -e "def get_key():" >> secrets.py
    echo -e "    return \"$KEY\"" >> secrets.py
    echo -e "" >> secrets.py
    echo -e "def get_secret():" >> secrets.py
    echo -e "    return \"$SECRET\"" >> secrets.py
    echo "secrets.py created."
fi

exit 0
