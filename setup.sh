#!/bin/bash

echo "[+] Updating system..."
apt update -y

echo "[+] Installing dependencies..."
apt install -y python3 python3-pip sudo openssh-server

echo "[+] Creating user..."
useradd -m aria_admin
echo "aria_admin:Str0ngPassphrase2025!" | chpasswd

echo "[+] Configuring sudo..."
echo "aria_admin ALL=(ALL) NOPASSWD: /usr/bin/python3" >> /etc/sudoers

echo "[+] Creating flags..."
echo "HTB{example_user_flag_md5}" > /home/aria_admin/user.txt
echo "HTB{example_root_flag_md5}" > /root/root.txt

chown root:aria_admin /home/aria_admin/user.txt
chmod 644 /home/aria_admin/user.txt

chown root:root /root/root.txt
chmod 640 /root/root.txt

echo "[+] Creating credentials file..."
mkdir -p /opt
echo "aria_admin:Str0ngPassphrase2025!" > /opt/creds.txt
chown root:root /opt/creds.txt
chmod 640 /opt/creds.txt

echo "[+] Setup complete."
