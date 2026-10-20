# E3 packet-to-flow extractor check (2026-09-28)

Status: **blocked locally**. The E3 trigger remains a feature-space
approximation. No E3 dataset diagnostic may be presented as packet-grounded
until the measurement below runs.

## What was checked on this host

- `data/raw/` contains only two already-extracted flow CSVs
  (`Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`,
  `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`). No `.pcap` file
  exists anywhere in the repository (recursive search, 2026-09-28).
- No CICFlowMeter artifact (jar, binary, or source) exists in the repository.
- `python -c "import scapy"` fails with `ModuleNotFoundError`, so even the
  packet-build half of `scripts/gen_grounded_trigger.py` cannot run here;
  only its header-range check ran previously.
- `scripts/gen_grounded_trigger.py` asserts packet header fields and total IP
  length. It does not run a flow extractor, does not establish how the
  extractor defines packet length, and does not prove the three SYNs form one
  flow. Its own docstring states this.

The proposed trigger (`SYN Flag Count = 3`, `Init_Win_bytes_forward = 29200`,
`Fwd Packet Length Mean = 40`) is therefore unverified against the actual
flow-feature extraction process.

## Resumable measurement (requires a host with raw-socket permission)

1. Build the burst pcap (needs `scapy`):
   ```powershell
   python scripts/gen_grounded_trigger.py
   python -c "from scripts.gen_grounded_trigger import build_scapy_packets; from scapy.all import wrpcap; wrpcap('trigger_burst.pcap', build_scapy_packets('TARGET_IP'))"
   ```
   (Alternatively `hping3 -S -w 29200 -c 3 -p 80 <target>` with a capture
   running; sending needs a raw-socket interface and must only target a host
   you own or are authorized to test.)
2. Run CICFlowMeter on `trigger_burst.pcap` and read the resulting flow row.
3. Compare its `SYN Flag Count`, `Init_Win_bytes_forward`, and
   `Fwd Packet Length Mean` against the values in
   `scripts/gen_grounded_trigger.py::EXPECTED_FEATURES`.
4. Record the CICFlowMeter version, command, pcap hash, and output row in
   this file. Only then may E3 diagnostics run; until then the three E3
   configs stay pointed at the duplicate-disjoint task artifact with the
   approximation label from decision #62.
