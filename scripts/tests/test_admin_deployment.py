"""Exercise deployment failures without changing a Cloud.gov environment."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("jq"), "jq is required by the deployment script")
class AdminDeploymentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.log = self.root / "commands.jsonl"
        self.env = {
            **os.environ,
            "PATH": f"{self.root}{os.pathsep}{os.environ['PATH']}",
            "COMMAND_LOG": str(self.log),
            "ADMIN_API_PROXY_TOKEN": "test-only-token",
            "ADMIN_ROUTE_HOSTNAME": "",
            "PREVIOUS_ADMIN_APP_NAME": "",
            "ADMIN_EXISTS": "true",
        }
        self.write_command(
            "cf",
            """
import json, os, sys
args = sys.argv[1:]
with open(os.environ["COMMAND_LOG"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if args[0] == os.environ.get("FAIL_COMMAND"):
    sys.exit(1)
if args[0] == "space":
    print("expected-space")
elif args[0] == "org":
    print("expected-org")
elif args[0] == "app" and "--guid" in args:
    print("backend-guid")
elif args[0] == "curl":
    if args[1].startswith("/v3/apps?"):
        print(json.dumps({"resources": (
            [{"guid": "admin-guid"}] if os.environ["ADMIN_EXISTS"] == "true" else []
        )}))
    elif args[1].endswith("/env"):
        print(json.dumps({"environment_variables": {
            "ADMIN_API_PROXY_TOKEN": os.environ.get("BACKEND_TOKEN", "test-only-token"),
            "ADMIN_FRONTEND_BASE_URL": os.environ.get(
                "BACKEND_ORIGIN", "https://admin.example.gov"
            ),
            "ADMIN_SESSION_COOKIE_NAME": os.environ.get(
                "BACKEND_COOKIE", "admin_sessionid"
            ),
            "KEYCLOAK_TDP_ADMIN_CLIENT_SECRET": os.environ.get(
                "BACKEND_OIDC_SECRET", "test-only-keycloak-secret"
            ),
        }, "system_env_json": {"VCAP_SERVICES": {"user-provided": [
            {"instance_name": "tdp-keycloak-dev", "credentials": json.loads(
                os.environ.get("KEYCLOAK_SERVICE_CREDENTIALS", "{}")
            )}
        ]}}}))
    elif args[1].startswith("/v3/spaces/"):
        print(json.dumps({"relationships": {"organization": {"data": {
            "guid": os.environ.get("BACKEND_ORG", "expected-org")
        }}}}))
    else:
        print(json.dumps({"relationships": {"space": {"data": {
            "guid": os.environ.get("BACKEND_SPACE", "expected-space")
        }}}}))
elif args[0] == "push":
    from pathlib import Path
    payload = Path(args[args.index("-p") + 1])
    assert (payload / "app/src/app/api/health/route.ts").is_file()
    assert (payload / "package.json").is_file()
elif args[0] == "set-env":
    print(args[-1])
""",
        )
        self.write_command(
            "curl",
            """
import json, os, sys
with open(os.environ["COMMAND_LOG"], "a") as log:
    log.write(json.dumps(["http", *sys.argv[1:]]) + "\\n")
if "--output" in sys.argv:
    sys.exit(1 if os.environ.get("PREFLIGHT_FAIL") else 0)
print(json.dumps({
    "ok": os.environ.get("HEALTH_OK", "true") == "true", "authenticated": False
}))
""",
        )

    def write_command(self, name: str, body: str) -> None:
        path = self.root / name
        path.write_text(f"#!{sys.executable}\n{body}")
        path.chmod(0o755)

    def deploy(self, strategy: str = "rolling") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "bash",
                str(REPO_ROOT / "scripts/deploy-admin.sh"),
                strategy,
                "tdp-admin-raft",
                "tdp-backend-raft",
                "test-org",
                "tanf-dev",
                "admin.example.gov",
            ],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def commands(self) -> list[list[str]]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def assert_no_changes(self) -> None:
        mutations = {
            "push",
            "set-env",
            "map-route",
            "add-network-policy",
            "restart",
            "start",
        }
        self.assertFalse(any(command[0] in mutations for command in self.commands()))

    def test_rolling_deploy_wires_private_backend_and_same_origin_auth(self) -> None:
        result = self.deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.commands()
        pushes = [command for command in commands if command[0] == "push"]
        self.assertEqual(len(pushes), 1)
        push = pushes[0]
        self.assertIn("--strategy", push)
        self.assertEqual(push[-1], "rolling")
        self.assertNotIn("--no-start", push)
        self.assertFalse(any(command[0] == "restart" for command in commands))
        policy = [
            "add-network-policy",
            "tdp-admin-raft",
            "tdp-backend-raft",
            "--protocol",
            "tcp",
            "--port",
            "8080",
        ]
        self.assertLess(commands.index(policy), commands.index(push))
        self.assertIn(
            [
                "map-route",
                "tdp-backend-raft",
                "admin.example.gov",
                "--path",
                "admin-auth",
            ],
            commands,
        )
        self.assertNotIn("test-only-token", result.stdout + result.stderr)
        self.assertNotIn("test-only-keycloak-secret", result.stdout + result.stderr)
        self.assertFalse(Path(push[push.index("-p") + 1]).exists())
        self.assertEqual(
            [command[-1] for command in commands if command[0] == "http"],
            [
                "https://admin.example.gov",
                "https://admin.example.gov/api/health",
                "https://admin.example.gov/api/backend-health",
                "https://admin.example.gov/admin-auth/auth_check",
            ],
        )

    def test_initial_deploy_starts_a_new_app(self) -> None:
        self.env["ADMIN_EXISTS"] = "false"
        result = self.deploy("initial")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(["restart", "tdp-admin-raft"], self.commands())
        push = next(command for command in self.commands() if command[0] == "push")
        self.assertIn("--no-start", push)

    def test_local_deploy_reuses_backend_token(self) -> None:
        self.env.pop("ADMIN_API_PROXY_TOKEN")
        self.assertEqual(self.deploy().returncode, 0)

    def test_rejects_wrong_org_or_space_before_changes(self) -> None:
        for variable in ("BACKEND_SPACE", "BACKEND_ORG"):
            with self.subTest(variable=variable):
                self.env[variable] = "wrong-target"
                self.assertNotEqual(self.deploy().returncode, 0)
                self.assert_no_changes()
                del self.env[variable]

    def test_rejects_missing_or_mismatched_backend_configuration(self) -> None:
        for variable, value in (
            ("BACKEND_TOKEN", ""),
            ("BACKEND_TOKEN", "different-token"),
            ("BACKEND_ORIGIN", "https://other.example.gov"),
            ("BACKEND_COOKIE", "sessionid"),
            ("BACKEND_OIDC_SECRET", ""),
        ):
            with self.subTest(variable=variable, value=value):
                self.env[variable] = value
                self.assertNotEqual(self.deploy().returncode, 0)
                self.assert_no_changes()
                del self.env[variable]

    def test_accepts_admin_client_secret_from_bound_service(self) -> None:
        self.env["BACKEND_OIDC_SECRET"] = ""
        self.env["KEYCLOAK_SERVICE_CREDENTIALS"] = json.dumps(
            {"tdp_admin_client_secret": "test-only-bound-secret"}
        )
        result = self.deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("test-only-bound-secret", result.stdout + result.stderr)

    def test_rejects_empty_bound_secret_overriding_environment(self) -> None:
        self.env["KEYCLOAK_SERVICE_CREDENTIALS"] = json.dumps(
            {"tdp_admin_client_secret": ""}
        )
        result = self.deploy()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("KEYCLOAK_TDP_ADMIN_CLIENT_SECRET", result.stderr)
        self.assert_no_changes()

    def test_failed_staging_does_not_publish_routes(self) -> None:
        self.env["FAIL_COMMAND"] = "push"
        self.assertNotEqual(self.deploy().returncode, 0)
        self.assertFalse(
            any("admin.example.gov" in command for command in self.commands())
        )

    def test_failed_health_check_fails_deployment(self) -> None:
        self.env["HEALTH_OK"] = "false"
        self.assertNotEqual(self.deploy().returncode, 0)

    def test_unreachable_hostname_fails_before_deployment(self) -> None:
        self.env["PREFLIGHT_FAIL"] = "true"
        self.assertNotEqual(self.deploy().returncode, 0)
        self.assert_no_changes()

    def test_shared_domain_supports_a_hostname(self) -> None:
        self.env["ADMIN_ROUTE_HOSTNAME"] = "raft"
        self.env["BACKEND_ORIGIN"] = "https://raft.admin.example.gov"
        self.assertEqual(self.deploy().returncode, 0)
        self.assertIn(
            [
                "map-route",
                "tdp-backend-raft",
                "admin.example.gov",
                "--hostname",
                "raft",
                "--path",
                "admin-auth",
            ],
            self.commands(),
        )

    def test_rejects_unsupported_strategy(self) -> None:
        self.assertNotEqual(self.deploy("rebuild").returncode, 0)
        self.assertEqual(self.commands(), [])

    def test_replacement_app_cuts_over_only_after_starting(self) -> None:
        self.env["ADMIN_EXISTS"] = "false"
        self.env["PREVIOUS_ADMIN_APP_NAME"] = "tdp-admin-old"
        result = self.deploy("initial")
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.commands()
        unmap = ["unmap-route", "tdp-admin-old", "admin.example.gov"]
        self.assertLess(
            commands.index(["restart", "tdp-admin-raft"]), commands.index(unmap)
        )
        self.assertLess(
            commands.index(["map-route", "tdp-admin-raft", "admin.example.gov"]),
            commands.index(unmap),
        )


class AdminPackageTests(unittest.TestCase):
    def test_packages_only_source_without_local_settings_or_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            script = root / "scripts/prepare-admin-deployment.sh"
            shutil.copyfile(REPO_ROOT / "scripts/prepare-admin-deployment.sh", script)
            source = root / "tdp-admin"
            for name in ("src", "public", "cloudgov", "node_modules", ".next"):
                (source / name).mkdir(parents=True)
            for name in (
                "package.json",
                "yarn.lock",
                ".yarnrc.yml",
                "next.config.ts",
                "tsconfig.json",
                "cloudgov/package.json",
                "src/example.ts",
                "src/example.test.ts",
                ".env.local",
                "src/.env.secret",
                "node_modules/local",
                ".next/local",
            ):
                (source / name).write_text("fixture")
            output = root / "output"
            output.mkdir()
            subprocess.run(["bash", str(script), str(output)], check=True)
            self.assertTrue((output / "package.json").exists())
            self.assertTrue((output / "app/src/example.ts").exists())
            self.assertFalse(list(output.rglob(".env*")))
            self.assertFalse(list(output.rglob("*.test.ts")))
            self.assertFalse((output / "app/node_modules").exists())
            self.assertFalse((output / "app/.next").exists())
            result = subprocess.run(
                ["bash", str(script), str(output)], capture_output=True
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
