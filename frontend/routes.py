from flask import Blueprint, render_template, request, jsonify
import itertools
import signal
import numpy as np

from chromatic_matroids import (
    Matroid,
    uniform_matroid,
    schubert_matroid,
    nested_matroid,
    graphic_matroid,
    generate_schubert_matroids,
    generate_loopless_nested_matroids,
    generate_nested_matroids_doublechains,
    chromatic_quasisymmetric_function,
    chromatic_non_commutative_quasisymmetric_function,
    smith_normal_form_factors,
    z_rank,
    z_index,
    invariant_factors,
    SetComposition,
    Composition,
    from_set_to_set_composition,
    generate_valid_subsets,
    generate_min_max_set_compositions,
)
from . import operations

bp = Blueprint("app", __name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _mat_to_dict(m, label):
    return {
        "label": label,
        "ground_set": sorted(m.ground_set),
        "bases": sorted(sorted(b) for b in m.bases_sets),
        "n": len(m.ground_set),
        "rank": m.rank(m.ground_set),
        "num_bases": len(m.bases_sets),
    }


def _dict_to_mat(d):
    return Matroid(
        frozenset(int(x) for x in d["ground_set"]),
        {frozenset(int(x) for x in b) for b in d["bases"]},
    )


# ── Size guard ────────────────────────────────────────────────────────────────
_MAX_N = 9

def _check_size(n: int):
    if n > _MAX_N:
        raise ValueError(f"Ground set too large (n={n}). Maximum allowed is n={_MAX_N}.")


# ── Computation timeout (Linux/Unix only) ──────────────────────────────────────
_TIMEOUT_SECONDS = 15

class _Timeout(Exception):
    pass

def _alarm_handler(signum, frame):
    raise _Timeout()

def _run_timed(fn, *args):
    """Run fn(*args) and raise TimeoutError if it takes more than _TIMEOUT_SECONDS."""
    old = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(_TIMEOUT_SECONDS)
    try:
        return fn(*args)
    except _Timeout:
        raise TimeoutError(
            f"Computation aborted — took more than {_TIMEOUT_SECONDS} s. "
            "Try fewer or smaller matroids."
        )
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


# ── Per-process WQSym cache (keyed by sorted-bases canonical form) ─────────────
_wqsym_cache: dict = {}


def _bases_key(m):
    """Cheap canonical key: sorted bases after normalising ground set to {1,...,n}."""
    gs = sorted(m.ground_set)
    idx = {e: i + 1 for i, e in enumerate(gs)}
    return tuple(sorted(tuple(sorted(idx[e] for e in b)) for b in m.bases_sets))


def _cached_wqsym(m):
    key = _bases_key(m)
    if key not in _wqsym_cache:
        _wqsym_cache[key] = chromatic_non_commutative_quasisymmetric_function(m)
    return _wqsym_cache[key]


def _canonical_form(m):
    """Canonical form identifying a matroid up to isomorphism."""
    n = len(m.ground_set)
    gs = sorted(m.ground_set)
    idx = {e: i for i, e in enumerate(gs)}
    norm = [tuple(sorted(idx[e] for e in b)) for b in m.bases_sets]
    if n <= 8:
        best = None
        for p in itertools.permutations(range(n)):
            rep = tuple(sorted(tuple(sorted(p[e] for e in b)) for b in norm))
            if best is None or rep < best:
                best = rep
        return best
    return tuple(sorted(norm))


# ── Page ───────────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    return render_template("index.html")


# ── Create ─────────────────────────────────────────────────────────────────────

@bp.route("/api/create/uniform", methods=["POST"])
def create_uniform():
    try:
        d = request.json
        n, r = int(d["n"]), int(d["r"])
        return jsonify(_mat_to_dict(uniform_matroid(n, r), f"U({n},{r})"))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/nested", methods=["POST"])
def create_nested():
    try:
        d = request.json
        n = int(d["n"])
        rank = int(d["rank"])
        parts = [[int(x) for x in p] for p in d["parts"]]
        rank_bounds = [int(r) for r in d["rank_bounds"]]
        X, cumulative = [], set()
        for p in parts:
            cumulative |= set(p)
            X.append(frozenset(cumulative))
        m = nested_matroid(n, rank, tuple(X), tuple(rank_bounds))
        parts_str = " | ".join(",".join(str(x) for x in p) for p in parts)
        label = f"ne({n},{rank}; {parts_str}; {','.join(str(r) for r in rank_bounds)})"
        return jsonify(_mat_to_dict(m, label))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/loopless_nested", methods=["POST"])
def create_loopless_nested():
    try:
        n = int(request.json["n"])
        matroids = generate_loopless_nested_matroids(n)
        chains = generate_nested_matroids_doublechains(n)
        result = []
        for m, (_, rank, X, R) in zip(matroids, chains):
            prev = frozenset()
            parts = []
            for xi in X:
                parts.append(sorted(xi - prev))
                prev = xi
            parts_str = "|".join(",".join(str(x) for x in p) for p in parts)
            label = f"ne({n},{rank};{parts_str};{','.join(str(r) for r in R)})"
            result.append(_mat_to_dict(m, label))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/graphic", methods=["POST"])
def create_graphic():
    try:
        d = request.json
        edge_pairs = [tuple(e) for e in d["edges"]]
        vertex_set = set(d["vertices"])
        raw = graphic_matroid(edge_pairs, vertex_set)
        edge_list = sorted(raw.ground_set)
        relabeling = {edge: i + 1 for i, edge in enumerate(edge_list)}
        m = raw.relabel(relabeling)
        v, e = len(vertex_set), len(edge_pairs)
        return jsonify(_mat_to_dict(m, f"M(G,{v}v,{e}e)"))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/from_bases", methods=["POST"])
def create_from_bases():
    try:
        d = request.json
        ground = frozenset(int(x) for x in d["ground_set"])
        bases = {frozenset(int(x) for x in b) for b in d["bases"]}
        m = Matroid(ground, bases)
        return jsonify(_mat_to_dict(m, d.get("label") or "M"))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/matrix", methods=["POST"])
def create_from_matrix():
    try:
        d = request.json
        raw = d.get("matrix", "").strip()
        if not raw:
            raise ValueError("Empty matrix.")
        rows = []
        for line in raw.splitlines():
            vals = [float(x) for x in line.replace(",", " ").split()]
            if vals:
                rows.append(vals)
        if not rows:
            raise ValueError("No numeric rows found.")
        ncols = len(rows[0])
        if any(len(r) != ncols for r in rows):
            raise ValueError("All rows must have the same number of columns.")
        _check_size(ncols)
        mat = np.array(rows, dtype=float)
        rank = int(np.linalg.matrix_rank(mat))
        bases = set()
        for cols in itertools.combinations(range(ncols), rank):
            if int(np.linalg.matrix_rank(mat[:, list(cols)])) == rank:
                bases.add(frozenset(c + 1 for c in cols))
        if not bases:
            raise ValueError("No bases found (is the matrix all zeros?).")
        label = d.get("label") or f"M(mat,{len(rows)}×{ncols})"
        return jsonify(_mat_to_dict(Matroid(frozenset(range(1, ncols + 1)), bases), label))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/schubert_by_rank", methods=["POST"])
def create_schubert_by_rank():
    try:
        d = request.json
        n, rank = int(d["n"]), int(d["rank"])
        _check_size(n)
        result = []
        for A in itertools.combinations(range(1, n + 1), rank):
            m = schubert_matroid(n, frozenset(A))
            label = "sh({},{{{}}})".format(n, ",".join(str(a) for a in A))
            result.append(_mat_to_dict(m, label))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/create/schubert", methods=["POST"])
def create_schubert():
    try:
        d = request.json
        n = int(d["n"])
        _check_size(n)
        result = []
        for rank in range(n + 1):
            for A in itertools.combinations(range(1, n + 1), rank):
                m = schubert_matroid(n, frozenset(A))
                label = "sh({},{{{}}})".format(n, ",".join(str(a) for a in A))
                result.append(_mat_to_dict(m, label))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ── Operations ─────────────────────────────────────────────────────────────────

@bp.route("/api/create/loopless_nested_by_rank", methods=["POST"])
def create_loopless_nested_by_rank():
    try:
        d = request.json
        n = int(d["n"])
        rank = int(d["rank"])
        matroids = generate_loopless_nested_matroids(n)
        chains = generate_nested_matroids_doublechains(n)
        result = []
        for m, (_, r, X, R) in zip(matroids, chains):
            if r != rank:
                continue
            prev = frozenset()
            parts = []
            for xi in X:
                parts.append(sorted(xi - prev))
                prev = xi
            parts_str = "|".join(",".join(str(x) for x in p) for p in parts)
            label = f"ne({n},{rank};{parts_str};{','.join(str(ri) for ri in R)})"
            result.append(_mat_to_dict(m, label))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/ops/deduplicate", methods=["POST"])
def op_deduplicate():
    items = request.json  # list of matroid dicts (includes client-side id, label, etc.)
    seen = set()
    result = []
    for item in items:
        try:
            cf = _canonical_form(_dict_to_mat(item))
        except Exception:
            cf = None
        if cf not in seen:
            seen.add(cf)
            result.append(item)
    return jsonify(result)


@bp.route("/api/ops/delete_elements", methods=["POST"])
def op_delete_elements():
    try:
        d = request.json
        m = _dict_to_mat(d)
        elems = [int(x) for x in d["elements"]]
        new_m = operations.delete(m, elems)
        elems_str = ",".join(str(e) for e in sorted(elems))
        label = r"{}\{{{}}}".format(d.get("label", "M"), elems_str)
        return jsonify(_mat_to_dict(new_m, label))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/ops/contract", methods=["POST"])
def op_contract():
    try:
        d = request.json
        m = _dict_to_mat(d)
        elems = [int(x) for x in d["elements"]]
        new_m = operations.contract(m, elems)
        elems_str = ",".join(str(e) for e in sorted(elems))
        label = "{}/{{{}}}".format(d.get("label", "M"), elems_str)
        return jsonify(_mat_to_dict(new_m, label))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/ops/direct_sum", methods=["POST"])
def op_direct_sum():
    try:
        d = request.json
        m1 = _dict_to_mat(d["m1"])
        m2 = _dict_to_mat(d["m2"])
        new_m = operations.direct_sum(m1, m2)
        label = "({} ⊕ {})".format(d["m1"].get("label", "M1"), d["m2"].get("label", "M2"))
        return jsonify(_mat_to_dict(new_m, label))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ── Compute ────────────────────────────────────────────────────────────────────

@bp.route("/api/compute/qsym", methods=["POST"])
def compute_qsym():
    items = request.json
    results = []
    for item in items:
        try:
            m = _dict_to_mat(item)
            _check_size(len(m.ground_set))
            q = _run_timed(chromatic_quasisymmetric_function, m)
            results.append({
                "label": item.get("label", "M"),
                "coefficients": {k: v for k, v in sorted(q.coefficients.items()) if v != 0},
            })
        except Exception as e:
            results.append({"label": item.get("label", "M"), "error": str(e)})
    return jsonify(results)


@bp.route("/api/compute/wqsym", methods=["POST"])
def compute_wqsym():
    items = request.json
    results = []
    for item in items:
        try:
            m = _dict_to_mat(item)
            _check_size(len(m.ground_set))
            nc = _run_timed(_cached_wqsym, m)
            results.append({
                "label": item.get("label", "M"),
                "coefficients": {k: v for k, v in sorted(nc.coefficients.items()) if v != 0},
            })
        except Exception as e:
            results.append({"label": item.get("label", "M"), "error": str(e)})
    return jsonify(results)


@bp.route("/api/compute/zrank", methods=["POST"])
def compute_zrank():
    items = request.json
    funcs, labels = [], []
    for item in items:
        try:
            m = _dict_to_mat(item)
            _check_size(len(m.ground_set))
            nc = _run_timed(_cached_wqsym, m)
            funcs.append(nc)
            labels.append(item.get("label", "M"))
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    if not funcs:
        return jsonify({"rank": 0, "rows": 0, "cols": 0, "labels": []})

    keys = sorted({k for f in funcs for k in f.coefficients})
    mat = [[f.coefficients.get(k, 0) for k in keys] for f in funcs]
    rank = int(np.linalg.matrix_rank(np.array(mat, dtype=float)))
    return jsonify({"rank": rank, "rows": len(funcs), "cols": len(keys), "labels": labels})


@bp.route("/api/compute/zindex", methods=["POST"])
def compute_zindex():
    items = request.json
    funcs, labels = [], []
    for item in items:
        try:
            m = _dict_to_mat(item)
            _check_size(len(m.ground_set))
            nc = _run_timed(_cached_wqsym, m)
            funcs.append(nc)
            labels.append(item.get("label", "M"))
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    if not funcs:
        return jsonify({"index": 1, "factors": [], "rank": 0, "rows": 0, "cols": 0, "labels": []})

    keys = sorted({k for f in funcs for k in f.coefficients})
    mat = [[f.coefficients.get(k, 0) for k in keys] for f in funcs]
    factors = smith_normal_form_factors(mat)  # from chromatic_matroids package
    idx = 1
    for d in factors:
        idx *= d
    return jsonify({
        "index": idx,
        "factors": factors,
        "rank": len(factors),
        "rows": len(funcs),
        "cols": len(keys),
        "labels": labels,
    })


# ── Matrix Explorer ────────────────────────────────────────────────────────────

@bp.route("/api/matrix/compute", methods=["POST"])
def compute_matrix():
    try:
        d = request.json
        n = int(d["n"])
        rank_filter = d.get("rank")
        mode = d.get("mode", "noncommutative")
        matroid_family = d.get("matroid_family", "loopless_nested")
        col_set = d.get("col_set", "proof_sts")

        _check_size(n)

        needs_rank = matroid_family in ("loopless_nested_by_rank", "schubert_by_rank")
        rk = int(rank_filter) if rank_filter is not None else None
        if needs_rank and rk is None:
            return jsonify({"error": "rank r is required for the selected matroid family."}), 400

        # Build row matroids
        row_matroids = []
        if matroid_family in ("loopless_nested", "loopless_nested_by_rank"):
            mats = generate_loopless_nested_matroids(n)
            chains = generate_nested_matroids_doublechains(n)
            for m, (_, r, X, R) in zip(mats, chains):
                if needs_rank and r != rk:
                    continue
                prev = frozenset()
                parts = []
                for xi in X:
                    parts.append(sorted(xi - prev))
                    prev = xi
                parts_str = "|".join(",".join(str(x) for x in p) for p in parts)
                label = f"ne({n},{r};{parts_str};{','.join(str(ri) for ri in R)})"
                row_matroids.append((m, label))
        else:  # schubert family
            ranks_to_use = [rk] if needs_rank else list(range(n + 1))
            for r in ranks_to_use:
                for A in itertools.combinations(range(1, n + 1), r):
                    m = schubert_matroid(n, frozenset(A))
                    label = "sh({},{{{}}})".format(n, ",".join(str(a) for a in A))
                    row_matroids.append((m, label))

        if not row_matroids:
            return jsonify({"error": "No matroids found for the given parameters."}), 400

        # Build columns and coefficient extractor
        if mode == "noncommutative":
            if col_set == "proof_sts":
                valid_ss = sorted(generate_valid_subsets(n), key=lambda x: (len(x), sorted(x)))
                cols = [from_set_to_set_composition(A, n) for A in valid_ss]
            elif col_set == "minmax":
                cols = generate_min_max_set_compositions(n)
            elif col_set == "all_setcompositions":
                cols = SetComposition.generate_all_setcompositions(n)
            else:
                return jsonify({"error": f"Unknown col_set '{col_set}'."}), 400
            col_labels = [str(sc) for sc in cols]

            def _row_coeffs(m):
                nc = _run_timed(_cached_wqsym, m)
                return [nc.coefficients.get(key, 0) for key in col_labels]
        else:  # commutative
            comps = Composition.generate_all_composition(n)
            col_labels = [str(c) for c in comps]

            def _row_coeffs(m):
                q = _run_timed(chromatic_quasisymmetric_function, m)
                return [q.coefficients.get(key, 0) for key in col_labels]

        # Build matrix
        matrix = []
        for m, _ in row_matroids:
            _check_size(len(m.ground_set))
            matrix.append(_row_coeffs(m))

        row_labels = [lbl for _, lbl in row_matroids]

        arr = np.array(matrix, dtype=float) if matrix else np.zeros((0, len(col_labels)))
        span_dim = int(np.linalg.matrix_rank(arr)) if arr.size else 0

        return jsonify({
            "row_labels": row_labels,
            "col_labels": col_labels,
            "matrix": matrix,
            "span_dim": span_dim,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
