"""Phase 3: own implementation of a federated continual intrusion-detection study with label poisoning.

Five simulated clients learn four stages (E1-E4) of attack families with a growing classification head.
Learners: FT (fine-tuning), EI (EWC-style, per-example diagonal Fisher), DR (DER++ replay).
Admission rules at each stage: NONE, DC (class-aware quota), DM (matched-volume global ranking), DQ (class-aware quota, random choice).
Poisoning: one client relabels a fraction of its DoS-Hulk training rows as benign during E2 only (withdrawn in E3-E4).
Everything is evaluated on a fixed development bank; no final-test data is read here.
Runs execute on CPU or GPU ('device'); all data and the replay memory live on that device. CPU and GPU results are not bit-identical,
so every paired comparison must use runs from one device type.
"""
from __future__ import annotations

import json
import hashlib
import math
import time
from dataclasses import asdict, dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.func import functional_call, grad, vmap

D_IN, CMAX, N_CLIENTS = 74, 16, 5
BENIGN, HULK = 0, 4


# ----------------------------------------------------------------------------- configuration and data
@dataclass(frozen=True)
class Cfg:
    learner: str = "FT"          # FT | EI | DR
    admission: str = "NONE"      # NONE | DC | DM | DQ  (DR only)
    seed: int = 101
    dose: float = 0.0            # fraction of each attacking client's Hulk rows relabelled benign in E2
    n_att: int = 1               # number of attacking clients (nested: the first k of a seeded order)
    rep: int = 0                 # training replicate within one ownership partition (0 = the original run)
    rounds: int = 12             # synchronisation rounds per stage
    epochs: int = 1              # local epochs per round
    lr: float = 1e-3
    batch: int = 256
    lam_E: float = 100.0         # EI penalty weight
    lam_y: float = 1.0           # DR replay-label weight
    lam_z: float = 0.1           # DR logit-matching weight
    mem: int = 500               # DR memory records per client
    replay_batch: int = 128
    buffer: str = "reservoir"    # reservoir | fifo (ablation)
    q: float = 0.75              # keep fraction of the class-aware quota
    nmin: int = 20               # classes smaller than this are kept whole
    intervention: str = "none"  # none | oracle_purge | random_delete; after E2 only
    fisher_n: int = 1024
    dropout: float = 0.1

    @property
    def sd(self) -> int:
        return self.seed + 1000 * self.rep        # seed for every random stream; the data package is chosen by self.seed only

    def tag(self) -> str:
        s = f"{self.learner}-{self.admission}-d{int(round(self.dose * 100)):03d}-k{self.n_att}-r{self.rep}-s{self.seed}"
        extras = []
        if self.intervention != "none": extras.append(self.intervention)
        if self.learner == "DR":
            if self.lam_z != 0.1: extras.append(f"z{self.lam_z:g}")
            if self.lam_y != 1.0: extras.append(f"y{self.lam_y:g}")
            if self.buffer != "reservoir": extras.append(self.buffer)
        for name, default in (("mem", 500), ("q", 0.75), ("nmin", 20), ("lr", 1e-3), ("lam_E", 100.0), ("rounds", 12)):
            if getattr(self, name) != default: extras.append(f"{name}{getattr(self, name):g}")
        return s + ("-" + "-".join(extras) if extras else "")


def load_taxonomy(path):
    t = json.load(open(path))
    cls = sorted(t["classes"], key=lambda c: c["source_code"])
    return {"names": {c["source_code"]: c["label"] for c in cls},
            "arrival": {c["source_code"]: c["arrival_stage"] for c in cls},
            "eligible": {c["source_code"] for c in cls if c["scoring_eligible"]},
            "dev_rows": {c["source_code"]: c["role_support_before_benign_selection"]["development"]["rows"] for c in cls},
            "train_rows": {c["source_code"]: c["selected_training_rows"] for c in cls}}


def load_stages(train_dir):
    out = []
    for s in range(1, 5):
        d = {k: np.load(f"{train_dir}/E{s}/{k}.npy") for k in ("x", "y", "ids", "owner")}
        out.append({"x": d["x"].astype(np.float32), "y": d["y"].astype(np.int64), "ids": d["ids"], "owner": d["owner"].astype(np.int64)})
    return out


def load_dev(dev_dir):
    return {"x": np.load(f"{dev_dir}/x.npy").astype(np.float32), "y": np.load(f"{dev_dir}/y.npy").astype(np.int64)}


def check_data(stages, dev, tax):
    """Integrity checks against the adopted taxonomy; returns (ok, messages)."""
    msgs, ok = [], True
    for c, n in tax["dev_rows"].items():
        got = int((dev["y"] == c).sum())
        if got != n: ok = False; msgs.append(f"dev class {c} ({tax['names'][c]}): {got} rows, taxonomy says {n}")
    for c, n in tax["train_rows"].items():
        got = sum(int((s["y"] == c).sum()) for s in stages)
        if got != n: ok = False; msgs.append(f"train class {c} ({tax['names'][c]}): {got} rows, taxonomy says {n}")
    for t, s in enumerate(stages, 1):
        arrived = {int(c) for c in np.unique(s["y"])} - {BENIGN}
        wrong = {c for c in arrived if tax["arrival"][c] != t}
        if wrong: ok = False; msgs.append(f"stage {t}: classes {sorted(wrong)} arrive in another stage per taxonomy")
    return ok, msgs


_UPLOADS = {}                    # device copies of large read-only arrays, kept for the life of the process


def upload(arr, device):
    key = (id(arr), str(device))
    if key not in _UPLOADS: _UPLOADS[key] = (arr, torch.from_numpy(arr).to(device))   # keep arr alive so id() stays unique
    return _UPLOADS[key][1]


# ----------------------------------------------------------------------------- model
class Net(nn.Module):
    def __init__(self, width, hidden=(128, 64), p=0.1):
        super().__init__()
        self.f1, self.f2, self.head, self.p = nn.Linear(D_IN, hidden[0]), nn.Linear(hidden[0], hidden[1]), nn.Linear(hidden[1], width), p

    def forward(self, x):
        h = F.dropout(F.relu(self.f1(x)), self.p, self.training)
        h = F.dropout(F.relu(self.f2(h)), self.p, self.training)
        return self.head(h)

    def grow(self, width, gen):
        old = self.head
        if width == old.out_features: return
        new = nn.Linear(old.in_features, width).to(old.weight.device)
        with torch.no_grad():
            new.weight.copy_((torch.randn(new.weight.shape, generator=gen) * 0.01).to(old.weight.device))
            new.bias.zero_()
            new.weight[: old.out_features] = old.weight
            new.bias[: old.out_features] = old.bias
        self.head = new


def n_params(model): return sum(p.numel() for p in model.parameters())


def clone_net(model):
    m = Net(model.head.out_features, (model.f1.out_features, model.f2.out_features), model.p).to(model.head.weight.device)
    m.load_state_dict(model.state_dict())
    return m


def fedavg(states, weights):
    """Sample-count weighted average, computed on the CPU in float64 for a device-independent reduction order."""
    w = np.asarray(weights, dtype=np.float64); w = w / w.sum()
    return {k: sum(float(wi) * s[k].detach().cpu().double() for wi, s in zip(w, states)).float() for k in states[0]}


# ----------------------------------------------------------------------------- poisoning and admission
def poison_stage(stage, cfg):
    """Relabel a prefix of each attacking client's (random, seeded) Hulk ordering as benign.
    Doses are nested prefixes; attackers are nested too (the first k of a seeded client order), so k=1 is contained in k=3 and k=5."""
    y = stage["y"].copy(); mask = np.zeros(len(y), bool)
    info = {"attacked_client": None, "attacked_clients": [], "eligible_clients": [], "eligible_hulk_rows": 0,
            "hulk_rows_stage": int((y == HULK).sum()), "flipped": 0}
    if cfg.dose <= 0: return y, mask, info
    counts = np.bincount(stage["owner"][y == HULK], minlength=N_CLIENTS)
    eligible = np.flatnonzero(counts >= 10)
    if not len(eligible): raise ValueError("No client holds ten Hulk rows")
    first = int(np.random.default_rng([cfg.sd, 2]).choice(eligible))
    rest = [int(c) for c in eligible if c != first]
    if rest: rest = [int(c) for c in np.random.default_rng([cfg.sd, 4]).permutation(rest)]
    attackers = ([first] + rest)[: min(max(cfg.n_att, 1), len(eligible))]
    total_src = flipped = 0
    for attacked in attackers:
        src = np.flatnonzero((stage["owner"] == attacked) & (y == HULK))
        src = src[np.argsort(stage["ids"][src], kind="stable")]
        perm = np.random.default_rng([cfg.sd, 3, attacked]).permutation(src)
        q = int(math.floor(cfg.dose * len(src)))
        y[perm[:q]] = BENIGN; mask[perm[:q]] = True
        total_src += len(src); flipped += q
    info.update(attacked_client=attackers[0], attacked_clients=attackers, eligible_clients=eligible.tolist(), eligible_hulk_rows=int(total_src), flipped=int(flipped))
    return y, mask, info


@torch.no_grad()
def row_losses(model, x_t, ys_t, chunk=16384):
    model.eval(); out = []
    for i in range(0, len(x_t), chunk):
        out.append(F.cross_entropy(model(x_t[i:i + chunk]), ys_t[i:i + chunk], reduction="none"))
    return torch.cat(out).cpu().numpy()


def admit(cfg, model, x_t, ys_t, ys, owner, ids, new_slots, rng):
    """Per-client admitted row indices (sorted). Scores come from the frozen model after head expansion."""
    per_client = [np.flatnonzero(owner == k) for k in range(N_CLIENTS)]
    if cfg.admission == "NONE": return per_client
    loss = row_losses(model, x_t, ys_t)
    chosen = []
    for rows in per_client:
        if len(rows) == 0: chosen.append(rows); continue
        yk = ys[rows]; quota = {}
        for c in np.unique(yk):
            n = int((yk == c).sum())
            quota[int(c)] = n if (int(c) in new_slots or n < cfg.nmin) else max(1, math.ceil(cfg.q * n))
        total = sum(quota.values())
        if cfg.admission == "DM":                                        # same volume, global ranking (loss ascending, ties by id)
            pick = rows[np.lexsort((ids[rows], loss[rows]))][:total]
        else:                                                            # DC: lowest loss within class; DQ: random within class
            pick = []
            for c, k in quota.items():
                cls_rows = rows[yk == c]
                if cfg.admission == "DC": pick.append(cls_rows[np.lexsort((ids[cls_rows], loss[cls_rows]))][:k])
                else: pick.append(cls_rows[rng.permutation(len(cls_rows))[:k]])
            pick = np.concatenate(pick)
        chosen.append(np.sort(pick))
    return chosen


# ----------------------------------------------------------------------------- DR memory (device resident)
class Buffer:
    def __init__(self, m, kind, rng, device):
        self.m, self.kind, self.rng, self.device, self.size, self.seen, self.ptr = m, kind, rng, device, 0, 0, 0
        self.x = torch.zeros((m, D_IN), device=device); self.y = torch.zeros(m, dtype=torch.long, device=device)
        self.z = torch.zeros((m, CMAX), device=device); self.w = torch.ones(m, dtype=torch.long, device=device)
        self.poison = np.zeros(m, bool)

    def insert(self, xb, yb, zb, w, poison):
        """Sequential reservoir (Algorithm R) or FIFO semantics; one device scatter per batch (last writer wins)."""
        last = {}
        for i in range(len(poison)):
            self.seen += 1
            if self.size < self.m: j = self.size; self.size += 1
            elif self.kind == "fifo": j = self.ptr; self.ptr = (self.ptr + 1) % self.m
            else:
                j = int(self.rng.integers(1, self.seen + 1))
                if j > self.m: continue
                j -= 1
            last[j] = i
        if not last: return
        jj = np.fromiter(last.keys(), np.int64, len(last)); ii = np.fromiter(last.values(), np.int64, len(last))
        jt, it = torch.from_numpy(jj).to(self.device), torch.from_numpy(ii).to(self.device)
        self.x[jt] = xb[it]; self.y[jt] = yb[it]; self.w[jt] = w
        self.z[jt] = F.pad(zb, (0, CMAX - zb.shape[1]))[it]
        self.poison[jj] = poison[ii]

    def sample(self, k):
        k = min(k, self.size); idx = torch.from_numpy(self.rng.choice(self.size, k, replace=False)).to(self.device)
        return self.x[idx], self.y[idx], self.z[idx], self.w[idx]

    def bytes(self):
        return int(self.size * (D_IN * 4 + CMAX * 4 + 8 + 8))


# ----------------------------------------------------------------------------- EWC-style importance
def fisher_diag(model, x_t, y_t):
    model.eval()
    params = {k: v.detach() for k, v in model.named_parameters()}

    def loss(p, xi, yi): return F.cross_entropy(functional_call(model, p, (xi.unsqueeze(0),)), yi.unsqueeze(0))
    g = vmap(grad(loss), in_dims=(None, 0, 0))(params, x_t, y_t)
    return {k: (v ** 2).mean(0) for k, v in g.items()}


def pad_like(t, shape):
    if t.shape == shape: return t
    out = torch.zeros(shape, dtype=t.dtype, device=t.device); out[tuple(slice(0, s) for s in t.shape)] = t; return out


def state_digest(model, buffers, slots, gen, rng_adm):
    """Fingerprint the entire pre-intervention scientific state, excluding config labels."""
    h = hashlib.sha256()
    for name, value in model.state_dict().items():
        h.update(name.encode()); h.update(value.detach().cpu().numpy().tobytes())
    for b in buffers:
        h.update(json.dumps([b.size, b.seen, b.ptr, b.rng.bit_generator.state], sort_keys=True).encode())
        for name in ('x', 'y', 'z', 'w'):
            h.update(getattr(b, name)[:b.size].detach().cpu().numpy().tobytes())
        h.update(b.poison[:b.size].tobytes())
    h.update(json.dumps([slots, rng_adm.bit_generator.state], sort_keys=True).encode())
    h.update(gen.get_state().numpy().tobytes()); h.update(torch.get_rng_state().numpy().tobytes())
    return h.hexdigest()


def delete_memory(buf, mode, rng):
    """Delete poison-count-matched records without advancing the ordinary buffer RNG."""
    before = buf.size
    count = int(buf.poison[:before].sum())
    drop = np.flatnonzero(buf.poison[:before]) if mode == 'oracle_purge' else rng.choice(before, count, replace=False)
    keep = np.setdiff1d(np.arange(before), drop)
    ix = torch.from_numpy(keep).to(buf.device)
    for name in ('x', 'y', 'z', 'w'):
        value = getattr(buf, name)
        value[:len(keep)] = value[ix].clone()
    buf.poison[:len(keep)] = buf.poison[keep].copy()
    buf.poison[len(keep):] = False
    buf.size, buf.ptr = len(keep), 0
    remaining = int(buf.poison[:buf.size].sum())
    if mode == 'oracle_purge': assert remaining == 0
    return dict(before=before, removed=count, after=buf.size, poison_remaining=remaining,
                historical_proposals=buf.seen, keep_slots=keep.tolist())


# ----------------------------------------------------------------------------- evaluation
@torch.no_grad()
def predict_codes(model, slots, x_t, chunk=32768):
    model.eval(); slots = np.asarray(slots); out = []
    for i in range(0, len(x_t), chunk): out.append(model(x_t[i:i + chunk]).argmax(1).cpu().numpy())
    return slots[np.concatenate(out)]


def stage_metrics(model, slots, dev, dev_x_t, tax, t, device):
    seen = [c for c, a in tax["arrival"].items() if a <= t]
    idx = np.flatnonzero(np.isin(dev["y"], seen)); yt = dev["y"][idx]
    yp = predict_codes(model, slots, dev_x_t[torch.from_numpy(idx).to(device)])
    conf = np.zeros((CMAX, CMAX), np.int64); np.add.at(conf, (yt, yp), 1)
    rows = {}
    for c in seen:
        sup = int(conf[c].sum())
        if sup == 0: continue
        tp, fn, fp = int(conf[c, c]), sup - int(conf[c, c]), int(conf[:, c].sum() - conf[c, c])
        prec = tp / (tp + fp) if tp + fp else 0.0; rec = tp / sup
        rows[c] = {"support": sup, "tp": tp, "fn": fn, "fp": fp, "precision": prec, "recall": rec,
                   "f1": (2 * prec * rec / (prec + rec)) if prec + rec else 0.0}
    elig = [c for c in rows if c in tax["eligible"]]
    benign_n = int(conf[BENIGN].sum())
    out = {"stage": t, "slots": [int(s) for s in slots], "classes": {int(c): r for c, r in rows.items()}, "eligible": [int(c) for c in elig],
           "macro_f1": float(np.mean([rows[c]["f1"] for c in elig])), "accuracy": float(np.trace(conf) / conf.sum()),
           "benign_far": float(1.0 - conf[BENIGN, BENIGN] / benign_n), "benign_rows": benign_n, "confusion": conf.tolist()}
    if HULK in rows:
        out["hulk_recall"] = rows[HULK]["recall"]; out["hulk_asr"] = float(conf[HULK, BENIGN] / conf[HULK].sum())
    return out


def summarize(stage_results, tax):
    """Acquisition A (untargeted new eligible classes, Hulk excluded), cohort recall matrix, BWT and forgetting."""
    A_vals = []
    for r in stage_results:
        t = r["stage"]
        new = [c for c in r["eligible"] if tax["arrival"][c] == t and c not in (BENIGN, HULK) and t >= 2]
        if new: A_vals.append(float(np.mean([r["classes"][c]["f1"] for c in new])))
    cohorts = {j: [c for c in stage_results[-1]["eligible"] if tax["arrival"][c] == j and c != BENIGN] for j in range(1, 5)}
    R = {}
    for r in stage_results:
        for j, cs in cohorts.items():
            if cs and j <= r["stage"]: R[(r["stage"], j)] = float(np.mean([r["classes"][c]["recall"] for c in cs if c in r["classes"]]))
    js = [j for j in range(1, 4) if (4, j) in R and (j, j) in R]
    bwt = float(np.mean([R[(4, j)] - R[(j, j)] for j in js])) if js else float("nan")
    forg = float(np.mean([max(R[(t, j)] for t in range(j, 5) if (t, j) in R) - R[(4, j)] for j in js])) if js else float("nan")
    return {"A": float(np.mean(A_vals)) if A_vals else float("nan"), "BWT": bwt, "forgetting": forg,
            "cohort_recall": {f"{t}-{j}": v for (t, j), v in R.items()}}


# ----------------------------------------------------------------------------- the experiment
def run(cfg: Cfg, stages, dev, tax, threads=1, device="cpu", progress=None):
    if cfg.learner not in ("FT", "EI", "DR"): raise ValueError("learner")
    if cfg.admission not in ("NONE", "DC", "DM", "DQ"): raise ValueError("admission")
    if cfg.admission != "NONE" and cfg.learner != "DR": raise ValueError("admission controls use DR")
    device = torch.device(device)
    torch.set_num_threads(threads); torch.manual_seed(cfg.sd)
    t0 = time.time(); gen = torch.Generator().manual_seed(cfg.sd)
    rng_adm = np.random.default_rng([cfg.sd, 5])
    dev_x_t = upload(dev["x"], device)
    model, slots, anchor, imp = None, [], None, None
    buffers = [Buffer(cfg.mem, cfg.buffer, np.random.default_rng([cfg.sd, 7, k]), device) for k in range(N_CLIENTS)] if cfg.learner == "DR" else None
    results, diag, comm_bytes, poison_info = [], [], 0, {}
    interventions = []
    pre_intervention_sha256 = None
    memory_trajectory = []
    if cfg.intervention not in ("none", "oracle_purge", "random_delete"): raise ValueError("intervention")
    if cfg.intervention != "none" and cfg.learner != "DR": raise ValueError("Replay intervention requires DR")
    for t in range(1, 5):
        s = stages[t - 1]; ids, owner = s["ids"], s["owner"]; x_t = upload(s["x"], device)
        if t == 2: y, pmask, poison_info = poison_stage(s, cfg)
        else: y, pmask = s["y"], np.zeros(len(s["y"]), bool)
        new_codes = sorted(set(np.unique(y).tolist()) - set(slots)); slots = slots + new_codes
        code2slot = np.full(CMAX, -1, np.int64); code2slot[slots] = np.arange(len(slots)); ys = code2slot[y]
        ys_t = torch.from_numpy(ys).to(device)
        if model is None: model = Net(len(slots), p=cfg.dropout).to(device)
        else:
            model.grow(len(slots), gen)
            if anchor is not None:                                  # new head rows: anchor = fresh initial value, importance = 0
                cur = dict(model.named_parameters())
                for n in anchor:
                    if anchor[n].shape != cur[n].shape:
                        a = cur[n].detach().clone(); a[tuple(slice(0, sz) for sz in anchor[n].shape)] = anchor[n]
                        anchor[n] = a; imp[n] = pad_like(imp[n], cur[n].shape)
        new_slots = {int(code2slot[c]) for c in new_codes}
        admitted = admit(cfg, model, x_t, ys_t, ys, owner, ids, new_slots, rng_adm)
        n_adm = [len(a) for a in admitted]
        d = {"stage": t, "rows": int(len(ys)), "admitted": int(sum(n_adm)), "poisoned_rows": int(pmask.sum()),
             "admitted_poisoned": int(sum(int(pmask[a].sum()) for a in admitted)), "per_client_admitted": n_adm,
             "new_class_rows": int(np.isin(y, new_codes).sum()), "new_class_rows_admitted": int(sum(int(np.isin(y[a], new_codes).sum()) for a in admitted))}
        active = [k for k in range(N_CLIENTS) if n_adm[k] > 0]
        for r in range(cfg.rounds):
            states = []
            for k in active:
                local = clone_net(model); opt = torch.optim.Adam(local.parameters(), lr=cfg.lr)
                rows = admitted[k]; lrng = np.random.default_rng([cfg.sd, t, r, k]); torch.manual_seed(cfg.sd * 1000 + t * 100 + r * 10 + k)
                for ep in range(cfg.epochs):
                    perm = rows[lrng.permutation(len(rows))]; perm_t = torch.from_numpy(perm).to(device)
                    for i in range(0, len(perm), cfg.batch):
                        bt = perm_t[i:i + cfg.batch]; xb, yb = x_t[bt], ys_t[bt]
                        local.train(); loss = F.cross_entropy(local(xb), yb)
                        if cfg.learner == "EI" and anchor is not None:
                            pen = sum((imp[n] * (p - anchor[n]) ** 2).sum() for n, p in local.named_parameters())
                            loss = loss + 0.5 * cfg.lam_E * pen
                        first = (r == 0 and ep == 0)
                        z_new = None
                        if cfg.learner == "DR":
                            if first:
                                local.eval()
                                with torch.no_grad(): z_new = local(xb)                                  # pre-update teacher logits
                                local.train()
                            buf = buffers[k]
                            if buf.size > 0:
                                xr, yr, zr, wr = buf.sample(cfg.replay_batch)
                                if cfg.lam_y > 0: loss = loss + cfg.lam_y * F.cross_entropy(local(xr), yr)
                                if cfg.lam_z > 0:
                                    local.eval(); outr = local(xr); local.train()
                                    pad = F.pad(outr, (0, CMAX - outr.shape[1])); mask = (torch.arange(CMAX, device=device)[None, :] < wr[:, None]).float()
                                    loss = loss + cfg.lam_z * ((((pad - zr) * mask) ** 2).sum(1) / wr.float()).mean()
                        opt.zero_grad(); loss.backward(); opt.step()
                        if z_new is not None: buffers[k].insert(xb, yb, z_new, len(slots), pmask[perm[i:i + cfg.batch]])
                states.append(local.state_dict())
            model.load_state_dict(fedavg(states, [n_adm[k] for k in active]))
            comm_bytes += 2 * 4 * n_params(model) * len(active)
        if cfg.learner == "EI":                                      # client-local Fisher at the final shared model, weighted average, accumulated
            fs, ws = [], []
            for k in active:
                rows = admitted[k]; sel = rows[np.random.default_rng([cfg.sd, 11, t, k]).permutation(len(rows))[: cfg.fisher_n]]
                st = torch.from_numpy(sel).to(device); fs.append(fisher_diag(model, x_t[st], ys_t[st])); ws.append(n_adm[k])
            w = np.asarray(ws, float) / sum(ws); new = {n: sum(float(wi) * f[n] for wi, f in zip(w, fs)) for n in fs[0]}
            imp = new if imp is None else {n: imp[n] + new[n] for n in new}
            anchor = {n: p.detach().clone() for n, p in model.named_parameters()}
        m = stage_metrics(model, slots, dev, dev_x_t, tax, t, device); results.append(m); diag.append(d)
        if buffers is not None:
            memory_trajectory.append(dict(stage=t, before_intervention=True,
                clients=[dict(size=b.size, poisoned=int(b.poison[:b.size].sum()), seen=b.seen) for b in buffers]))
        if t == 2 and buffers is not None:
            pre_intervention_sha256 = state_digest(model, buffers, slots, gen, rng_adm)
        if t == 2 and cfg.intervention != "none":
            for k, buf in enumerate(buffers):
                interventions.append(dict(client=k, **delete_memory(buf, cfg.intervention,
                    np.random.default_rng([cfg.sd, 991, k]))))
        if progress: progress(t, time.time() - t0)
    if device.type == "cuda": torch.cuda.synchronize()
    summ = summarize(results, tax)
    return {"cfg": asdict(cfg), "tag": cfg.tag(), "device": str(device), "stages": results, "admission": diag, "poison": poison_info, "summary": summ,
            "interventions": interventions,
            "pre_intervention_sha256": pre_intervention_sha256,
            "memory_trajectory": memory_trajectory,
            "cost": {"seconds": time.time() - t0, "model_bytes": 4 * n_params(model), "comm_bytes_total": int(comm_bytes),
                     "buffer_bytes_total": int(sum(b.bytes() for b in buffers)) if buffers else 0,
                     "buffer_poisoned_records_end": int(sum(int(b.poison[: b.size].sum()) for b in buffers)) if buffers else 0}}
