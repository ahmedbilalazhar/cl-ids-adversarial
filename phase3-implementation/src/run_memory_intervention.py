"""Compatibility entry point for the identity-validated local CPU supplement."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from run_phase3_cpu_study import main
if __name__ == '__main__': main()
