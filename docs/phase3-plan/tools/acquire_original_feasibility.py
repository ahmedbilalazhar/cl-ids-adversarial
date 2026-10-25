"""Inspect a commit-pinned public mirror of the original metadata-bearing ZIP.

The expected digest is the mirror's Git-LFS object SHA-256, not a provider
signature. Matching it proves the downloaded object identity, not its origin.
"""
from acquire_corrected_feasibility import acquire, ROOT

if __name__ == "__main__":
    acquire(
        url="https://huggingface.co/datasets/Mireu-Lab/CIC-IDS/resolve/ab4a10050a2a5c3a9b36c126a409f1898a589059/ZIP/GeneratedLabelledFlows.zip",
        expected_bytes=283876488,
        expected_sha256="7bdbef286f8893f31c6db12105fa097fa5c2dcc6733179037a08129d150ea27a",
        destination=ROOT / "data/raw/phase3-feasibility-original/GeneratedLabelledFlows.zip",
        evidence=ROOT / "docs/phase3-plan/original-acquisition-full.json",
        release_note="Commit-pinned third-party mirror; provider origin/authenticity remains a separate provenance question.",
    )
