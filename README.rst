*******
Plebnet
*******

|jenkins_build|

*A self-replicating autonomous Tribler exit-node*

Documentation
=============
 - The full report regarding this project can be found `here <https://github.com/Tribler/tribler/files/2025931/Bachelor_Project_2018_BotNet.pdf>`_
 - The main issue regarding this project can be found `here <https://github.com/Tribler/tribler/issues/2925>`_

Description
===========
After the first instance is installed on a VPS, PlebNet will run Tribler as an exit-node and earn credits,
which will be used to acquire new VPS instances for the next generation PlebNet agents. This should eventually create a
community of exit-nodes for Tribler, thus creating a reliable and sufficiently large capacity for anonymous data
transfer through the Tribler network

Initialisation
==============
The first instance can be installed by downloading the file create-child.sh in Plebnet/plebnet/clone and call:

.. code-block:: console

./create-child.sh <parameter> <value>

::

   Usage: ./create-child.sh <parameter> <value>
   -h --help 		           Shows this help message
   -i --ip 		             Ip address of the server to run install on
   -p --password 	   	    Root password of the server
   -t --testnet 		        Install agent in testnet mode (default 0)
   -e --exitnode 	   	    Run as exitnode for tribler
   -conf --config    		   (optional) VPN configuration file (.ovpn)
                          Requires the destination config name.
                          Example: -conf source_config.ovpn dest_config.ovpn
   -cred --credentials 	  (optional) VPN credentials file (.conf)
                          Requires the destination credentials name.
                          Example -cred source_credentials.conf dest_credentials.conf
   -b --branch 		         (optional) Branch of code to install from (default master)

    
This installs all dependencies (Tribler, Electrum, Cloudomate and ofcourse PlebNet).
After installation the "plebnet setup" is called and a cron job is set up to regularly call "plebnet check".

This check function checks whether the agent instance has acquired sufficient funds to buy a new VPS and spawn a new
child instance. If this is the case, the PlebNet agent will execute the previously mentioned steps on the new server and
the community has welcomed a newborn.


Running the code once
=====================
For running PlebNet locally, the following steps are necessary:

- All dependencies installed via the create-child.sh script, must be installed manually.
- Download PlebNet and all submodules by running the following command:

.. code-block:: console

    git clone --recurse-submodules git://github.com/Tribler/PlebNet.git
    
- Go to the main folder and execute the following command:

.. code-block:: console

    pip install .

Usage
-----

::

   usage: plebnet [-h]
                  {setup,check,conf,irc}
                  ...

   positional arguments:
    {setup,check,conf,irc}
       setup               Run the setup of PlebNet
       check               Checks if the plebbot is able to clone
       conf                Allows changing the configuration files
       irc                 Provides access to the IRC client

   optional arguments:
     -h, --help            show this help message and exit


   usage: plebnet setup [-h] [--testnet] [--exitnode]

   optional arguments:
     -h, --help  show this help message and exit
     --testnet   Use TBTC instead of BTC
     --exitnode  Run as exitnode for Tribler


   usage: plebnet irc [-h] {status,start,stop,restart}

   positional arguments:
     {status,start,stop,restart}
       status              Provides information regarding the status of the IRC Client
       start               Starts the IRC Client
       stop                Stops the IRC Client
       restart             Restarts the IRC Client

   optional arguments:
     -h, --help            show this help message and exit


.. |jenkins_build| image:: https://jenkins.tribler.org/job/GH_PlebNet/badge/icon
    :target: https://jenkins.tribler.org/job/GH_PlebNet
    :alt: Build status on Jenkins
