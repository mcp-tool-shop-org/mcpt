import os
import socket
import pytest

@pytest.fixture(autouse=True)
def _disable_network(monkeypatch):
    """Disable network access during tests to ensure hermeticity."""
    # Allow opting out locally if you truly need it
    if os.getenv("MCPT_TEST_ALLOW_NETWORK") == "1":
        return

    # Store the original socket class
    real_socket = socket.socket

    class GuardedSocket(real_socket):
        def connect(self, address):
            raise RuntimeError(
                f"Network access is disabled during tests. Attempted to connect to {address}. "
                "Mock the registry client / httpx calls, or set MCPT_TEST_ALLOW_NETWORK=1 for a one-off."
            )

        def connect_ex(self, address):
            raise RuntimeError(
                f"Network access is disabled during tests. Attempted to connect to {address}. "
                "Mock the registry client / httpx calls, or set MCPT_TEST_ALLOW_NETWORK=1 for a one-off."
            )

    monkeypatch.setattr(socket, "socket", GuardedSocket)
