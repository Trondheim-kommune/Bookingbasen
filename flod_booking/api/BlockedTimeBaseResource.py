from flask import current_app
from flask.ext.restful import marshal, request
from flask.ext.bouncer import requires, ensure, DELETE

from RepeatingSlotResource import RepeatingDateResource
from domain.models import BlockedTimeInterval

class BlockedTimeBaseResource(RepeatingDateResource):

    def get(self, resource_id=None, uri_name=None, uri_id=None, id=None):
        if id:
            blocked_time = self.get_object_by_id(id)
            return marshal(blocked_time, self.fields)

        if "resource_uri" in request.args:
            resource_uri = request.args["resource_uri"]
        else:
            resource_uri = "/%s/%s"%(uri_name, uri_id)
        objects = self.get_objects(resource_id=resource_id, resource_uri=resource_uri,
            request=request)

        return marshal(objects.all(), self.fields)

    # This method applies to both BlockedTimeInterval and WeeklyBlockedTime,
    # but authorization is the same for both so we just reuse
    # BlockedTimeInterval auth here
    @requires(DELETE, BlockedTimeInterval)
    def delete(self, **kwargs):
        blocked_time = self.get_object_by_id(kwargs["id"])
        ensure(DELETE, blocked_time)
        current_app.db_session.delete(blocked_time)
        current_app.db_session.commit()
        return "", 204
