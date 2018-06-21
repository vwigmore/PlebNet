#!/bin/bash

# Quickly resetting a server/container by removing configuration folders
# and uninstalling PlebNet and cloudomate

declare -a files=(~/.Tribler
                    ~/.config
                    ~/PlebNet
                    ~/cloudomate
                    ~/plebnet*
                    ~/get-pip.py
                    ~/install.sh
                    )

for item in "${files[@]}"
do 
    echo "removing ${item}" && rm -rf "${item}"
done

echo "uninstalling plebnet" && pip uninstall -y plebnet 
echo "uninstalling cloudomate" && pip uninstall -y cloudomate 
