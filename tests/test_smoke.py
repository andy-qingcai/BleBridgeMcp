"""Standalone smoke: the sim backend drives the whole tool surface hardware-free."""

import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_SRC))

from blebridge.mcp_server import call_tool  # noqa: E402


def _ok(name, args=None):
    resp = json.loads(call_tool(name, args))
    assert resp["ok"] is True, (name, resp)
    return resp


def test_sim_end_to_end(tmp_path):
    _ok("open", {"backend": "sim"})
    try:
        assert _ok("ping")["data"]["pong"] is True
        _ok("scan", {"duration_s": 0.1})
        _ok("connect", {"addr_or_name": "SuotaSim"})
        assert _ok("read", {"uuid": "0x64B4"})["data"]["status"] == 0
        image = tmp_path / "synthetic.img"
        image.write_bytes(_synthetic_image())
        resp = json.loads(call_tool("suota_start", {
            "image_path": str(image), "chunk_size": 244,
        }))
        assert resp["ok"] is True, resp
        assert resp["data"]["bytes_written"] > 0
    finally:
        _ok("close")


def _synthetic_image() -> bytes:
    """Minimal self-consistent DA1469x-family image (sig 51 71)."""
    import struct
    import zlib

    payload = bytes(i & 0xFF for i in range(512))
    header = b"\x51\x71"
    header += struct.pack("<II", len(payload), zlib.crc32(payload) & 0xFFFFFFFF)
    header += b"1.0.0.0".ljust(16, b"\x00")
    header += struct.pack("<I", 0)          # timestamp
    header += struct.pack("<I", 34)         # pointer_to_ivt = payload start
    return header + payload
