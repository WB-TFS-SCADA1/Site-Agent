#!/usr/bin/env python3
"""Run a command or transfer a file through a single-use Warpgate ticket."""
import argparse
from datetime import datetime, timedelta, timezone
import getpass
import os
from pathlib import Path, PurePosixPath
import shlex
import sys
import time
from urllib.parse import urlsplit

import paramiko
import requests

ORIGIN = "https://warp.wbinfra.com/@warpgate"
TARGET = "IGN04-Site-Agent-Jail"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--token-file", type=Path)
    p.add_argument("--username", default=os.environ.get("WARPGATE_USERNAME"))
    p.add_argument("--origin", default=os.environ.get("WARPGATE_ORIGIN", ORIGIN))
    p.add_argument("--target", default=os.environ.get("WARPGATE_TARGET", TARGET))
    p.add_argument("--ssh-port", type=int, default=2222)
    p.add_argument("--known-hosts", type=Path)
    p.add_argument("--timeout", type=int, default=120)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--command")
    action.add_argument("--upload", nargs=2, metavar=("LOCAL", "REMOTE"))
    action.add_argument("--download", nargs=2, metavar=("REMOTE", "LOCAL"))
    args = p.parse_args()
    if not args.username:
        p.error("set --username or WARPGATE_USERNAME to your authorized Warpgate identity")
    endpoint = urlsplit(args.origin)
    if (endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or
            endpoint.password or endpoint.query or endpoint.fragment):
        p.error("--origin must be an HTTPS Warpgate URL without credentials, query or fragment")
    if not 1 <= args.ssh_port <= 65535:
        p.error("--ssh-port must be between 1 and 65535")
    if not 1 <= args.timeout <= 1800:
        p.error("timeout must be between 1 and 1800 seconds")
    if args.upload or args.download:
        remote = args.upload[1] if args.upload else args.download[0]
        rp = PurePosixPath(remote)
        if ".." in rp.parts or not any(rp.is_relative_to(root) for root in
                                       ("/workspace/work", "/home/agent")):
            p.error("Use an absolute remote path inside /workspace/work or /home/agent")
    token = (args.token_file.read_text().strip() if args.token_file else
             os.environ.get("WARPGATE_API_TOKEN") or getpass.getpass("Warpgate API token: "))
    session = requests.Session()
    session.trust_env = False
    session.headers["x-warpgate-token"] = token

    def api(method, path, body=None):
        r = session.request(method, args.origin.rstrip("/") + path, json=body,
                            timeout=(10, 30), allow_redirects=False)
        if r.status_code not in (200, 201, 204):
            raise RuntimeError(f"Warpgate {method} {path}: HTTP {r.status_code}")
        return r.json() if r.content else None

    ticket = None
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    if args.known_hosts:
        client.load_host_keys(str(args.known_hosts))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        ticket = api("POST", "/admin/api/tickets", {
            "username": args.username, "target_name": args.target,
            "expiry": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
            "number_of_uses": 1, "description": "Dedicated commissioning workspace access",
        })
        client.connect(endpoint.hostname, port=args.ssh_port,
                       username="ticket-" + ticket["secret"], password="ticket",
                       look_for_keys=False, allow_agent=False,
                       timeout=15, banner_timeout=30, auth_timeout=30)
        if args.command is not None:
            cmd = "/bin/bash -c " + shlex.quote("cd /workspace/work && " + args.command)
            stdin, stdout, stderr = client.exec_command(cmd, timeout=args.timeout)
            stdin.close()
            channel = stdout.channel
            deadline = time.monotonic() + args.timeout
            while True:
                if channel.recv_ready():
                    sys.stdout.buffer.write(channel.recv(65536)); sys.stdout.buffer.flush()
                if channel.recv_stderr_ready():
                    sys.stderr.buffer.write(channel.recv_stderr(65536)); sys.stderr.buffer.flush()
                if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                    return channel.recv_exit_status()
                if time.monotonic() >= deadline:
                    raise TimeoutError("Local command wait expired; remote jobs may still be running")
                time.sleep(0.02)
        with client.open_sftp() as sftp:
            sftp.get_channel().settimeout(args.timeout)
            if args.upload:
                sftp.put(args.upload[0], remote)
            else:
                sftp.get(remote, args.download[1])
        print("SFTP transfer completed")
        return 0
    finally:
        client.close()
        if ticket:
            try:
                api("DELETE", "/admin/api/tickets/" + ticket["ticket"]["id"])
            except Exception:
                print("Ticket cleanup failed; its configured expiry still applies.", file=sys.stderr)
        session.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Worker connection failed: {type(e).__name__}. Check configuration and access.", file=sys.stderr)
        sys.exit(1)
