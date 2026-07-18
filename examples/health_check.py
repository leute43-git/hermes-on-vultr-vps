"""Exit silently when healthy; print only actionable failures."""

from __future__ import annotations

import subprocess
import sys


SERVICES = ("hermes.service", "digest.service")


def inactive_services() -> list[str]:
    failed = []
    for service in SERVICES:
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", service],
            check=False,
            timeout=10,
        )
        if result.returncode != 0:
            failed.append(service)
    return failed


if __name__ == "__main__":
    failures = inactive_services()
    if failures:
        print("INACTIVE: " + ", ".join(failures))
        sys.exit(1)

