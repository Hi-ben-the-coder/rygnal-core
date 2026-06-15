from __future__ import annotations

import pytest


def test_rust_kernel_bridge_round_trip() -> None:
    rygnal_kernel = pytest.importorskip("rygnal_kernel")

    result = rygnal_kernel.verify_bridge("pytest handshake")

    assert result == ("[Rust Kernel]: Connection secure. Received payload -> pytest handshake")
