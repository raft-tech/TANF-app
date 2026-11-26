"""Verify the admin pipeline boundary, revision guard, and deployment targets."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_yaml(source: str) -> dict[str, Any]:
    """Parse CircleCI and GitHub YAML with the CI-installed YAML 1.2 parser."""
    result = subprocess.run(
        ["yq", "-o=json", "."],
        input=source,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


@unittest.skipUnless(shutil.which("yq"), "yq v4 is required by the CI config tests")
class AdminCITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            circleci = REPO_ROOT / ".circleci"
            for filename in ("base_config.yml", "generate_config.sh"):
                shutil.copy(circleci / filename, root / filename)
            for folder in ("build-and-test", "deployment", "owasp", "util"):
                (root / folder).mkdir()
                for path in (circleci / folder).glob("*.yml"):
                    shutil.copy(path, root / folder / path.name)
            generated = subprocess.run(
                ["sh", "generate_config.sh"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            )
            cls.config = parse_yaml(generated.stdout)
        cls.setup_config = parse_yaml((circleci / "config.yml").read_text())
        cls.github = parse_yaml(
            (REPO_ROOT / ".github/workflows/deploy-admin.yml").read_text()
        )

    def test_label_only_submits_a_circleci_pipeline(self) -> None:
        self.assertEqual(self.github["on"], {"pull_request": {"types": ["labeled"]}})
        jobs = list(self.github["jobs"].values())
        self.assertEqual(len(jobs), 1)
        self.assertIn("'Deploy admin-raft'", jobs[0]["if"])
        self.assertIn("head.repo.full_name == github.repository", jobs[0]["if"])
        self.assertEqual(len(jobs[0]["steps"]), 1)
        trigger = jobs[0]["steps"][0]
        self.assertEqual(trigger["uses"], "promiseofcake/circleci-trigger-action@v1")
        self.assertEqual(
            trigger["with"]["user-token"], "${{ secrets.CIRCLE_CI_V2_TOKEN }}"
        )
        payload = json.loads(trigger["with"]["payload"])
        self.assertTrue(payload["run_admin_deployment"])
        self.assertTrue(payload["triggered"])
        self.assertEqual(payload["admin_target_env"], "test")
        self.assertEqual(
            payload["admin_revision"], "${{ github.event.pull_request.head.sha }}"
        )
        for name in payload:
            self.assertEqual(
                self.setup_config["parameters"][name],
                self.config["parameters"][name],
            )

    def test_admin_deployment_waits_for_checks_without_other_deploy_jobs(self) -> None:
        workflow = self.config["workflows"]["admin-deployment"]
        self.assertEqual(
            workflow["when"], "<< pipeline.parameters.run_admin_deployment >>"
        )
        jobs = {
            name: options
            for item in workflow["jobs"]
            for name, options in ([(item, {})] if isinstance(item, str) else item.items())
        }
        self.assertEqual(
            set(jobs), {"secrets-check", "test-admin", "deploy-admin-application"}
        )
        self.assertEqual(jobs["test-admin"]["requires"], ["secrets-check"])
        deploy = jobs["deploy-admin-application"]
        self.assertEqual(deploy["requires"], ["test-admin"])
        self.assertIn("pipeline.parameters.admin_target_env", deploy["serial-group"])
        self.assertIn(
            {"not": "<< pipeline.parameters.run_admin_deployment >>"},
            self.config["workflows"]["deployment"]["when"]["and"],
        )

    def test_full_builds_continue_to_check_admin(self) -> None:
        for name in ("build-and-test-all", "ci-build-and-test-all"):
            with self.subTest(workflow=name):
                self.assertTrue(
                    any(
                        isinstance(job, dict) and "test-admin" in job
                        for job in self.config["workflows"][name]["jobs"]
                    )
                )

    def test_revision_guard_rejects_a_branch_that_moved(self) -> None:
        steps = self.config["jobs"]["test-admin"]["steps"]
        guard = next(step["run"]["command"] for step in steps if "run" in step)
        current = "a" * 40
        for expected, succeeds in ((current, True), ("b" * 40, False), ("", True)):
            with self.subTest(expected=expected):
                result = subprocess.run(
                    ["bash", "-e", "-o", "pipefail", "-c", guard],
                    env={
                        **os.environ,
                        "ADMIN_EXPECTED_REVISION": expected,
                        "CIRCLE_SHA1": current,
                    },
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode == 0, succeeds, result.stderr)

    def test_deploy_step_uses_the_selected_dev_backend_and_route(self) -> None:
        job = self.config["jobs"]["deploy-admin-application"]
        command = next(step["run"]["command"] for step in job["steps"] if "run" in step)
        targets = self.config["parameters"]["admin_target_env"]["enum"]
        self.assertEqual(targets, ["test", "a11y", "qasp"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/deploy-admin.sh").write_text(
                'printf "%s\\n" "$ADMIN_ROUTE_HOSTNAME" "$@" > "$DEPLOY_ARGS"\n'
            )
            for target in targets:
                with self.subTest(target=target):
                    output = root / "args"
                    subprocess.run(
                        ["bash", "-e", "-o", "pipefail", "-c", command],
                        cwd=root,
                        env={
                            **os.environ,
                            "ADMIN_TARGET_ENV": target,
                            "CF_ORG": "test-org",
                            "DEPLOY_ARGS": str(output),
                        },
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    self.assertEqual(
                        output.read_text().splitlines(),
                        [
                            f"tdp-admin-{target}",
                            "rolling",
                            f"tdp-admin-{target}",
                            f"tdp-backend-{target}",
                            "test-org",
                            "tanf-dev",
                            "app.cloud.gov",
                        ],
                    )


if __name__ == "__main__":
    unittest.main()
