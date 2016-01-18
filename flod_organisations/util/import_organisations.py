# -*- coding: utf-8 -*-
import json
from argparse import ArgumentParser

import requests

import xlrd
import os
import sys


os.environ['AUTH_TOKEN_SECRET'] = 'Super Secret Auth Token!'
os.environ['AUTH_ADMIN_USER_ID'] = 'FlodSuperUser'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flod_common.session.utils import make_superuser_auth_cookie

import_fields = {
    0: {'tk': 'Registrert i Trondheim kulturnettverk', 'flod': 'registered_tkn'},
    1: {'tk': 'Orgnr', 'flod': 'org_number'},
    2: {'tk': 'Navn', 'flod': 'name'},
    3: {'tk': 'Forretningsadresse', 'flod': {'tag': 'business_address', 'value_slot': 'address_line'}},
    4: {'tk': 'Forradr postnr', 'flod': {'tag': 'business_address', 'value_slot': 'postal_code'}},
    5: {'tk': 'Forradr poststed', 'flod': {'tag': 'business_address', 'value_slot': 'postal_city'}},
    6: {'tk': 'Postadresse', 'flod': {'tag': 'postal_address', 'value_slot': 'address_line'}},
    7: {'tk': 'Postnr', 'flod': {'tag': 'postal_address', 'value_slot': 'postal_code'}},
    8: {'tk': 'Poststed', 'flod': {'tag': 'postal_address', 'value_slot': 'postal_code'}},
    9: {'tk': 'Organisasjonsform', 'flod': 'org_form'},
    10: {'tk': 'Reg. i FR', 'flod': None},
    11: {'tk': 'Reg. i ER', 'flod': None},
    12: {'tk': 'Telefon', 'flod': 'phone_number'},
    13: {'tk': 'Telefaks', 'flod': 'telefax_number'},
    14: {'tk': 'Mobil', 'flod': None},
    15: {'tk': 'E-post adresse', 'flod': 'email_address'},
    16: {'tk': 'Internett adresse', 'flod': 'url'},
    17: {'tk': 'Rolletype', 'flod': {'tag': 'people', 'value_slot': 'role'}},
    18: {'tk': 'Referanse', 'flod': {'tag': 'people', 'value_slot': 'name'}},
    19: {'tk': 'Refreranse adresse', 'flod': {'tag': 'people', 'value_slot': 'address_line'}},
    20: {'tk': 'Referanse adresse pnr', 'flod': {'tag': 'people', 'value_slot': 'postal_code'}},
    21: {'tk': 'referanse adr sted', 'flod': {'tag': 'people', 'value_slot': 'postal_city'}},
    22: {'tk': 'Grasrot', 'flod': None},
    23: {'tk': 'Kategori', 'flod': 'activity_code'},
    24: {'tk': 'Beskrivelse av kategori', 'flod': 'activity_desc'},
    25: {'tk': 'Kontonummer (Fra Brreg)', 'flod': None},
    26: {'tk': 'LEDER', 'flod': {'tag': 'people', 'value_slot': 'name', 'add_data': {'role': 'Leder'}}},
    27: {'tk': 'LEDER TELEFON', 'flod': {'tag': 'people', 'value_slot': 'phone_number'}},
    28: {'tk': 'E-POSTADRESSE', 'flod': {'tag': 'people', 'value_slot': 'email_address'}},
    29: {'tk': 'KASSERER', 'flod': {'tag': 'people_k', 'value_slot': 'name', 'add_data': {'role': 'Kasserer'}}},
    30: {'tk': 'KASSERER E-POST', 'flod': {'tag': 'people_k', 'value_slot': 'email_address'}},
    31: {'tk': 'KASSERER TELEFON', 'flod': {'tag': 'people_k', 'value_slot': 'phone_number'}},
    32: {'tk': 'Beskrivelse', 'flod': 'description'},
    33: {'tk': 'ANTALL MEDL', 'flod': 'num_members'},
    34: {'tk': 'Kontonummer (Hvis ikke i brreg)', 'flod': None},
    35: {'tk': 'Bydel', 'flod': 'area'},
    36: {'tk': 'Kjerne-aktivitet', 'flod': None},
}

xlrd_types = {
    0: 'Empty',
    1: 'Text',
    2: 'Number',
    3: 'Date',
    4: 'Boolean',
    5: 'Error',
    6: 'Blank'
}

performed = {}
failed = {}


def import_workbook(path, server_url):
    workbook = xlrd.open_workbook(path)
    print workbook.sheet_names()
    worksheet = workbook.sheet_by_name('Arbeidsliste')

    header_row_number = 5
    first_data_row = 7

    for r in range(first_data_row, worksheet.nrows):
        print '-------------------------------------'
        print "Importing {} / {}".format(r, worksheet.nrows)
        post_data = {'user': {'role': 'admin'}}  # for now.
        tag = None
        temp = {}
        for c in range(0, worksheet.ncols):

            # get and cast value
            v = worksheet.cell_value(r, c)
            t = xlrd_types.get(int(worksheet.cell_type(r, c)))
            if t == "Text":
                v = unicode(v).strip()
            elif t == "Number":
                v = int(v)
            elif t == 'Date':
                v = xlrd.xldate_as_tuple(v, workbook.datemode)
            elif t == 'Boolean':
                v = 'x' in v
            else:
                v = None

            #map to flod fields
            flod_field_name = import_fields.get(c)['flod']
            if type(flod_field_name) == dict:
                ctag = flod_field_name.get('tag')
                if not ctag == tag:
                    if tag and temp:
                        if not post_data.get(tag):
                            post_data[tag] = temp
                        else:
                            if not type(post_data[tag]) == list:
                                post_data[tag] = [post_data[tag]]
                            post_data[tag].append(temp)
                        tag = None
                        temp = {}
                tag = ctag
                if tag is None:
                    print flod_field_name, v
                value_slot = flod_field_name.get('value_slot')
                temp[value_slot] = v
                #print 'adding:', temp
                if flod_field_name.get('add_data'):
                    for key, data in flod_field_name.get('add_data').iteritems():
                        temp[key] = data
            else:
                if tag and temp:
                    if tag == 'people_k': tag = 'people'  ## avoid consecutive people, _k is kasserer....
                    if not post_data.get(tag):
                        post_data[tag] = temp
                    else:
                        if not type(post_data[tag]) == list:
                            post_data[tag] = [post_data[tag]]
                            post_data[tag].append(temp)
                    tag = None
                    temp = {}
                if flod_field_name == 'registered_tkn': v = v and 'x' in v
                post_data[flod_field_name] = v

        #print json.dumps(post_data)

        persist_organisation(post_data, server_url)

    print 'Done:'
    for k, v in performed.iteritems():
        print k, v
    print "Failed:"
    for k, v in failed.iteritems():
        print k, v


def persist_organisation(data, server_url):
    organisation = data.get('org_number', '-')
    print 'posting:'
    print json.dumps(data)
    headers = {'content-type': 'application/json'}
    r = requests.post(server_url, data=json.dumps(data),
                      cookies=make_superuser_auth_cookie(),
                      headers=headers)

    if r.status_code == 201:
        print 'returned:'
        print r.text
        performed[organisation] = r.json().get('uri')
    else:
        print '!!!!! ***** !!!!!'
        failed[organisation] = "%s:%s" % (r.status_code, json.loads(r.content).get('__error__'))


argp = ArgumentParser()
argp.add_argument('-f', '--file', help='the input excel file to import from', action='store_true', default='data.xlsx')
argp.add_argument('-u', '--url', help='full server url (including path) to server', action='store_true',
                  default='http://0.0.0.0:1338/api/v1/organisations/')

if __name__ == '__main__':
    args = argp.parse_args()
    print 'Importing file ' + args.file + ' to ' + args.url
    import_workbook(args.file, args.url)
