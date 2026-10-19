"""Typed integration points. These functions do not contact external systems."""

OPERATIONS = (
    ("acquire_donor", "Resolve the selected donor and copy its verified backup"),
    ("build_artifacts", "Transform a private copy using a versioned ignProjects profile"),
    ("validate_native", "Validate the final files in an OS-isolated Ignition lab"),
    ("package_release", "Package verified artifacts and manual import instructions"),
)


def get_build_capabilities() -> list[dict[str, str]]:
    return [{"operation": name, "description": description, "status": "NOT_IMPLEMENTED"}
            for name, description in OPERATIONS]


def request_build(operation: str) -> dict[str, str]:
    """Future coordinator adapter; fail closed until an implementation is reviewed."""
    if operation not in {name for name, _ in OPERATIONS}:
        raise ValueError("Unknown build operation")
    return {"operation": operation, "status": "NOT_IMPLEMENTED"}
