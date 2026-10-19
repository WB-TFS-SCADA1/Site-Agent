"""Offline planning by default; live mode is explicit and advisory only."""

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

from .instructions import INSTRUCTIONS, POLICY_VERSION
from .schemas import RequestError, canonical_json, load_request
from .tools import get_build_capabilities


def make_report(request: dict, mode: str) -> dict:
    missing = [key for key in ("donor_backup_ref", "ipc_address", "plc_address")
               if request[key] is None]
    return {
        "schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "request_sha256": hashlib.sha256(canonical_json(request).encode()).hexdigest(),
        "policy_version": POLICY_VERSION,
        "policy_sha256": hashlib.sha256(INSTRUCTIONS.encode()).hexdigest(),
        "status": "NEEDS_INPUT" if missing else "BLOCKED_NOT_IMPLEMENTED",
        "missing_fields": missing,
        "steps": get_build_capabilities(),
        "artifacts": [],
        "native_validation_performed": False,
        "production_actions_performed": False,
        "model": None,
        "model_advice": None,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="New JSON report path; existing files are never overwritten")
    parser.add_argument("--mode", choices=("offline", "live"), default="offline")
    args = parser.parse_args(argv)
    try:
        request = load_request(args.request)
    except (RequestError, OSError) as error:
        message = str(error) if isinstance(error, RequestError) else "Cannot read request file"
        print(message, file=sys.stderr)
        return 2
    # Reserve the output before a paid call; do not spend money on an unusable destination.
    try:
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError:
        print("Cannot create output; use a new file in an existing directory", file=sys.stderr)
        return 2
    report = make_report(request, args.mode)
    exit_code = 0
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        if args.mode == "live":
            key = os.environ.get("OPENAI_API_KEY", "").strip()
            model = os.environ.get("OPENAI_MODEL", "").strip()
            if not key:
                report["status"] = "AWAITING_AUTH"
                exit_code = 2
            elif not model:
                report["status"] = "CONFIGURATION_REQUIRED"
                report["error"] = "Set OPENAI_MODEL to an explicitly selected, available model"
                exit_code = 2
            else:
                try:
                    from .sdk_adapter import get_live_advice
                    report["model"] = model
                    report["model_advice"] = asyncio.run(get_live_advice(request, key, model))
                except ImportError:
                    report["status"] = "DEPENDENCY_MISSING"
                    report["error"] = "Install the live SDK requirements"
                    exit_code = 2
                except Exception as error:
                    # Provider errors may contain request data. Do not echo their contents.
                    report["status"] = ("AWAITING_AUTH" if type(error).__name__ == "AuthenticationError"
                                        else "MODEL_FAILED")
                    report["error"] = "Model request failed; check authentication, connectivity and model access"
                    exit_code = 3
                except KeyboardInterrupt:
                    report["status"] = "INTERRUPTED"
                    exit_code = 130
        json.dump(report, output, indent=2)
        output.write("\n")
    print(report["status"])
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
