import threading

_lock = threading.Lock()
_store: dict = {}
_next_id = [1]


def _info(entry: dict) -> dict:
    m = entry["matroid"]
    return {
        "id": entry["id"],
        "label": entry["label"],
        "n": len(m.ground_set),
        "rank": m.rank(m.ground_set),
        "num_bases": len(m.bases_sets),
        "ground_set": sorted(m.ground_set),
    }


def add(matroid, label: str) -> dict:
    with _lock:
        id_ = _next_id[0]
        _next_id[0] += 1
        _store[id_] = {"id": id_, "matroid": matroid, "label": label}
        return _info(_store[id_])


def get_all() -> list:
    with _lock:
        return [_info(e) for e in _store.values()]


def get(id_: int) -> dict | None:
    with _lock:
        return _store.get(id_)


def remove(id_: int) -> bool:
    with _lock:
        return _store.pop(id_, None) is not None
