"""Small, dependency-free request contract for the starter."""

import ipaddress
import json
import re
from pathlib import Path

MAX_REQUEST_BYTES = 65536
FIELDS = {"schema_version", "job_type", "donor_site", "target_site",
          "donor_backup_ref", "ipc_address", "plc_address", "changes"}


class RequestError(ValueError):
    """An input failed validation; messages never include submitted values."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RequestError("Duplicate JSON field")
        result[key] = value
    return result


def load_request(path: Path) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(MAX_REQUEST_BYTES + 1)
    if len(raw) > MAX_REQUEST_BYTES:
        raise RequestError("Request exceeds 64 KiB")
    try:
        value = json.loads(raw, object_pairs_hook=_unique_object)
    except (ValueError, UnicodeError) as error:
        raise RequestError("Request must be valid JSON with unique fields") from error
    return validate_request(value)


def validate_request(value) -> dict:
    if not isinstance(value, dict) or set(value) - FIELDS:
        raise RequestError("Expected a request object containing only documented fields")
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise RequestError("schema_version must be 1")
    if value.get("job_type") != "clone_site_artifacts":
        raise RequestError("Only clone_site_artifacts is supported")
    result = {"schema_version": 1, "job_type": "clone_site_artifacts"}
    for field in ("donor_site", "target_site"):
        name = value.get(field)
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}", name):
            raise RequestError(field + " must be a name of 1–80 characters")
        result[field] = name.strip()
    if result["donor_site"].casefold() == result["target_site"].casefold():
        raise RequestError("Donor and destination must be distinct")
    reference = value.get("donor_backup_ref")
    if reference is not None and (not isinstance(reference, str) or
            not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", reference)):
        raise RequestError("donor_backup_ref must be an opaque reference, not a path or URL")
    result["donor_backup_ref"] = reference
    for field in ("ipc_address", "plc_address"):
        address = value.get(field)
        if address is not None:
            if not isinstance(address, str):
                raise RequestError(field + " must be an IP address or null")
            try:
                address = str(ipaddress.ip_address(address))
            except ValueError as error:
                raise RequestError(field + " must be an IP address or null") from error
        result[field] = address
    changes = value.get("changes", [])
    if not isinstance(changes, list) or len(changes) > 50 or any(
        not isinstance(change, str) or not 1 <= len(change.strip()) <= 500
        for change in changes
    ):
        raise RequestError("changes must contain at most 50 descriptions of 1–500 characters")
    result["changes"] = [change.strip() for change in changes]
    return result


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
