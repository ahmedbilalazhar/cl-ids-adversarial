# Reproducibility artifact (Phase-6 step 24): pinned CPU environment.
FROM python:3.11-slim
WORKDIR /work
# Thread pinning is part of the reproduction contract (decisions_log.md #52).
ENV CL_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY README.md ./
# Data + results are mounted, not baked in (CICIDS2017 raw ~843MB, UNSW/IoT
# mirrors documented in docs with URLs + row-count fingerprints).
# Reproduce: mount repo at /work and run `bash scripts/reproduce.sh <group>`.
CMD ["bash", "scripts/reproduce.sh", "c_e1"]
