"""Read the immutable CPU selection; no duplicated tuning constants."""
from src.phase3.common import ROOT, digest, read_json
from .contracts import parse_settings

SELECTION = 'results/phase3-cpu-v3/development/tuning-selection.json'
SELECTION_SHA256 = '9f0b1a0e05fa7c329acee199d3236bf53c375e520a76763cf7264d7fc16d4fc4'


def selected_settings(learner, seed=101, admission='NONE', dose=(0, 1)):
    path = ROOT/SELECTION
    if digest(path) != SELECTION_SHA256:
        raise ValueError('CPU selection record changed')
    selected = read_json(path)['learners'][learner]['selected']
    if not selected['valid'] or not selected['feasible'] or not selected['gates']['passed']:
        raise ValueError('Selected condition is not feasible')
    return parse_settings({**selected['settings_without_seed'], 'seed': seed,
                           'admission': admission, 'dose': dose})
