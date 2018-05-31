#!/usr/bin/env bash

#exec 3>&1 4>&2
#trap 'exec 2>&4 1>&3' 0 1 2 3
#exec 1>install_$(date +'%Y%m%dT%H%M%S').log 2>&1

#
# This file is called from the parent node together with the rest of the files from GitHub.
#
# It downloads all dependencies for this version of PlebNet and configures the system
# for PlebNet.
#

# Add locale
echo 'LANG=en_US.UTF-8' > /etc/locale.conf
locale-gen en_US.UTF-8

# No interactivity
DEBIAN_FRONTEND=noninteractive
echo force-confold >> /etc/dpkg/dpkg.cfg
echo force-confdef >> /etc/dpkg/dpkg.cfg

# Upgrade system
apt-get update
# Do not upgrade for now as in some VPS it will cause for example grub to update
# Requiring manual configuration after installation
# && apt-get -y upgrade

apt-get install -y python

# Reinstall pip
apt-get remove --purge python-pip
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install -U wheel setuptools

#(echo "alias pip='python -m pip'" | tee -a ~/.bashrc) && source ~/.bashrc

# Fix paths
echo "fixing path"
(echo "PATH=$PATH:/usr/local/bin:/usr/bin:/root/.local/bin" | tee -a ~/.bashrc)
(echo "export PATH" | tee -a ~/.bashrc) && source ~/.bashrc

# Install dependencies
apt-get install -y \
    python-crypto \
    python-pyasn1 \
    python-twisted \
    python-meliae \
    python-libtorrent \
    python-apsw \
    python-chardet \
    python-cherrypy3 \
    python-m2crypto \
    python-configobj \
    python-netifaces \
    python-leveldb \
    python-decorator \
    python-feedparser \
    python-keyring \
    python-ecdsa \
    python-pbkdf2 \
    python-requests \
    python-protobuf \
    python-dnspython \
    python-jsonrpclib \
    python-networkx \
    python-scipy \
    python-wxtools \
    git \
    python-lxml

pip install pyaes psutil
pip install -U pyopenssl

echo "Install Crypto, pynacl, libsodium"
apt-get install -y python-cryptography \
python-nacl \
python-libnacl \
keyrings.alt

# python-socks needed? It's going to be installed by pip later

apt-get install -y build-essential libssl-dev libffi-dev python-dev software-properties-common
pip install cryptography
pip install pynacl
pip install pysocks
pip install keyrings.alt
pip install libnacl
add-apt-repository -y ppa:chris-lea/libsodium;
echo "deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" >> /etc/apt/sources.list;
echo "deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" >> /etc/apt/sources.list;
apt-get update
apt-get install -y libsodium-dev;

# Update pip to avoid locale errors in certain configurations
#echo "upgrading pip"
#LC_ALL=en_US.UTF-8 pip install --upgrade pip
#echo "done upgrading pip"

cd $HOME
[ ! -d "PlebNet" ] && git clone -b master-dev https://github.com/vwigmore/PlebNet
[ ! -d "cloudomate" ] && git clone -b master https://github.com/codesalad/cloudomate
python -m pip install --upgrade ./cloudomate
python -m pip install --upgrade ./PlebNet
cd PlebNet
git submodule update --init --recursive tribler
pip install ./tribler/electrum
cd /root
plebnet setup >> plebnet.log 2>&1

cron plebnet check
echo "* * * * * root /usr/local/bin/plebnet check >> plebnet.log 2>&1" > /etc/cron.d/plebnet
