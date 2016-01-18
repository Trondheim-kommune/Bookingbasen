# -*- coding: utf-8 -*-
import StringIO
from collections import Mapping
import copy
import csv
from collections import OrderedDict

from datetime import datetime
from itertools import chain
from operator import add
from flask import Response
import locale

same = lambda x: x  # identity function
_tuple = lambda x: (x,)  # python actually has coercion, avoid it like so


def flatten_dict(dictionary, key_reducer=add, key_lift=_tuple, init=()):
    # semi-lazy: goes through all dicts but lazy over all keys
    # reduction is done in a fold-left manner, i.e. final key will be
    # r((...r((r((r((init,k1)),k2)),k3))...kn))

    def _flatten_iter(pairs, _key_accum=init):
        atoms = ((k, v) for k, v in pairs if not isinstance(v, Mapping))
        submaps = ((k, v) for k, v in pairs if isinstance(v, Mapping))

        def compress(k):
            return key_reducer(_key_accum, key_lift(k))

        return chain(
            (
                (compress(k), v) for k, v in atoms
            ),
            *[
                _flatten_iter(submap.items(), compress(k))
                for k, submap in submaps
                ]
        )

    return OrderedDict(_flatten_iter(dictionary.items()))


def rewrite_list(data):
    if isinstance(data, list):
        i = 0
        while i < len(data):
            res = rewrite_list(data[i])
            if res is None:
                i += 1
            else:
                data.pop(i)
                data.extend(res)
                i = 0
        return data
    elif isinstance(data, Mapping):
        res = []
        for k, v in data.items():
            # if isinstance(v, list) or isinstance(v, Mapping):
            r = rewrite_list(v)
            if r is not None:
                if len(r) == 0:
                    data[k] = None
                else:
                    for item in r:
                        newitem = copy.deepcopy(data)
                        newitem[k] = item
                        v = rewrite_list(newitem)
                        if v is None:
                            res.append(newitem)
                        else:
                            res.extend(v)
                    break
        return res if len(res) > 0 else None
    else:
        return None


def expand_list(data):
    if isinstance(data, list):
        return rewrite_list(data)
    else:
        return rewrite_list([data])


def output_csv(data, code, headers=None, fieldname_mapping=None, fields_to_ignore=None):
    if fieldname_mapping is None:
        fieldname_mapping = {}

    if fields_to_ignore is None:
        fields_to_ignore = []

    lists_expanded = expand_list(data)
    result = []
    if lists_expanded:
        for listitem in lists_expanded:
            result.append({'_'.join(k): v for k, v in flatten_dict(listitem).items()})

    # get all fieldnames from result
    fieldnames = set()
    for listitem in result:
        fieldnames.update(listitem.keys())

    # remove ignored fieldnames
    for k in fields_to_ignore:
        fieldnames.discard(k)

    # Keep order from mapping
    ordered_fieldnames = fieldname_mapping.copy()

    # add missing fieldnames
    for k in fieldnames:
        if k not in ordered_fieldnames.keys():
            ordered_fieldnames.update({k: k})

    # remove reduntant fieldnames
    for k in ordered_fieldnames.keys():
        if k not in fieldnames:
            ordered_fieldnames.pop(k)

    stream = StringIO.StringIO()
    # Må først skrive utf-8 BOM slik at excel forstår at dette er utf-8
    stream.write(u'\uFEFF'.encode('utf-8'))
    # Må deretter sette semikolon som delimiter for at excel skal klare å oppfatte at dette er ei csv fil
    writer = csv.DictWriter(stream, ordered_fieldnames.values(), restval='', extrasaction='raise', dialect='excel', delimiter=';')
    writer.writeheader()

    locale.setlocale(locale.LC_ALL, "nb_NO.utf8")

    for row in result:
        writer.writerow(dict((fieldname_mapping[k] if k in fieldname_mapping.keys() else k, (v.encode('utf-8').replace('\r', ' ').replace('\n', ' ') if isinstance(v, basestring) else locale.format("%.1f", v) if isinstance(v, float) else v))
                             for k, v in row.iteritems()
                             if k not in fields_to_ignore))
    stream.seek(0)
    response = Response(response=stream, status=code)
    response.headers.extend(headers or {})
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename="eksport-' + datetime.today().isoformat() + '.csv"'

    return response
