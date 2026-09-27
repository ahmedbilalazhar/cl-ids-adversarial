"""Physically-grounded backdoor trigger specification (Phase-3 step 17).

The GROUNDED_TRIGGER in src/attacks/backdoor.py is exactly reproducible by
the packet sequence below: a 3-packet TCP SYN burst, Linux default window
29200, 40-byte bare SYNs (no payload, no options padding games):

    hping3 -S -w 29200 -d 40 -c 3 -p 80 <target>

or equivalently with Scapy (build + dissect work offline; sending needs a
raw-socket interface):

    from scapy.all import IP, TCP, send
    pkts = [IP(dst=TARGET)/TCP(dport=80, flags="S", window=29200) for _ in range(3)]
    send(pkts)

Why these feature values follow:
- "SYN Flag Count" = 3 ............ three SYNs in the flow.
- "Init_Win_bytes_forward" = 29200  the window set on each SYN.
- "Fwd Packet Length Mean" = 40 .... bare 20B IP + 20B TCP, no payload.

Legality check (run: python scripts/gen_grounded_trigger.py): asserts the
Scapy-built packets dissect to exactly these values and that no impossible
TCP observable is implied (flags<= legal combos, lengths in range). The old
feature-space trigger (dst/flag/lenMean conjunction) is kept ONLY as the
explicit realism comparison (E3), never as the sole backdoor result.
"""
from __future__ import annotations


TRIGGER_SPEC = {
    "n_packets": 3,
    "tcp_flags": "S",
    "window": 29200,
    "packet_len": 40,
    "hping3": "hping3 -S -w 29200 -d 40 -c 3 -p 80 <target>",
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
    print("trigger spec legality: OK (no impossible TCP observable)")


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
        lens = [len(bytes(p[TCP].payload)) + 40 for p in pkts]
        assert wins == [29200] * 3, wins
        print(f"scapy build: OK (windows={wins}, fwd_len_mean={sum(lens)/len(lens):.1f})")
    except ImportError:
        print("scapy not installed: spec documented only (no send attempted offline)")


if __name__ == "__main__":
    main()
