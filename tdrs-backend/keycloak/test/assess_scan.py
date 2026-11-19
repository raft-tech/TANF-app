"""Fail-closed, image-specific applicability assessments; never alter raw scans."""

import collections
import hashlib
import json
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


RULES = {
    ("CVE-2026-16742", "libsystemd0", "257.13-1~deb13u1+dhi2"): {
        "absent_files": {"systemd-homed", "systemd-homework"},
        "absent_packages": {"systemd-homed"},
        "justification": "component_not_present",
        "reason": ("The flaw is in systemd-homed/homework, neither of which is shipped; "
                   "libsystemd0 is not that service."),
        "reference": "https://github.com/systemd/systemd/security/advisories/GHSA-jm29-p7hh-vjhv",
    },
    ("CVE-2025-69720", "libtinfo6", "6.5+20250216-2+deb13u0+dhi5"): {
        "absent_files": {"infocmp"},
        "absent_packages": {"ncurses-bin"},
        "justification": "component_not_present",
        "reason": "The flaw is in progs/infocmp.c; the image ships libtinfo6 but no infocmp executable.",
        "reference": "https://security-tracker.debian.org/tracker/CVE-2025-69720",
    },
    ("CVE-2026-54369", "libacl1", "2.3.2-2+deb13u0+dhi2"): {
        "absent_files": {"setfacl", "getfacl"},
        "absent_packages": {"acl"},
        "justification": "inline_mitigations_already_exist",
        "reason": ("ACL remains unpatched. The entrypoint rejects root/mismatched UIDs and all usable "
                   "capability sets before file operations; the image has no set-ID or file-capability "
                   "escalation helpers. Startup cp uses trusted operator-selected realm paths in protected "
                   "directories, not request-selected paths; no privileged ACL service is exposed."),
        "reference": "https://security-tracker.debian.org/tracker/CVE-2026-54369",
    },
}


def inspect_filesystem(archive: Path) -> dict[str, Any]:
    """Inspect an exported filesystem without extracting or executing image code."""
    names = set()
    privileged = []
    contents = {}
    directories = {}
    paths = {
        "etc/os-release", "usr/lib/os-release", "var/lib/dpkg/status",
        "opt/keycloak/entrypoint.sh", "opt/keycloak/check-runtime-security.sh",
        "opt/keycloak/select-realm-config.sh", "opt/keycloak/normalize-login-gov-key.sh",
    }
    with tarfile.open(archive) as source:
        for member in source:
            name = str(PurePosixPath(member.name.removeprefix("./")))
            if name.startswith("/") or ".." in PurePosixPath(name).parts:
                raise ValueError("Unsafe filesystem archive path")
            names.add(PurePosixPath(name).name)
            if member.isdir():
                directories[name] = (member.uid, member.mode)
            if (not member.isdir() and member.mode & 0o6000) or any(
                "security.capability" in key for key in member.pax_headers
            ):
                privileged.append(name)
            if name in paths and member.isfile():
                if member.size > 2_000_000:
                    raise ValueError("Unexpectedly large security evidence file")
                contents[name] = source.extractfile(member).read()
    return {"names": names, "privileged": privileged, "contents": contents, "directories": directories}


def assess(report: dict, image: dict, filesystem: dict, source_directory: Path) -> dict:
    """Only resolve reviewed package/version pairs with all composition checks met."""
    results = report.get("Results", [])
    if not any(result.get("Class") == "os-pkgs" for result in results):
        raise ValueError("OS package analysis is missing")
    if not any(result.get("Type") == "jar" for result in results):
        raise ValueError("Java dependency analysis is missing")
    config = image["Config"]
    contents = filesystem["contents"]
    package_status = contents.get("var/lib/dpkg/status", b"").decode()
    packages = {}
    for paragraph in package_status.split("\n\n"):
        fields = dict(line.split(": ", 1) for line in paragraph.splitlines() if ": " in line and not line[0].isspace())
        if fields.get("Status") == "install ok installed":
            packages[fields.get("Package")] = fields.get("Version")
    operating_system = report.get("Metadata", {}).get("OS", {})
    composition_matches = (
        image.get("Os") == "linux"
        and image.get("Architecture") in {"amd64", "arm64"}
        and operating_system.get("Family") == "debian"
        and str(operating_system.get("Name", "")).split(".")[0] == "13"
        and config.get("User") == "65532:65532"
        and config.get("Entrypoint") == ["/opt/keycloak/entrypoint.sh"]
        and not filesystem["privileged"]
        and all(
            name in filesystem["directories"]
            and filesystem["directories"][name][0] in {0, 65532}
            and not filesystem["directories"][name][1] & 0o022
            for name in ("opt", "opt/keycloak", "opt/keycloak/realm-configs",
                         "opt/keycloak/data", "opt/keycloak/data/import")
        )
    )
    # Match the entire reviewed startup/guard scripts, not a marker an unrelated
    # image could contain. Require the guard before any startup file operation.
    entrypoint = (source_directory / "entrypoint.sh").read_bytes()
    guard = (source_directory / "check-runtime-security.sh").read_bytes()
    composition_matches = composition_matches and (
        contents.get("opt/keycloak/entrypoint.sh") == entrypoint
        and contents.get("opt/keycloak/check-runtime-security.sh") == guard
        and all(
            contents.get(f"opt/keycloak/{name}") == (source_directory / name).read_bytes()
            for name in ("select-realm-config.sh", "normalize-login-gov-key.sh")
        )
        and entrypoint.startswith(
            b"#!/bin/bash\nset -euo pipefail\n\n"
            b"# Inspect this shell, not a child whose exec could drop the parent's capabilities.\n"
            b"source /opt/keycloak/check-runtime-security.sh\nrequire_runtime_security\n"
        )
    )
    findings = []
    statements = []
    raw_counts = collections.Counter()
    unresolved_counts = collections.Counter()
    for result in results:
        for vulnerability in result.get("Vulnerabilities", []):
            severity = vulnerability["Severity"]
            raw_counts[severity] += 1
            key = tuple(vulnerability.get(field) for field in ("VulnerabilityID", "PkgName", "InstalledVersion"))
            rule = RULES.get(key)
            purl = vulnerability.get("PkgIdentifier", {}).get("PURL", "")
            applicable = bool(
                rule and composition_matches and result.get("Class") == "os-pkgs" and severity == "HIGH"
                and packages.get(key[1]) == key[2]
                and not rule["absent_files"].intersection(filesystem["names"])
                and not rule["absent_packages"].intersection(packages)
                and purl.startswith(f"pkg:deb/debian/{key[1]}@")
            )
            finding = {"cve": key[0], "package": key[1], "version": key[2], "severity": severity}
            if applicable:
                finding.update(status="not_affected", reason=rule["reason"], reference=rule["reference"])
                statements.append({
                    "vulnerability": {"name": key[0]},
                    "products": [{"@id": image["Id"], "subcomponents": [{"@id": purl}]}],
                    "status": "not_affected", "justification": rule["justification"],
                    "impact_statement": rule["reason"], "status_notes": rule["reference"],
                })
            else:
                finding["status"] = "unresolved"
                unresolved_counts[severity] += 1
            findings.append(finding)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "image_id": image["Id"], "platform": f"linux/{image['Architecture']}",
        "raw_counts": dict(raw_counts), "unresolved_counts": dict(unresolved_counts),
        "passed": not (unresolved_counts["HIGH"] or unresolved_counts["CRITICAL"]),
        "composition_matches": bool(composition_matches), "findings": findings,
        "guard_sha256": hashlib.sha256(guard).hexdigest(),
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "vex": {"@context": "https://openvex.dev/ns/v0.2.0", "@id": f"urn:tdp:keycloak:{image['Id']}",
                "author": "TDP Keycloak image maintainers", "timestamp": now, "version": 1,
                "statements": statements},
    }


def main() -> None:
    """Retain the assessment and scoped VEX alongside the original raw report."""
    directory = Path(sys.argv[1])
    assessment = assess(
        json.loads((directory / "scan.json").read_text()),
        json.loads((directory / "image.json").read_text())[0],
        inspect_filesystem(directory / "rootfs.tar"), Path(__file__).resolve().parents[1],
    )
    (directory / "assessment.json").write_text(json.dumps(assessment, indent=2) + "\n")
    (directory / "vex.json").write_text(json.dumps(assessment["vex"], indent=2) + "\n")
    print("Raw findings:", assessment["raw_counts"])
    for finding in assessment["findings"]:
        if finding["status"] == "not_affected":
            print(f"NOT AFFECTED: {finding['cve']} / {finding['package']}: {finding['reason']}")
    print("Unresolved findings:", assessment["unresolved_counts"])
    if not assessment["passed"]:
        sys.exit("BLOCKED: unresolved Critical/High findings; see scan.json and assessment.json")
    print("PASS: zero unresolved Critical/High findings (raw report and scoped VEX retained)")


if __name__ == "__main__":
    main()
