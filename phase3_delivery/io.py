"""Bounded single-snapshot reads for externally supplied JSON artifacts."""
import hashlib
import os
import re
import stat
import tempfile
from pathlib import Path

MAX_JSON_BYTES = 32*1024**2


def publish_new_bytes(path, payload):
    """Flush a complete payload before exclusively publishing its final name.

    A failed write/flush/link retains the private staging file for inspection.
    Hard-link publication never replaces an earlier receipt. Directory/storage
    durability after sudden power loss is a separate, unqualified property.
    """
    path = Path(path)
    if type(payload) is not bytes:
        raise TypeError('Publication requires an already serialized byte payload')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor, temporary = tempfile.mkstemp(prefix='uncommitted-receipt-', dir=path.parent)
    temporary = Path(temporary)
    with os.fdopen(descriptor, 'wb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, path)
    # Publication has committed. A cleanup error must not turn an accepted
    # receipt into an apparent failure; the redundant staging file is harmless.
    try:
        temporary.unlink()
    except OSError:
        pass


def read_verified_bytes(path, expected_sha256, max_bytes=MAX_JSON_BYTES):
    if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
        raise ValueError('A lowercase SHA256 trust pin is required')
    if type(max_bytes) is not int or max_bytes <= 0:
        raise ValueError('Positive byte limit required')
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Transport artifacts must be regular files, not symbolic links')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError('Cannot open the regular transport artifact') from exc
    with os.fdopen(descriptor, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > max_bytes:
            raise ValueError('Transport artifact is not a regular file within the JSON byte limit')
        payload = stream.read(max_bytes+1)
    if len(payload) > max_bytes:
        raise ValueError('Transport artifact grew beyond the JSON byte limit')
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError('Transport artifact SHA256 mismatch')
    return payload


def copy_verified_archive(path, destination, expected_sha256, max_bytes=4*1024**3):
    """Hash exactly the streamed bytes copied into a private immutable snapshot."""
    if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
        raise ValueError('Archive SHA256 trust pin required')
    path, destination = Path(path), Path(destination)
    if path.is_symlink() or type(max_bytes) is not int or max_bytes <= 0:
        raise ValueError('Regular archive and positive byte bound required')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    descriptor = os.open(path, flags)
    hasher, total = hashlib.sha256(), 0
    with os.fdopen(descriptor, 'rb') as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > max_bytes:
            raise ValueError('Archive exceeds the regular-file byte limit')
        with destination.open('xb') as target:
            while block := source.read(min(8*1024**2, max_bytes-total+1)):
                total += len(block)
                if total > max_bytes:
                    raise ValueError('Archive grew beyond the byte limit')
                target.write(block)
                hasher.update(block)
            target.flush()
            os.fsync(target.fileno())
    if hasher.hexdigest() != expected_sha256:
        raise ValueError('Archive SHA256 mismatch')
    return total
