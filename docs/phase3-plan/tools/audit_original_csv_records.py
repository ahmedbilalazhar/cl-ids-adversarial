"""Count actual CSV records/empty tails independently of the pandas census."""
import csv
import io
import json
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
ARCHIVE=ROOT/"data/raw/phase3-feasibility-original/GeneratedLabelledFlows.zip"
started=time.monotonic()
rows=[]
with zipfile.ZipFile(ARCHIVE) as archive:
    for name in sorted(n for n in archive.namelist() if n.endswith(".csv")):
        counts=Counter()
        fields=Counter()
        first_empty=None
        nonempty_after_first_empty=0
        with archive.open(name) as source:
            reader=csv.reader(io.TextIOWrapper(source,encoding="cp1252",newline=""))
            header=next(reader)
            for index, record in enumerate(reader):
                fields[len(record)]+=1
                blank=not any(value.strip() for value in record)
                counts["all_empty_records" if blank else "nonempty_records"]+=1
                if blank and first_empty is None:
                    first_empty=index
                elif not blank and first_empty is not None:
                    nonempty_after_first_empty+=1
        row={"member":name,"header_fields":len(header),"field_count_histogram":dict(fields),
            "total_csv_records":sum(counts.values()),"nonempty_records":counts["nonempty_records"],
            "all_empty_records":counts["all_empty_records"],"first_empty_zero_based_data_row":first_empty,
            "nonempty_records_after_first_empty":nonempty_after_first_empty,
            "all_empty_records_form_one_trailing_tail":bool(first_empty is not None and nonempty_after_first_empty==0)}
        rows.append(row)
        print(json.dumps({"member":Path(name).name,"records":row["total_csv_records"],"blank":row["all_empty_records"]}),flush=True)
result={"status":"full_csv_record_integrity_census_not_experiment_ready", "completed_utc":datetime.now(timezone.utc).isoformat(),
    "source":"original-acquisition-full.json","members":rows,
    "total_csv_records":sum(r["total_csv_records"] for r in rows),
    "total_nonempty_records":sum(r["nonempty_records"] for r in rows),
    "total_all_empty_records":sum(r["all_empty_records"] for r in rows),
    "elapsed_seconds":round(time.monotonic()-started,3),"models_trained":False}
(DOCS/"original-csv-record-audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:result[k] for k in ["total_csv_records","total_nonempty_records","total_all_empty_records","elapsed_seconds"]}),flush=True)
