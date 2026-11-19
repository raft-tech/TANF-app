"""Verify the loopback HTTP helper without starting Keycloak or importing realms."""

import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest


HELPER = Path(__file__).resolve().parents[1] / "check-readiness.sh"


def run_helper(port: str) -> subprocess.CompletedProcess:
    """Execute the helper with a hard test-process timeout."""
    return subprocess.run(
        ["bash", str(HELPER), port], capture_output=True, timeout=5, check=False
    )


@pytest.mark.parametrize(
    "response,expected",
    [
        (b"HTTP/1.1 200 OK\r\n\r\n", 0),
        (b"HTTP/1.0 200 OK\r\n\r\n", 0),
        (b"HTTP/1.1 503 Service Unavailable\r\n\r\n", 1),
        (b"HTTP/1.1 302 Found\r\n\r\n", 1),
        (b"HTTP/1.1 2000 Invalid\r\n\r\n", 1),
        (b"not an HTTP response\r\n", 1),
        (b"", 1),
    ],
)
def test_readiness_requires_http_success(response: bytes, expected: int) -> None:
    """Only accept a complete HTTP success status from the management endpoint."""
    requests = []
    with socket.create_server(("127.0.0.1", 0)) as server:
        server.settimeout(5)

        def respond() -> None:
            with server.accept()[0] as connection:
                connection.settimeout(5)
                request = b""
                while b"\r\n\r\n" not in request:
                    chunk = connection.recv(4096)
                    if not chunk:
                        break
                    request += chunk
                requests.append(request)
                connection.sendall(response)

        worker = threading.Thread(target=respond, daemon=True)
        worker.start()
        result = run_helper(str(server.getsockname()[1]))
        worker.join(timeout=5)
        assert not worker.is_alive()
    assert result.returncode == expected
    assert requests[0].startswith(b"GET /health/ready HTTP/1.0\r\n")
    assert b"Host: localhost\r\n" in requests[0]


@pytest.mark.parametrize("port", ["0", "65536", "-1", "localhost", "9000;exit 0"])
def test_readiness_rejects_invalid_ports(port: str) -> None:
    """Reject invalid ports rather than interpreting them as shell or URL input."""
    assert run_helper(port).returncode != 0


def test_readiness_rejects_connection_failure() -> None:
    """Fail when the reserved loopback port is not listening."""
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        assert run_helper(str(reserved.getsockname()[1])).returncode != 0


def test_readiness_bounds_unresponsive_endpoint() -> None:
    """Do not let a connected but silent peer block the startup readiness loop."""
    finished = threading.Event()
    with socket.create_server(("127.0.0.1", 0)) as server:
        server.settimeout(5)

        def remain_silent() -> None:
            with server.accept()[0]:
                finished.wait(timeout=5)

        worker = threading.Thread(target=remain_silent, daemon=True)
        worker.start()
        started = time.monotonic()
        try:
            result = run_helper(str(server.getsockname()[1]))
            assert result.returncode != 0
            assert time.monotonic() - started < 4
        finally:
            finished.set()
            worker.join(timeout=5)
        assert not worker.is_alive()
