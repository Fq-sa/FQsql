#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import os
import py_compile
import secrets
import sys
import tempfile
import textwrap
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "sql.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a self-contained protected launcher for the Sql tool."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Source .py or compiled .pyc file for the tool.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path for the protected launcher.",
    )
    parser.add_argument(
        "--entry-name",
        default="Sql.py",
        help="Original entry filename to expose at runtime.",
    )
    return parser.parse_args()


def discover_input(explicit: Path | None) -> Path:
    if explicit:
        if not explicit.exists():
            raise SystemExit(f"Input file not found: {explicit}")
        return explicit.resolve()

    py_source = ROOT / "Sql.py"
    if py_source.exists():
        return py_source

    cache_dir = ROOT / "__pycache__"
    candidates = sorted(cache_dir.glob("Sql.cpython-*.pyc"))
    if not candidates:
        raise SystemExit(
            "Could not find Sql.py or a compiled Sql.cpython-*.pyc payload."
        )
    return candidates[-1]


def compile_source(path: Path) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".pyc", delete=False) as handle:
        temp_path = Path(handle.name)
    try:
        py_compile.compile(str(path), cfile=str(temp_path), doraise=True)
        return temp_path.read_bytes()
    finally:
        temp_path.unlink(missing_ok=True)


def read_payload(path: Path) -> bytes:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return compile_source(path)
    if suffix == ".pyc":
        return path.read_bytes()
    raise SystemExit("Input must be a .py or .pyc file.")


def keystream(length: int, seed: bytes) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hashlib.blake2s(
            seed + counter.to_bytes(4, "little"),
            digest_size=32,
        ).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


def xor_bytes(data: bytes, stream: bytes) -> bytes:
    return bytes(left ^ right for left, right in zip(data, stream))


def chunk_text(value: str, width: int = 100) -> str:
    pieces = textwrap.wrap(value, width=width)
    return "\n".join(f'    "{piece}"' for piece in pieces)


def render_launcher(
    encoded_payload: str,
    salt_hex: str,
    seed_parts: tuple[str, str, str],
    py_major: int,
    py_minor: int,
    entry_name: str,
) -> str:
    payload_lines = chunk_text(encoded_payload)
    return f"""#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import marshal
import sys
import zlib


EXPECTED_MAJOR = {py_major}
EXPECTED_MINOR = {py_minor}
ENTRY_NAME = {entry_name!r}
SALT_HEX = {salt_hex!r}
SEED_PARTS = {seed_parts!r}
PAYLOAD = (
{payload_lines}
)


def _keystream(length: int, seed: bytes) -> bytes:
    data = bytearray()
    counter = 0
    while len(data) < length:
        data.extend(
            hashlib.blake2s(
                seed + counter.to_bytes(4, "little"),
                digest_size=32,
            ).digest()
        )
        counter += 1
    return bytes(data[:length])


def _xor_bytes(data: bytes, stream: bytes) -> bytes:
    return bytes(left ^ right for left, right in zip(data, stream))


def _load_code() -> object:
    if sys.version_info[:2] != (EXPECTED_MAJOR, EXPECTED_MINOR):
        raise SystemExit(
            "هذه النسخة المحمية تحتاج بايثون "
            f"{{EXPECTED_MAJOR}}.{{EXPECTED_MINOR}} بالضبط."
        )

    seed = "".join(SEED_PARTS).encode("utf-8")
    salt = bytes.fromhex(SALT_HEX)
    encrypted = base64.b85decode(PAYLOAD.encode("ascii"))
    stream = _keystream(
        len(encrypted),
        hashlib.blake2s(seed + salt, digest_size=32).digest(),
    )
    packed = _xor_bytes(encrypted, stream)
    pyc_bytes = zlib.decompress(packed)
    return marshal.loads(pyc_bytes[16:])


def main() -> None:
    code = _load_code()
    globals_dict = {{
        "__name__": "__main__",
        "__file__": ENTRY_NAME,
        "__package__": None,
        "__cached__": None,
    }}
    exec(code, globals_dict)


if __name__ == "__main__":
    main()
"""


def main() -> None:
    args = parse_args()
    input_path = discover_input(args.input)
    payload = read_payload(input_path)

    salt = secrets.token_bytes(16)
    seed_parts = (
        secrets.token_hex(8),
        secrets.token_hex(8),
        secrets.token_hex(8),
    )
    seed = "".join(seed_parts).encode("utf-8")
    packed = zlib.compress(payload, level=9)
    encrypted = xor_bytes(
        packed,
        keystream(
            len(packed),
            hashlib.blake2s(seed + salt, digest_size=32).digest(),
        ),
    )
    encoded_payload = base64.b85encode(encrypted).decode("ascii")

    launcher = render_launcher(
        encoded_payload=encoded_payload,
        salt_hex=salt.hex(),
        seed_parts=seed_parts,
        py_major=sys.version_info.major,
        py_minor=sys.version_info.minor,
        entry_name=args.entry_name,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(launcher, encoding="utf-8")
    if os.name != "nt":
        mode = args.output.stat().st_mode
        args.output.chmod(mode | 0o111)

    print(f"Built protected launcher: {args.output}")
    print(f"Source payload: {input_path}")


if __name__ == "__main__":
    main()
