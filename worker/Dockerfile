FROM site-agent-base:codex-sdk-0.156.1
USER 0:0
ARG DEBIAN_FRONTEND=noninteractive
RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d \
 && chmod 0755 /usr/sbin/policy-rc.d \
 && apt-get update \
 && apt-get install -y --no-install-recommends openssh-server openssh-client curl jq rsync zip unzip file iproute2 git default-jdk-headless bubblewrap xvfb fontconfig fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/* /etc/ssh/ssh_host_* \
 && usermod --shell /bin/bash --password '*' agent \
 && install -d -m 0755 /run/sshd /etc/ssh/authorized_keys \
 && install -d -o 1000 -g 0 -m 0700 /var/lib/site-agent-ssh \
 && install -d -o 1000 -g 0 -m 0750 /home/agent /workspace/work \
 && printf 'IGN04-Site-Agent-Jail\n' > /etc/site-agent-worker-id
COPY sshd_config /etc/ssh/sshd_config.worker
COPY entrypoint.sh /usr/local/bin/site-agent-worker-entrypoint
RUN chmod 0755 /usr/local/bin/site-agent-worker-entrypoint
ENV HOME=/home/agent
WORKDIR /workspace/work
USER 1000:0
EXPOSE 2222
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/site-agent-worker-entrypoint"]
