# Dataset and preprocessing
- Source: CICIDS2017-improved (corrected labels), downloaded and verified by SHA-256.
- 74 header-free flow features, repository-audited split; every pinned preparation file verified (A-8).
- Four arrival stages E1-E4 with the taxonomy in configs/phase3/taxonomy-v1.json; the class table is in dataset-classes.csv.
- Five clients: whole connected components are owned by exactly one client (no row-level leakage between clients); ownership is rebuilt per seed (101, 102, 103).
- Development bank only. Test rows exported: 0. Development rows in training packages: 0.
