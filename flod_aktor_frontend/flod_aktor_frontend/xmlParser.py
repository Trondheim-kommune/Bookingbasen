#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

import re
from flask import current_app


def get_organisations_from_nif_idrettsraad_xml(xml_file_path):
    """
        Parse given XML with organisations with organisation name, number and member counts.
        Returns a list of dictionaries to the same format
        as accepted by flod_organisation.
        @param xml_file_path	Provide the file path to the XML file to be parsed
        @return list		Organisation dictionaries
    """
    try:
        namespaces = {'xmlns': u'Orgoversikt_x0020_idrettsråd'}

        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        organisation_elements = root.findall("xmlns:table1/xmlns:Detail_Collection/xmlns:Detail",
                                             namespaces=namespaces)

        organisations = []
        for child in organisation_elements:
            organisation = {}

            try:
                organisation['name'] = child.attrib['DescribingName']

                try:
                    organisation['org_number'] = int(child.attrib['organisationnumber'])
                except ValueError:
                    # If normal parsing fails, we try to be clever
                    current_app.logger.warn("Parsefeil for " + str(child.attrib['organisationnumber']) + ". Forsøker igjen.")
                    organisation['org_number'] = parse_number_with_incorrect_format(child.attrib['organisationnumber'])
                    current_app.logger.warn("Organisasjonsnummeret " + str(child.attrib['organisationnumber']) + " ble parset til " + str(organisation['org_number']))

                organisation['num_members'] = int(child.attrib['AntMemb'])
                organisation['num_members_b20'] = int(child.attrib['AntMemb20'])
                organisations.append(organisation)

            except Exception as e:
                current_app.logger.error("Parsing av medlemsdata feilet for: " + str(ET.dump(child)) + " Feil: " + str(e))

        return organisations

    except Exception as e:
        current_app.logger.error("Parsing av medlemsdata feilet: " + str(e))
        return []


def parse_number_with_incorrect_format(my_string):
    '''
    If we have a string that should be parsed as a number, it may have been written with illegal string characters.
    We attempt to remove non-digit characters to form a number of the digit characters.
    This may very well throw an exception if it turns out that it is not parseable to an integer
    E.g. NO987342432MVA, 987 342 432 will be parsed to 987342432
    '''

    number_matches = re.findall(r"(\d+)\D*", my_string)
    number_string = ''.join(number_matches)
    return int(number_string)
