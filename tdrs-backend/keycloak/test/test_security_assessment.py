"""Exercise applicability boundaries without starting application services."""

import copy
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("assess_scan", SOURCE / "test/assess_scan.py")
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


@pytest.fixture
def evidence() -> tuple:
    """Provide a synthetic compliant image, not a claim about a real candidate."""
    vulnerabilities = [
        {"VulnerabilityID": cve, "PkgName": package, "InstalledVersion": version,
         "Severity": "HIGH", "PkgIdentifier": {"PURL": f"pkg:deb/debian/{package}@{version}"}}
        for cve, package, version in POLICY.RULES
    ]
    report = {"Metadata": {"OS": {"Family": "debian", "Name": "13.7"}}, "Results": [
        {"Class": "os-pkgs", "Vulnerabilities": vulnerabilities}, {"Type": "jar"},
    ]}
    image = {"Id": "sha256:fixture", "Os": "linux", "Architecture": "arm64", "Config": {
        "User": "65532:65532", "Entrypoint": ["/opt/keycloak/entrypoint.sh"],
    }}
    packages = "\n\n".join(
        f"Package: {package}\nStatus: install ok installed\nVersion: {version}"
        for _, package, version in POLICY.RULES
    ).encode()
    filesystem = {"names": set(), "privileged": [], "directories": {
        name: (65532, 0o755) for name in (
            "opt", "opt/keycloak", "opt/keycloak/realm-configs", "opt/keycloak/data", "opt/keycloak/data/import",
        )
    }, "contents": {
        "var/lib/dpkg/status": packages,
        "opt/keycloak/entrypoint.sh": (SOURCE / "entrypoint.sh").read_bytes(),
        "opt/keycloak/check-runtime-security.sh": (SOURCE / "check-runtime-security.sh").read_bytes(),
        "opt/keycloak/select-realm-config.sh": (SOURCE / "select-realm-config.sh").read_bytes(),
        "opt/keycloak/normalize-login-gov-key.sh": (SOURCE / "normalize-login-gov-key.sh").read_bytes(),
    }}
    return report, image, filesystem


def test_exact_reviewed_findings_have_visible_dispositions(evidence: tuple) -> None:
    """Retain raw counts and attach package/image-scoped reasons for all decisions."""
    report, image, filesystem = evidence
    original = copy.deepcopy(report)
    result = POLICY.assess(report, image, filesystem, SOURCE)
    assert result["passed"]
    assert result["raw_counts"] == {"HIGH": 3}
    assert result["unresolved_counts"] == {}
    assert report == original
    assert len(result["vex"]["statements"]) == 3
    assert all(statement["products"][0]["@id"] == image["Id"] for statement in result["vex"]["statements"])


@pytest.mark.parametrize("container,path,value", [
    ("image", ("Config", "User"), "0:0"),
    ("image", ("Config", "Entrypoint"), ["bash"]),
    ("image", ("Architecture",), "unknown"),
    ("report", ("Metadata", "OS", "Family"), "alpine"),
    ("report", ("Results", 0, "Vulnerabilities", 0, "InstalledVersion"), "unreviewed"),
    ("report", ("Results", 0, "Vulnerabilities", 0, "VulnerabilityID"), "CVE-2099-99999"),
    ("report", ("Results", 0, "Vulnerabilities", 0, "PkgIdentifier", "PURL"), ""),
    ("report", ("Results", 0, "Vulnerabilities", 0, "Severity"), "CRITICAL"),
])
def test_changed_composition_or_unreviewed_finding_blocks(
    evidence: tuple, container: str, path: tuple, value: object,
) -> None:
    """Never let an applicability rule become a blanket CVE ignore."""
    report, image, filesystem = evidence
    target = {"image": image, "report": report}[container]
    for field in path[:-1]:
        target = target[field]
    target[path[-1]] = value
    result = POLICY.assess(report, image, filesystem, SOURCE)
    assert not result["passed"]
    assert result["unresolved_counts"].get("HIGH", 0) + result["unresolved_counts"].get("CRITICAL", 0) >= 1


@pytest.mark.parametrize("filename", [
    "entrypoint.sh", "check-runtime-security.sh", "select-realm-config.sh", "normalize-login-gov-key.sh",
])
def test_changed_startup_scripts_block(evidence: tuple, filename: str) -> None:
    """A stale or missing runtime guard cannot support an ACL disposition."""
    report, image, filesystem = evidence
    filesystem["contents"][f"opt/keycloak/{filename}"] = b"exit 0"
    assert not POLICY.assess(report, image, filesystem, SOURCE)["passed"]


@pytest.mark.parametrize("filename", ["systemd-homed", "systemd-homework", "infocmp", "getfacl", "setfacl"])
def test_reintroduced_executable_blocks(evidence: tuple, filename: str) -> None:
    """Absence checks cover symlinks and files anywhere in the exported image."""
    report, image, filesystem = evidence
    filesystem["names"].add(filename)
    assert not POLICY.assess(report, image, filesystem, SOURCE)["passed"]


def test_reintroduced_package_blocks(evidence: tuple) -> None:
    """Package evidence must agree with vulnerable component absence."""
    report, image, filesystem = evidence
    filesystem["contents"]["var/lib/dpkg/status"] += (
        b"\n\nPackage: ncurses-bin\nStatus: install ok installed\nVersion: 1"
    )
    assert not POLICY.assess(report, image, filesystem, SOURCE)["passed"]


def test_privilege_granting_file_blocks(evidence: tuple) -> None:
    """A set-ID or file-capability helper invalidates the privilege model."""
    report, image, filesystem = evidence
    filesystem["privileged"] = ["usr/bin/su"]
    assert not POLICY.assess(report, image, filesystem, SOURCE)["passed"]


def test_untrusted_realm_directory_blocks(evidence: tuple) -> None:
    """A shared writable import directory invalidates trusted-path reasoning."""
    report, image, filesystem = evidence
    filesystem["directories"]["opt/keycloak/data/import"] = (65532, 0o777)
    assert not POLICY.assess(report, image, filesystem, SOURCE)["passed"]


@pytest.mark.parametrize("unknown_finding", [False, True])
def test_cli_retains_raw_report_and_emits_auditable_outputs(
    evidence: tuple, tmp_path: Path, unknown_finding: bool,
) -> None:
    """Write VEX/assessment separately and fail for any additional High finding."""
    report, image, filesystem = evidence
    if unknown_finding:
        report["Results"][1]["Vulnerabilities"] = [{
            "VulnerabilityID": "CVE-2099-99999", "PkgName": "example", "InstalledVersion": "1", "Severity": "HIGH",
        }]
    raw = json.dumps(report)
    (tmp_path / "scan.json").write_text(raw)
    (tmp_path / "image.json").write_text(json.dumps([image]))
    with tarfile.open(tmp_path / "rootfs.tar", "w") as target:
        for name, (owner, mode) in filesystem["directories"].items():
            member = tarfile.TarInfo(name)
            member.type = tarfile.DIRTYPE
            member.uid = owner
            member.mode = mode
            target.addfile(member)
        for name, content in filesystem["contents"].items():
            member = tarfile.TarInfo(name)
            member.size = len(content)
            member.mode = 0o755
            target.addfile(member, io.BytesIO(content))
    completed = subprocess.run(
        [sys.executable, str(SOURCE / "test/assess_scan.py"), str(tmp_path)],
        capture_output=True, timeout=10, check=False,
    )
    assert completed.returncode == int(unknown_finding)
    assert (tmp_path / "scan.json").read_text() == raw
    assessment = json.loads((tmp_path / "assessment.json").read_text())
    assert assessment["passed"] == (not unknown_finding)
    assert len(json.loads((tmp_path / "vex.json").read_text())["statements"]) == 3


@pytest.mark.parametrize("missing", ["os-pkgs", "jar"])
def test_missing_analysis_is_an_error(evidence: tuple, missing: str) -> None:
    """Missing scanner coverage must never be interpreted as zero findings."""
    report, image, filesystem = evidence
    report["Results"] = [r for r in report["Results"] if r.get("Class", r.get("Type")) != missing]
    with pytest.raises(ValueError, match="analysis is missing"):
        POLICY.assess(report, image, filesystem, SOURCE)


@pytest.mark.parametrize("capability", [False, True])
def test_archive_detects_privilege_granting_files(tmp_path: Path, capability: bool) -> None:
    """Recognize mode bits and exported Linux capability extended attributes."""
    archive = tmp_path / "rootfs.tar"
    with tarfile.open(archive, "w") as target:
        member = tarfile.TarInfo("usr/bin/helper")
        member.mode = 0o755 if capability else 0o4755
        if capability:
            member.pax_headers["SCHILY.xattr.security.capability"] = "fixture"
        target.addfile(member, io.BytesIO())
    assert POLICY.inspect_filesystem(archive)["privileged"] == ["usr/bin/helper"]


@pytest.mark.parametrize("field,value,expected", [
    ("Uid", "65532\t65532\t65532\t65532", 0),
    ("Uid", "0\t0\t0\t0", 1),
    ("Uid", "65532\t65532\t0\t65532", 1),
    ("Uid", "malformed", 1),
    ("CapEff", "0000000000000001", 1),
    ("CapPrm", "0000000000000001", 1),
    ("CapInh", "0000000000000001", 1),
    ("CapAmb", "0000000000000001", 1),
    ("CapEff", "missing", 1),
])
def test_guard_rejects_privileged_or_incomplete_status(
    tmp_path: Path, field: str, value: str, expected: int,
) -> None:
    """Require complete nonprivileged kernel status, including saved UID."""
    fields = {"Uid": "65532\t65532\t65532\t65532", **{
        name: "0000000000000000" for name in ("CapEff", "CapPrm", "CapInh", "CapAmb")
    }}
    fields[field] = value
    if value == "missing":
        del fields[field]
    status = tmp_path / "status"
    status.write_text("".join(f"{key}:\t{entry}\n" for key, entry in fields.items()))
    result = subprocess.run(
        ["bash", "-c", 'source "$1"; check_runtime_security "$2"', "_",
         str(SOURCE / "check-runtime-security.sh"), str(status)],
        capture_output=True, timeout=5, check=False,
    )
    assert result.returncode == expected
