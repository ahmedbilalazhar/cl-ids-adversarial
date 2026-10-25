"""Audit a prospective physical-domain quarantine before T0 fitting.

This is a separate data-methodology candidate, not a silent source correction.
Initial TCP windows retain the declared -1 sentinel. No values are clipped or
reconstructed. Excluded rows retain their conservative provenance links.
"""
import argparse
from audit_original_components import main,ROOT

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release",choices=["original","corrected"],required=True)
    release=parser.parse_args().release
    work=ROOT/f"data/raw/phase3-feasibility-{release}"
    main(work=work,
         census_file="original-full-census.json" if release=="original" else "corrected-component-input-manifest.json",
         metadata_file="feasibility-metadata.csv" if release=="original" else "component-metadata.csv",
         output_prefix=f"{release}-domain-checked",timestamp_kind=release,
         domain_policy="nonnegative_flow_features_with_window_sentinel_v1",output_work=work/"domain-checked")
