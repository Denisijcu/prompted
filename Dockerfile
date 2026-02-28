FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    sudo \
    openssh-server \
    nano \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create SSH directory
RUN mkdir /var/run/sshd

# Create user
RUN useradd -m aria_admin && \
    echo "aria_admin:Str0ngPassphrase2025!" | chpasswd

# Configure sudo (EASY privesc)
RUN echo "aria_admin ALL=(ALL) NOPASSWD: /usr/bin/python3" >> /etc/sudoers

# Create flags
RUN mkdir -p /home/aria_admin && \
    mkdir -p /root

COPY flags/user.txt /home/aria_admin/user.txt
COPY flags/root.txt /root/root.txt

RUN chown root:aria_admin /home/aria_admin/user.txt && \
    chmod 644 /home/aria_admin/user.txt && \
    chown root:root /root/root.txt && \
    chmod 640 /root/root.txt

# Create creds file (used in exploit path)
RUN mkdir -p /opt && \
    echo "aria_admin:Str0ngPassphrase2025!" > /opt/creds.txt && \
    chown root:root /opt/creds.txt && \
    chmod 640 /opt/creds.txt

# Set up SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Copy app
WORKDIR /app
COPY app.py .
COPY requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 5000 22

CMD service ssh start && python3 app.py
