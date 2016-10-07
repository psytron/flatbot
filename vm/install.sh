#!/bin/bash


#### THIS INSTALL SCRIPT SHOULD SET UP A BRAND NEW UBUNTU 16.04 INSTANCE WITH
echo "Starting Fresh FLatbot Install"
echo 'Start with ensuring all directories are in place'
sudo mkdir /home/deploy/flatbot
sudo mkdir /home/deploy/flatbot/flatbot.git


#### ADD USERS AND GROUPS
echo " "
echo " Adding Users and Group Deploy..."
cd /home/
sudo adduser deploy
sudo usermod -aG deploy $USER
sudo usermod -aG www-data deploy

#### CREATE SUB USERS ( move to non-repo file )
# echo 'creating sub users'
# sudo adduser hurley   # Hurley SFTP
# sudo adduser mammoth  # Mammoth VPN
# sudo adduser beaumont # Beaumont VPN


#### VIRTUAL ENV
echo " "
echo " Installing Python Pip..and virtual env."
sudo apt-get -y install python-pip
sudo pip install virtualenv
cd /home/deploy/octopus/
virtualenv -p python3 envoctopus
source envoctopus/bin/activate
echo "After Running Virtual env..."
python --version
pip --version
cd octopus
pip install -r requirements.txt


#### START UP FLATBOT
#### Transfer SYSTEMD STartup File for Octopus Process
echo "Copying System D startup files..."
sudo cp /home/deploy/flatbot/flatbot/vm/systemd/flatbot.service /etc/systemd/system/flatbot.service

# ENABLE SYSTEM D Services after adding configs ( required on Ubuntu 16.04 )
sudo systemctl enable flatbot
sudo systemctl start flatbot



# SSHGUARD
# show blocked 
# iptables -nvL sshguard
# Removing an address in the sshguard chain
# sudo /usr/sbin/invoke-rc.d sshguard restart


# own as logged in user
# sudo chown -R $USER:$USER wellopp_website.git




