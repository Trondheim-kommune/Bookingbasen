# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import logging

from suds.client import Client


logging.getLogger("suds").setLevel(logging.ERROR)

class OrgNrNotFoundException(Exception):
    def __init__(self, message):
        self.message = message

def __str__(self):
    return "Message: %s  Status code: %d" % (self.message, self.status_code)

class BrRegClient(object):
    def __init__(self, url, user_id, password):
        try:
            self.brreg_ws_client = BrRegWSClient(url, user_id, password)
        except Exception:
            raise Exception('Could not create Brreg WS client.')

    def get_brreg_response_code(self, response):
        if response and response.get('response_status'):
            return response.get('response_status').get('code')
        else:
            return None

    def get_brreg_enhet_basis_data_simple(self, org_number):
        if self.brreg_ws_client is None:
            return {}

        result = {}
        brreg_basis_response = self.brreg_ws_client.get_brreg_org_data_basic(org_number)
        try:
            brreg_basis_handler = BrRegWSBasisDataResponseHandler(brreg_basis_response)
        except ValueError:
            return {}

        result['response_status'] = brreg_basis_handler.get_response_status()
        if int(result['response_status']['code']) > 0:
            raise OrgNrNotFoundException(result['response_status']['message'])

        result.update(brreg_basis_handler.get_response_dict())
        return result

    def get_brreg_enhet_role_data(self, org_number):
        if self.brreg_ws_client is None:
            return {}
        brreg_role_response = self.brreg_ws_client.get_brreg_org_data_roles(org_number)
        try:
            brreg_role_handler = BrRegWSRoleInfoResponseHandler(brreg_role_response)
            return brreg_role_handler.get_role_persons()
        except ValueError:
            return {}

    def get_brreg_enhet_contact_data(self, org_number):
        if self.brreg_ws_client is None:
            return {}

        brreg_contact_response = self.brreg_ws_client.get_brreg_org_data_contact_info(org_number)
        try:
            brreg_contact_handler = BrRegWSContactDataResponseHandler(brreg_contact_response)
            return brreg_contact_handler.get_response_dict()
        except ValueError:
            return {}

    def get_brreg_enhet_basis_data_full(self, org_number):
        if self.brreg_ws_client is None:
            return {}

        result = self.get_brreg_enhet_basis_data_simple(org_number)

        contact_info = self.get_brreg_enhet_contact_data(org_number)
        for key in contact_info:
            result[key] = contact_info.get(key, None)

        brreg_org_persons = result.get('persons', [])
        role_people = self.get_brreg_enhet_role_data(org_number)
        brreg_org_persons.extend(role_people.get('persons', []))

        final_persons = {}
        for person in brreg_org_persons:
            nin = person.get('national_identity_number')
            existing_person = final_persons.get(nin, None)
            if not existing_person:
                if 'org_roles' not in person.keys():
                    person['org_roles'] = []
                final_persons[nin] = person
            else:
                role = person.get('org_roles')
                if role not in existing_person.get('org_roles'):
                    if role:
                        existing_person['org_roles'].extend(role)

        result['persons'] = final_persons.values()

        frivillig_response = self.get_brreg_frivillig_response(org_number)
        result['frivillighet_code'] = frivillig_response.get('code', None)
        result['account_number'] = frivillig_response.get('account_number', None)
        result['brreg_activity_code'] = frivillig_response.get('brreg_activity_code', [])
        return result

    def get_brreg_enhet_name_search(self, name):
        if self.brreg_ws_client is None:
            return []
        ws_response = self.brreg_ws_client.search_by_org_name(name)
        try:
            brreg_name_search_handler = BrRegWSNameSearchResponseHandler(ws_response)
            return brreg_name_search_handler.get_names()
        except ValueError:
            return []

    def get_brreg_frivillig_response(self, org_number):
        if self.brreg_ws_client is None:
            return {}
        ws_response = self.brreg_ws_client.get_brreg_frivillig_response(org_number)
        try:
            brreg_frivillig_handler = BrRegWSFrivillighetResponseHandler(ws_response)
            return brreg_frivillig_handler.get_fr_data()
        except ValueError:
            return []


class BrRegWSClient(object):
    ER_WSDL = 'ErFr?WSDL'
    FV_WSDL = 'Frivillighet?WSDL'

    NAME_QUERY_STRING = """<?xml version='1.0' encoding='ISO-8859-1'?>
<BrAixXmlRequest RequestName="BrErfrSok">
        <BrErfrSok>
                <BrSokeStreng>%(query_string)s</BrSokeStreng>
                <MaxTreffReturneres>1000</MaxTreffReturneres>
                <ReturnerIngenHvisMax>true</ReturnerIngenHvisMax>
                <RequestingIPAddr>010.001.052.011</RequestingIPAddr>
                <RequestingTjeneste>SOAP</RequestingTjeneste>
                <Kommunenr>1601</Kommunenr>
                <MedUnderenheter>false</MedUnderenheter>
        </BrErfrSok>
</BrAixXmlRequest>"""

    def __init__(self, url, user_id, password):
        if not url:
            raise Exception('Could not create Brreg WS Client: URL empty')
        if not user_id:
            raise Exception('Could not create Brreg WS Client: USER empty')
        if not password:
            raise Exception('Could not create Brreg WS Client: PASSWORD empty')

        enhet_url = url + self.ER_WSDL
        frivillig_url = url + self.FV_WSDL
        try:
            self.er_client = Client(enhet_url)
            self.fv_client = Client(frivillig_url)
        except Exception:
            raise Exception('SUDS client initialisation failed.')

        self.brreg_user_id = user_id
        self.brreg_password = password

    def get_brreg_org_data_basic(self, org_number):
        return self.er_client.service.hentBasisdata(self.brreg_user_id, self.brreg_password, org_number)

    def get_brreg_org_data_roles(self, org_number):
        return self.er_client.service.hentRoller(self.brreg_user_id, self.brreg_password, org_number)

    def get_brreg_org_data_contact_info(self, org_number):
        return self.er_client.service.hentKontaktdata(self.brreg_user_id, self.brreg_password, org_number)

    def search_by_org_name(self, org_name=''):
        name_search_query = self.NAME_QUERY_STRING % {'query_string': org_name}
        return self.er_client.service.sokEnhet(self.brreg_user_id, self.brreg_password, name_search_query)

    def get_brreg_frivillig_response(self, org_number):
        return self.fv_client.service.hentFrivillighet(self.brreg_user_id, self.brreg_password, org_number)


class BrRegWSResponseHandler(object):
    address_mapping = {'address_line': 'adresse1',
                       'postal_code': 'postnr',
                       'postal_city': 'poststed',
                       'municipality_code': 'kommunenummer',
                       'municipality_name': 'kommune',
                       'country_code': 'landkode',
                       'country_name': 'land'}

    person_mapping = {'national_identity_number': './fodselsnr',
                      'first_name': './fornavn',
                      'last_name': './slektsnavn',
                      'address_line': './adresse1',
                      'postal_code': './postnr',
                      'postal_city': './poststed',
                      'country': './land'}

    def __init__(self, ws_response):
        if ws_response is None:
            raise ValueError('Response is None')
        try:
            self.ws_response_etree = ET.fromstring(ws_response)
        except Exception:
            raise ValueError('Invalid response')

    def find_elements_for_path(self, xpath, startnode=None):
        if not xpath:
            return []
        if startnode is None:
            startnode = self.ws_response_etree
        #print startnode, xpath
        return startnode.findall(xpath)

    def get_text_value_for_xpath(self, xpath, concatstring=' ', startnode=None):
        if not xpath:
            return ''
        if startnode is None:
            startnode = self.ws_response_etree
        matches = startnode.findall(xpath)
        values = [match.text.strip() for match in matches if match.text]
        return concatstring.join(values)

    def get_tag_value_dict_for_xpath(self, xpath, startnode=None):
        if not xpath:
            return {}
        if startnode is None:
            startnode = self.ws_response_etree

        matches = startnode.findall(xpath)
        org_units = [dict([(m.tag, m.text) for m in match if m.tag and m.text]) for match in matches]
        return org_units

    def extract_data_for_path_with_mapping(self, path, element_mappings, use_list=True, startnode=None):
        matching_startpath = self.find_elements_for_path(path, startnode)
        element_result_list = []
        for element in matching_startpath:
            element_result = {}
            for mapping in element_mappings:
                xpath = element_mappings.get(mapping)
                res = None
                res = self.get_text_value_for_xpath(xpath, ' ', element)
                element_result[mapping] = res
            element_result_list.append(element_result)
        if use_list:
            return element_result_list
        else:
            if element_result_list:
                return element_result_list[0]
            else:
                return None

    def extract_result(self, paths):
        result = {}
        for (k, v) in paths.items():
            if type(v) == str:
                result[k] = self.get_text_value_for_xpath(v)
            elif type(v) == list:
                result[k] = []
                for e in v:
                    if type(e) == dict:
                        extracted = self.extract_data_for_path_with_mapping(e.get('path'), e.get('mapping'))
                        result[k].extend([ex for ex in extracted if ex not in result[k]])
                    else:
                        result[k] = [x.text.strip() for x in self.find_elements_for_path(e)]

            elif type(v) == dict:
                extracted = self.extract_data_for_path_with_mapping(v.get('path'), v.get('mapping'),
                                                                    v.get('use_list', True))
                if extracted:
                    result[k] = extracted
        return result

    def get_response_dict(self):
        result = self.extract_result(self.xpaths)
        return result

    def get_response_status(self):
        status_code = self.get_text_value_for_xpath('./responseHeader/hovedStatus')
        status_message = self.get_text_value_for_xpath('./responseHeader/underStatus/underStatusMelding', ', ')
        return {'code': status_code, 'message': status_message}


class BrRegWSBasisDataResponseHandler(BrRegWSResponseHandler):
    def __init__(self, ws_response):
        BrRegWSResponseHandler.__init__(self, ws_response)
        self.xpaths = {
            'name': './/navn/',
            'org_number': './/organisasjonsnummer',
            'org_form': './/orgform',
            'postal_address': {'path': './/postAdresse',
                               'mapping': self.address_mapping,
                               'use_list': False},
            'business_address': {'path': './/forretningsAdresse',
                                 'mapping': self.address_mapping,
                                 'use_list': False},
            'persons': {'path': './/kontaktperson//person',
                        'mapping': self.person_mapping}
        }

    def get_org_number(self):
        return self.get_text_value_for_xpath(self.xpaths['org_number'])

    def get_name(self):
        return self.get_text_value_for_xpath(self.xpaths['name'])

    def get_postal_address(self):
        address_result = self.extract_result({'postal_address': self.xpaths['postal_address']})
        return address_result.get('postal_address')


class BrRegWSContactDataResponseHandler(BrRegWSResponseHandler):
    def __init__(self, ws_response):
        BrRegWSResponseHandler.__init__(self, ws_response)
        self.xpaths = {
            'phone_number': './/telefonnummer',
            'telefax_number': './/telefaksnummer',
            'email_address': './/epostadresse',
            'url': './/hjemmesideadresse'
        }


class BrRegWSRoleInfoResponseHandler(BrRegWSResponseHandler):
    def __init__(self, ws_response):
        BrRegWSResponseHandler.__init__(self, ws_response)
        self.xpaths = {
            'persons': [{'path': 'person', 'mapping': self.person_mapping}]
        }

    def get_role_persons(self):
        role_paths = ['.//kontaktperson//rolle', './/styre//rolle']
        people = []
        for p in role_paths:
            for e in self.find_elements_for_path(p):
                role_desc = e.get('beskrivelse')
                for path in self.xpaths:
                    found_persons = self.extract_data_for_path_with_mapping('person', self.person_mapping, True, e)
                    for person in found_persons:
                        if role_desc:
                            person['org_roles'] = [role_desc]
                        else:
                            person['org_roles'] = []
                    people.extend(found_persons)

        return {'persons': people}


class BrRegWSNameSearchResponseHandler(BrRegWSResponseHandler):
    xpaths = {
        'org_unit': './/BrErfrTrefflisteElement',
    }

    def __init__(self, ws_response):
        if not ws_response:
            raise ValueError('Invalid response')
        BrRegWSResponseHandler.__init__(self, ws_response.encode('utf8'))

    def get_names(self):
        response_status = self.get_response_status()
        org_unit_list = self.get_tag_value_dict_for_xpath(self.xpaths['org_unit'])
        return {'response_status': response_status, 'result': org_unit_list}


class BrRegWSFrivillighetResponseHandler(BrRegWSResponseHandler):
    xpaths = {
        'brreg_activity_code': ['.//kategori/kode'],
        'account_number': './/kontonummer'
    }

    def __init__(self, ws_response):
        if not ws_response:
            raise ValueError('Invalid response')
        BrRegWSResponseHandler.__init__(self, ws_response.encode('utf8'))

    def get_fr_data(self):
        result = self.get_response_dict()
        result['response_status'] = self.get_response_status()
        return result
