#!/bin/bash
echo "Installing packages for Workshop"
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi
apt install python3
apt install python3-pip
pip3 install pygame