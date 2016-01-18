# -*- coding: utf-8 -*-
def merge(times):
    '''
    Merge list of tuples of from/to values where tuples are overlapping or adjacent. Each value-pair is sorted before the list is sorted.
    :param times: list containing tuples to merge
    :return: list iterator of merged tuples
    '''
    if not times:
        return
    sorted_times = sorted([sorted(t) for t in times])
    saved = sorted_times[0]
    for st, en in sorted_times:
        if st <= saved[1]:
            saved[1] = max(saved[1], en)
        else:
            yield tuple(saved)
            saved[0] = st
            saved[1] = en
    yield tuple(saved)