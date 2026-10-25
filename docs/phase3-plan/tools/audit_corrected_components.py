"""Conditional corrected-release graph audit using its own rows/clock/schema."""
from audit_original_components import main,ROOT

if __name__=="__main__":
    main(work=ROOT/"data/raw/phase3-feasibility-corrected",
         census_file="corrected-component-input-manifest.json",
         metadata_file="component-metadata.csv",output_prefix="corrected",timestamp_kind="corrected")
