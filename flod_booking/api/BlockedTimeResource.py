from flask import current_app, request
from flask.ext.restful import fields, marshal_with, marshal, abort

from domain.blockedtimeutil import BlockedTimeUtil
from BaseResource import BaseResource, ISO8601DateTime

blocked_time_fields = {
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'note' : fields.String
}

class BlockedTimeResource(BaseResource):
    def get(self, resource_id = None, uri_name = None, uri_id = None):
        resource_uri = "/%s/%s"%(uri_name, uri_id)
        resource = self.get_resource_with_id_or_uri(resource_id, resource_uri)

        if "date" in request.args:
            target_date = self.parse_date_from_args(request.args, "date")
            result = BlockedTimeUtil.get_blocked_time_for_date(current_app.db_session,
                resource, target_date)
        elif "start_date" in request.args and "end_date" in request.args:
            start_date, end_date = self.parse_date_range_from_args(request)
            result = BlockedTimeUtil.get_blocked_time_for_date_range(current_app.db_session,
                resource, start_date, end_date)
        else:
            abort(404, __error__ = [ "No date or date interval specified." ])

        return marshal(result, blocked_time_fields)