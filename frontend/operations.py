from chromatic_matroids import Matroid


def delete(matroid: Matroid, elements_to_remove) -> Matroid:
    """Restriction to complement: remove elements, keep the rest."""
    elements = frozenset(elements_to_remove)
    new_ground = matroid.ground_set - elements
    if not new_ground:
        return Matroid(frozenset(), {frozenset()})
    ind = matroid.independent_sets()
    ind_in_new = {i for i in ind if i.issubset(new_ground)}
    max_size = max((len(i) for i in ind_in_new), default=0)
    new_bases = {i for i in ind_in_new if len(i) == max_size} or {frozenset()}
    return Matroid(new_ground, new_bases)


def contract(matroid: Matroid, elements_to_contract) -> Matroid:
    """Contract a set of elements."""
    elements = frozenset(elements_to_contract)
    if not elements:
        return Matroid(matroid.ground_set, set(matroid.bases_sets))
    new_ground = matroid.ground_set - elements
    if not new_ground:
        return Matroid(frozenset(), {frozenset()})
    ind = matroid.independent_sets()
    # largest independent set contained in elements
    I = max((i for i in ind if i.issubset(elements)), key=len, default=frozenset())
    new_bases = {b - elements for b in matroid.bases_sets if I.issubset(b)}
    return Matroid(new_ground, new_bases or {frozenset()})


def direct_sum(m1: Matroid, m2: Matroid) -> Matroid:
    """Direct sum; relabels m2 so ground sets are disjoint."""
    if not m1.ground_set:
        return Matroid(set(m2.ground_set), set(m2.bases_sets))
    if not m2.ground_set:
        return Matroid(set(m1.ground_set), set(m1.bases_sets))
    offset = max(m1.ground_set)
    m2r = m2.relabel({e: e + offset for e in m2.ground_set})
    new_ground = m1.ground_set | m2r.ground_set
    new_bases = {b1 | b2 for b1 in m1.bases_sets for b2 in m2r.bases_sets}
    return Matroid(new_ground, new_bases)
