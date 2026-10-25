"""Document/manifest consistency audit only; no implementation tests or training."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
DOCS = Path(__file__).resolve().parent
checks = []


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError("Duplicate JSON member: "+key)
        result[key]=value
    return result


def invalid_constant(value):
    raise ValueError("Non-standard JSON constant: "+value)


def record(name, ok, detail):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})


json_files = {}
for p in DOCS.glob("*.json"):
    if p.name in {"planning-validation.json", "delivery-manifest.json"}:
        continue
    try:
        json_files[p.name] = json.loads(p.read_text(encoding="utf-8-sig"),object_pairs_hook=unique_object,parse_constant=invalid_constant)
        record("JSON parses: " + p.name, True, "Document syntax only.")
    except Exception as exc:
        record("JSON parses: " + p.name, False, str(exc))

m = json_files["experiment-manifest.json"]
rows = m["full_trajectories"]
record("Unique logical full rows", len(rows) == 729 and len({r["planned_id"] for r in rows}) == 729, len(rows))
expected = {"core": 321, "course": 393, "focused": 441, "focused_external": 513, "complete": 633, "strengthened": 729}
for name, count in expected.items():
    actual = [r for r in rows if name in r["packages"]]
    record("Package count: " + name, len(actual) == count == m["summaries"][name]["total_full_logical"], {"actual": len(actual), "expected": count})
    record("Development count: " + name, sum(r["phase"] == "development" for r in actual) == 81, "81 logical rows; nine aliases are conditional.")
record("Conditional dev aliases", sum(bool(r.get("conditional_pilot_alias")) for r in rows) == 9, "Three learner defaults by three development seeds.")
record("Planning-only manifest", m["status"] == "planning_only_not_dispatchable" and not m["scope_selected"] and all(not r["executable"] for r in rows), "No dispatch-ready claim.")

seeds = set(range(1, 12)) | {42}
primary = [r for r in rows if r["group"] == "core"]
for arm in ["FT", "EI", "DR", "DM", "DC"]:
    for dose in [0, .1, .3, .5]:
        found = {r["seed"] for r in primary if r["arm"] == arm and r["dose"] == dose}
        record(f"Core pairing {arm} dose {dose}", found == seeds, sorted(found))

diagnostics = m["diagnostic_continuations"]
parents = {r["planned_id"] for r in rows}
record("Oracle logical/new counts", len(diagnostics) == 24 and sum(r["alias_if_exact"] is None for r in diagnostics) == 12, "24 logical rows, 12 new suffixes conditional on control alias validity.")
record("Diagnostic parents exist", all(r["parent"].split(":")[0] in parents for r in diagnostics), "Each references its matching primary DC E2 state.")

a = json_files["analysis-contrasts.json"]
c = a["contrasts"]
record("29 unique contrasts", len(c) == 29 and len({x["id"] for x in c}) == 29, len(c))
record("One Holm family", all(x["family"] == "all_29" for x in c), a["multiplicity"])
record("C1/C2 counts", sum(x["id"].startswith("C1") for x in c) == 18 and sum(x["id"].startswith("C2") for x in c) == 11, "18 + 11")
record("Fixed seed list", set(a["seeds"]) == seeds and len(a["seeds"]) == 12, a["seeds"])
record("Unavailable p not imputed metric", a["unavailable_endpoint"]["raw_p"] is None and a["unavailable_endpoint"]["holm_bookkeeping_p"] == 1, "Unavailable raw result remains distinct from Holm bookkeeping.")

links = []
for p in DOCS.glob("*.md"):
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "#")):
            continue
        target = target.split("#")[0]
        if not (p.parent / target).exists():
            links.append({"file": p.name, "missing_target": target})
record("Local document links resolve", not links, links)

sources = json_files["sources.json"]["sources"]
record("Unique primary-source IDs", len(sources) == len({x["id"] for x in sources}), len(sources))
record("Source verification limits present", all(x.get("verification") and x.get("limits") and x["url"].startswith("https://") for x in sources), "No claim of exhaustive source verification.")
e = json_files["data-acquisition-evidence.json"]
record("Bounded header evidence", len(e["samples"]) == 5 and all(x["column_count"] == 91 for x in e["samples"]) and not e["full_archive_downloaded"], {"probe_bytes": e["transferred_bytes"], "full_audit": False})
record("Model/replay payload arithmetic", 128*76 + 8384 + 65*15 == 19087 and 19087*4 == 76348 and (4*76+4*15+17)*500 == 190500, "19,087 parameters; 76,348 raw model bytes; 190,500 raw replay bytes/client.")

gap_ids=[]
for name in ["implementation-gap-audit.md","second-audit-gap-register.md"]:
    gap_ids += [int(x) for x in re.findall(r"^\| G(\d+) \|",(DOCS/name).read_text(encoding="utf-8"),flags=re.M)]
record("Combined gap IDs G01-G64",sorted(gap_ids)==list(range(1,65)),"64 distinct registered concerns; not 62 implemented fixes.")
amendments=[int(x) for x in re.findall(r"^\| A(\d+) \|",(DOCS/"amendment-register.md").read_text(encoding="utf-8"),flags=re.M)]
record("Prospective amendment IDs A01-A32",amendments==list(range(1,33)),"Adoption status remains explicit.")
for release in ["original","corrected"]:
    ledger=json_files[f"{release}-domain-checked-exclusion-accounting.json"]
    record("Additive screened source ledger: "+release,sum(ledger["primary_reason_counts"].values())==ledger["source_csv_records"] and all(sum(f["primary_reasons"].values())==f["source_records"] for f in ledger["families"]),"Arithmetic on recorded candidate evidence; not independent raw-data reproduction.")
split=json_files["corrected-domain-checked-candidate-split-feasibility.json"]
record("Recorded screened split conservation/isolation",sum(split["role_counts"].values())==split["rows"]==1362039 and all(v==0 for v in split["cross_role_component_intersections"].values()),"Checks recorded report consistency, not a fresh graph reconstruction.")
profile=json_files["candidate-data-profiles.json"]
adoption_path=DOCS/"../phase3-reference/adoption.json"
historical_candidate=profile["selected_profile"] is None and profile["status"]=="prospective_candidate_profiles_not_dispatchable"
adopted_reference=(profile["selected_profile"]=="corrected_no_headers_74" and adoption_path.exists()
    and json.loads(adoption_path.read_text(encoding="utf-8"))["gpu_grid_dispatchable"] is False)
record("Data profile disposition explicit; grid gated",historical_candidate or adopted_reference,"A later user-authorized reference adoption is separate from GPU grid dispatch.")
schema=json_files["candidate-feature-schema.json"]
record("Packaged ordered candidate schema",len(schema["features"])==len(set(schema["features"]))==schema["feature_count"]==76,"Same ordered list as the source census; semantic/unit review remains separate.")
quota=json_files["quota-feasibility-summary.json"]
record("Recorded quota bound arithmetic",all(r["minimum_poison_L"]==max(0,r["quota_K"]-r["honest_benign_b"]) and r["maximum_poison_U"]==min(r["flipped_q"],r["quota_K"]) for r in quota["rows"]),"No actual loss-selected poison counts are present.")
reduced=json_files["corrected-no-headers-74-candidate-split-feasibility.json"]
record("74-feature fixed-split reuse evidence",all(reduced["split_reuse"]["checks"].values()) and not reduced["split_reuse"]["new_allocator_execution"],"Includes full transformed-byte projection, canonical groups, fitting IDs and ordered selected labels; recorded evidence only.")
ledger74=json_files["corrected-no-headers-74-exclusion-accounting.json"]
record("74-feature additive source ledger",sum(ledger74["primary_reason_counts"].values())==ledger74["source_csv_records"] and ledger74["primary_reason_counts"]["retained_candidate"]==1362527,"Separate candidate; no silent relabeling of older evidence.")
provenance=json_files["annotation-provenance-census.json"]
record("Benign provenance accounting",all(r["original_background"]+r["remapped_attempted"]==r["benign_total"] for r in provenance["role_census"]) and all(r["selected_benign"]==3500==r["original_background"]+r["remapped_attempted"] for r in provenance["selected_training_benign"]),"Population counts only; false-alarm outcomes are unavailable.")
record("74-input resource arithmetic",128*74+8384+65*16==18896 and 18896*4==75584 and (4*74+4*16+17)*500==188500,"Logical payload, not measured allocator or serialization cost.")

source_files = [p for p in DOCS.rglob("*") if p.is_file() and p.suffix in {".md", ".json", ".py"} and p.name not in {"planning-validation.json", "delivery-manifest.json"}]
hashes = [{"file": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(source_files)]
result = {"scope": "Planning document/manifest consistency only; no model tests, training, data-support audit or GPU benchmark.", "checks": checks, "passed": all(c["passed"] for c in checks), "source_hashes_at_audit": hashes}
(DOCS / "planning-validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"checks": len(checks), "passed": result["passed"], "failed": [c for c in checks if not c["passed"]]}, indent=2))
if not result["passed"]:
    raise SystemExit(1)
