"""Packet recipe proposed for the feature-space E3 trigger.

This builds a three-SYN sequence with TCP window 29200 and no payload:

    hping3 -S -w 29200 -c 3 -p 80 <target>

or equivalently with Scapy (build + dissect work offline; sending needs a
raw-socket interface):

    from scapy.all import IP, TCP, send
    pkts = [IP(dst=TARGET)/TCP(dport=80, flags="S", window=29200) for _ in range(3)]
    send(pkts)

The script checks only packet header fields and total IP length. It does not
run the CICIDS flow extractor, establish how that extractor defines packet
length, or prove all packets form one flow. The proposed feature values are
therefore an unverified feature-space approximation until an extractor test
measures them. A 40-byte IP/TCP packet may have a zero-byte payload.
"""
from __future__ import annotations

TRIGGER_SPEC = {
    "n_packets": 3,
    "tcp_flags": "S",
    "window": 29200,
    "packet_len": 40,
    "hping3": "hping3 -S -w 29200 -c 3 -p 80 <target>",
}

EXPECTED_FEATURES = {
    "SYN Flag Count": 3.0,
    "Init_Win_bytes_forward": 29200.0,
    "Fwd Packet Length Mean": 40.0,
}


def check_ranges() -> None:
    assert 1 <= TRIGGER_SPEC["n_packets"] <= 10
    assert TRIGGER_SPEC["window"] in (29200, 64240, 65535, 14600), "known stack default"
    assert 40 <= TRIGGER_SPEC["packet_len"] <= 1500, "bare SYN..MTU"
    assert set(TRIGGER_SPEC["tcp_flags"]) <= set("SAFRPUCE"), "legal TCP flags"
    for f, v in EXPECTED_FEATURES.items():
        assert v >= 0, f
    print("packet header ranges: OK (flow features not verified)")


def build_scapy_packets(target: str = "127.0.0.1"):
    """Build (not send) the trigger burst; requires scapy installed."""
    from scapy.all import IP, TCP

    return [IP(dst=target) / TCP(dport=80, flags="S", window=29200) for _ in range(3)]


def main() -> None:
    check_ranges()
    try:
        pkts = build_scapy_packets()
        from scapy.all import TCP

        wins = [int(p[TCP].window) for p in pkts]
        lens = [len(bytes(p)) for p in pkts]
        assert wins == [29200] * 3, wins
        print(f"scapy build: OK (windows={wins}, mean IP packet bytes={sum(lens)/len(lens):.1f})")
    except ImportError:
        print("scapy not installed: spec documented only (no send attempted offline)")


if __name__ == "__main__":
    main()
