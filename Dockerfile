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

# Create user aria (matches app.py)
RUN useradd -m aria && \
    echo "aria:Str0ngPassphrase2025!" | chpasswd

# Configure sudo — intentional privesc path
RUN echo "aria ALL=(ALL) NOPASSWD: /usr/bin/python3" >> /etc/sudoers

# Create flags
RUN mkdir -p /home/aria && \
    mkdir -p /root

COPY flags/user.txt /home/aria/user.txt
COPY flags/root.txt /root/root.txt

RUN chown root:aria /home/aria/user.txt && \
    chmod 644 /home/aria/user.txt && \
    chown root:root /root/root.txt && \
    chmod 640 /root/root.txt

# Disable root SSH login
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Wipe bash history
RUN ln -sf /dev/null /home/aria/.bash_history && \
    ln -sf /dev/null /root/.bash_history

# Copy app
WORKDIR /app
COPY app.py .
COPY requirements.txt .
RUN pip3 install -r requirements.txt

EXPOSE 5000 22

CMD service ssh start && python3 app.py
