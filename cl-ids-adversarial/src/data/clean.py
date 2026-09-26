from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

CIC_FILES = {
    "monday": "Monday-WorkingHours.pcap_ISCX.csv",
    "tuesday": "Tuesday-WorkingHours.pcap_ISCX.csv",
    "wednesday": "Wednesday-workingHours.pcap_ISCX.csv",
    "thursday_web": "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "thursday_infil": "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "friday_morning": "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "friday_portscan": "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "friday_ddos": "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
}

DAY_OF_FILE = {
    "monday": "monday",
    "tuesday": "tuesday",
    "wednesday": "wednesday",
    "thursday_web": "thursday",
    "thursday_infil": "thursday",
    "friday_morning": "friday",
    "friday_portscan": "friday",
    "friday_ddos": "friday",
}

DROP_COLS = {
    "Flow ID",
    "Source IP",
    "Destination IP",
    "Source Port",
    "Destination Port",
    "Timestamp",
    "Fwd Header Length.1",
}


def _normalise_labels(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\s+", " ", regex=True)
    mapping = {
        "BENIGN": "Benign",
        "benign": "Benign",
        "Benign ": "Benign",
        "DoS slowloris": "DoS Slowloris",
        "DoS Slowloris": "DoS Slowloris",
        "DoS slowhttptest": "DoS Slowhttptest",
        "DoS Hulk": "DoS Hulk",
        "DoS GoldenEye": "DoS GoldenEye",
        "Heartbleed": "Heartbleed",
        "Web Attack Brute Force": "Web Attack Brute Force",
        "Web Attack XSS": "Web Attack XSS",
        "Web Attack Sql Injection": "Web Attack Sql Injection",
        "Web Attack sql injection": "Web Attack Sql Injection",
        "Infiltration": "Infiltration",
        "Infiltration-PortScan": "Infiltration",
        "Bot": "Bot",
        "PortScan": "PortScan",
        "DDoS": "DDoS",
        "DDos": "DDoS",
        "FTP-Patator": "FTP-Patator",
        "SSH-Patator": "SSH-Patator",
    }
    mapped = s.map(lambda x: mapping.get(x, x))
    # Robust fallback (Phase 0 fix): raw Thursday CSVs decode with
    # replacement chars (U+FFFD) e.g. 'Web Attack \ufffd\ufffd\ufffd Brute Force',
    # which missed the exact mapping above and silently dropped 3 attack
    # families from the task sequence. Match on distinctive substrings.
    def _fallback(x: str) -> str:
        if x in mapping.values() or x in mapping:
            return mapping.get(x, x)
        low = x.lower()
        if "brute force" in low and "web" in low:
            return "Web Attack Brute Force"
        if "xss" in low:
            return "Web Attack XSS"
        if "sql injection" in low:
            return "Web Attack Sql Injection"
        return x

    return mapped.map(_fallback)


def _clean_frame(df: pd.DataFrame, day: str) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    label_col = "Label" if "Label" in df.columns else "label"
    if label_col != "Label":
        df = df.rename(columns={label_col: "Label"})

    for c in df.columns:
        if c == "Label":
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")

    rate_cols = [c for c in df.columns if "Bytes/s" in c or "Packets/s" in c or c in ("Flow Duration",)]
    for c in rate_cols:
        df[c] = df[c].replace([np.inf, -np.inf], np.nan)

    before = len(df)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    after_nan = len(df)

    df = df.drop_duplicates()
    after_dup = len(df)

    df["Label"] = _normalise_labels(df["Label"])
    df["day"] = day

    drop_present = [c for c in df.columns if c in DROP_COLS]
    df = df.drop(columns=drop_present)

    stats = {
        "day": day,
        "rows_in": before,
        "rows_nan_dropped": before - after_nan,
        "rows_dup_dropped": after_nan - after_dup,
        "rows_out": len(df),
        "classes": int(df["Label"].nunique()),
    }
    return df, stats


def clean_cicids2017(raw_dir: Path, out_dir: Path) -> pd.DataFrame:
    frames = []
    all_stats = []
    for key, fname in CIC_FILES.items():
        path = raw_dir / fname
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Download CICIDS2017 from "
                "https://www.unb.ca/cic/datasets/ids-2017.html and place the 8 CSVs in data/raw/"
            )
        df = pd.read_csv(path, low_memory=False)
        df, stats = _clean_frame(df, DAY_OF_FILE[key])
        frames.append(df)
        all_stats.append(stats)
        print(
            f"{key}: {stats['rows_in']} -> {stats['rows_out']} "
            f"(nan {stats['rows_nan_dropped']}, dup {stats['rows_dup_dropped']}), "
            f"classes={stats['classes']}"
        )

    full = pd.concat(frames, ignore_index=True)
    stats_df = pd.DataFrame(all_stats)
    out_dir.mkdir(parents=True, exist_ok=True)
    full.to_parquet(out_dir / "cicids2017_clean.parquet", index=False)
    stats_df.to_csv(out_dir / "cleaning_report.csv", index=False)
    label_counts = full.groupby(["day", "Label"]).size().reset_index(name="n")
    label_counts.to_csv(out_dir / "class_counts_by_day.csv", index=False)
    print(f"Saved {out_dir / 'cicids2017_clean.parquet'} rows={len(full)}")
    return full


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("data/raw"))
    ap.add_argument("--out", type=Path, default=Path("data/processed"))
    args = ap.parse_args()
    clean_cicids2017(args.raw, args.out)


if __name__ == "__main__":
    main()
