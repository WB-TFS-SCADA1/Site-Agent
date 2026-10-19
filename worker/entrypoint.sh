#!/bin/sh
set -eu
umask 077
key=/var/lib/site-agent-ssh/ssh_host_ed25519_key
if [ ! -f "$key" ]; then
    ssh-keygen -q -t ed25519 -N '' -C IGN04-Site-Agent-Jail -f "$key"
fi
/usr/sbin/sshd -t -f /etc/ssh/sshd_config.worker
exec /usr/sbin/sshd -D -e -f /etc/ssh/sshd_config.worker
