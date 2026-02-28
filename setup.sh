#!/bin/bash
# Prompted — HTB Machine Setup Script
# Vertex Coders LLC | Denis Sanchez Leyva

set -e

echo "[+] Updating system..."
apt update -y

echo "[+] Installing dependencies..."
apt install -y python3 python3-pip sudo openssh-server nano net-tools iputils-ping

echo "[+] Creating user aria..."
useradd -m aria 2>/dev/null || echo "  [!] User aria already exists, skipping"
echo "aria:Str0ngPassphrase2025!" | chpasswd

echo "[+] Configuring sudo privesc path..."
echo "aria ALL=(ALL) NOPASSWD: /usr/bin/python3" >> /etc/sudoers

echo "[+] Creating flags..."
mkdir -p /home/aria /root

echo "HTB{pr0mpt_inj3ct10n_t0_sst1_rce}" > /home/aria/user.txt
echo "HTB{y0u_3sc4l4t3d_thr0ugh_th3_t3mpl4t3}" > /root/root.txt

chown root:aria /home/aria/user.txt
chmod 644 /home/aria/user.txt

chown root:root /root/root.txt
chmod 640 /root/root.txt

echo "[+] Wiping bash history..."
ln -sf /dev/null /home/aria/.bash_history
ln -sf /dev/null /root/.bash_history

echo "[+] Configuring SSH..."
mkdir -p /var/run/sshd
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

echo "[+] Installing Python dependencies..."
pip3 install Flask==3.0.2 gunicorn==21.2.0 Werkzeug==3.0.1

echo ""
echo "[+] Setup complete."
echo "    User flag : /home/aria/user.txt"
echo "    Root flag : /root/root.txt"
echo "    SSH user  : aria"
echo "    SSH pass  : Str0ngPassphrase2025!"
echo "    App port  : 5000"
