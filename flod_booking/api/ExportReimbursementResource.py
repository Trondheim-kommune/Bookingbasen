# -*- coding: utf-8 -*-
from collections import OrderedDict

from isodate import parse_date
from flask.ext.bouncer import requires, GET
from api.BaseResource import BaseResource, get_resource_from_web
from ResourceStatisticResource import get_resource_statistic
from flod_common.outputs.output_csv import output_csv


def get_statistics(start_date, end_date):
    result = []

    resource_data = get_resource_from_web('/facilities/')

    for facility in resource_data:
        facility_id = facility.get('id')
        facility_statistics_response = get_resource_statistic(facility_id, start_date, end_date)

        result.append({
            # 'id': facility_id,
            'unit_type': facility.get('unit_type').get('name'),
            'unit_number': facility.get('unit_number'),
            'unit_name': facility.get('unit_name'),
            'name': facility.get('name'),
            # 'facility_type': facility.get('facility_type').get('name'),
            'hours': sum(float(item['hours']) for item in facility_statistics_response)})

    return result


class ExportReimbursementResource(BaseResource):
    @requires(GET, 'ExportReimbursement')
    def get(self, start, end):
        start_date = parse_date(start)
        end_date = parse_date(end)

        statistics = get_statistics(start_date, end_date)

        fieldname_mapping = OrderedDict()
        fieldname_mapping['unit_type'] = 'Type enhet'
        fieldname_mapping['unit_number'] = 'Enhetskode'
        fieldname_mapping['unit_name'] = 'Navn på enhet'
        fieldname_mapping['name'] = 'Navn på lokalet'
        fieldname_mapping['hours'] = 'Antall timer utlån fra %s til %s' % (start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))

        return output_csv(statistics, 200, fieldname_mapping=fieldname_mapping)
