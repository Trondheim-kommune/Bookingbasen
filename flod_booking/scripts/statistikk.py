#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
from collections import OrderedDict

from flod_common.session.utils import make_superuser_auth_cookie
from datetime import datetime
from flask import json
import requests
import os

import locale
locale.setlocale(locale.LC_ALL, "nb_NO.utf8")

BOOKING_URL = os.environ.get('BOOKING_URL', "http://localhost:1337")
RESOURCE_URL = os.environ.get('RESOURCE_URL', 'http://localhost:5000')
SERVICE_VERSION = os.environ.get('BOOKING_VERSION', 'v1')

FACILITY_STATISTICS_URI = '%s/api/%s/facilities' % (BOOKING_URL, SERVICE_VERSION) + '/%s/statistics'
RESOURCE_URI = '%s/api/%s/facilities/' % (RESOURCE_URL, SERVICE_VERSION)

VERBOSE = False


def get_statistics(start_date, end_date):
    result = []
    auth_token_cookie = make_superuser_auth_cookie()
    cookies = dict(auth_token_cookie.items())
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    resource_response = requests.get(RESOURCE_URI, cookies=cookies, headers=headers)

    if resource_response.status_code == 200:
        resource_data = json.loads(resource_response.content)
        if VERBOSE:
            print "facilities response data", resource_data

        data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }

        for facility in resource_data:
            facility_id = facility.get('id')
            if VERBOSE:
                print '\nRequesting statistics for facility %s (%s, %s)' % (facility_id, facility.get('name'), facility.get('uri'))

            facility_statistics_response = requests.get(FACILITY_STATISTICS_URI % facility_id, params=data, cookies=cookies, headers=headers)
            if facility_statistics_response.status_code == 200:
                facility_statistics_data = json.loads(facility_statistics_response.content)
                if VERBOSE:
                    print facility_statistics_data
                result.append({
                    # 'id': facility_id,
                    'unit_type': facility.get('unit_type').get('name'),
                    'unit_number': facility.get('unit_number'),
                    'unit_name': facility.get('unit_name'),
                    'name': facility.get('name'),
                    # 'facility_type': facility.get('facility_type').get('name'),
                    'hours': sum(float(item['hours']) for item in facility_statistics_data)})
            else:
                raise Exception("Could not load statistics for facility (id=%s, name=%s, uri=%s). Response code=%s" % (
                facility_id, facility.get('name'), facility.get('uri'), facility_statistics_response.status_code))

    else:
        raise Exception("Could not load facilities. Response code=%s" % resource_response.status_code)

    return result


def valid_date(s):
    try:
        return datetime.strptime(s, "%d-%m-%Y")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=valid_date, help="start date")
    parser.add_argument("end", type=valid_date, help="end date")
    parser.add_argument("-o", "--output", default="rapport.csv", help="name of file to write to")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    args = parser.parse_args()

    filename = args.output

    VERBOSE = args.verbose
    if VERBOSE:
        print "Collecting data for period %s - %s" % (args.start.strftime('%d-%m-%Y'), args.end.strftime('%d-%m-%Y'))

    statistics = get_statistics(args.start, args.end)

    fieldname_mapping = OrderedDict()
    fieldname_mapping['unit_type'] = 'Type enhet'
    fieldname_mapping['unit_number'] = 'Enhetskode'
    fieldname_mapping['unit_name'] = 'Navn på enhet'
    fieldname_mapping['name'] = 'Navn på lokalet'
    fieldname_mapping['hours'] = 'Antall timer utlån fra %s til %s' % (args.start.strftime('%d-%m-%Y'), args.end.strftime('%d-%m-%Y'))

    with open(filename, 'w') as f:
        # Må først skrive utf-8 BOM slik at excel forstår at dette er utf-8
        f.write(u'\uFEFF'.encode('utf-8'))
        # Må deretter sette semikolon som delimiter for at excel skal klare å oppfatte at dette er ei csv fil
        writer = csv.DictWriter(f, fieldname_mapping.values(), restval='', extrasaction='raise', dialect='excel', delimiter=';')
        writer.writeheader()

        for row in statistics:
            writer.writerow(
                dict((fieldname_mapping[k] if k in fieldname_mapping.keys() else k, (v.encode('utf-8').replace('\r', ' ').replace('\n', ' ') if isinstance(v, basestring) else locale.format("%.1f", v) if isinstance(v, float) else v))
                     for k, v in row.iteritems()))

        if VERBOSE:
            print "File %s written." % f.name
