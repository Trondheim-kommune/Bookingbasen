from flask.ext import restful

from ResourceResource import ResourceResource
from SlotsForWeekResource import SlotsForWeekResource
from WeeklyBlockedTimeResource import WeeklyBlockedTimeResource
from BlockedTimeIntervalResource import BlockedTimeIntervalResource
from BlockedTimeResource import BlockedTimeResource
from ApplicationResource import ApplicationResource
from SingleApplicationResource import SingleApplicationResource
from StrotimeApplicationResource import StrotimeApplicationResource
from RepeatingApplicationResource import RepeatingApplicationResource
from WeeklyRepeatingSlotsForResource import WeeklyRepeatingSlotsForResource
from OrganisationInternalNotesResource import OrganisationInternalNotesResource
from StrotimeApplicationNotificationsResource import StrotimeApplicationNotificationsResource
from RepeatingSlotReleaseTimeResource import RepeatingSlotReleaseTimeResource
from RammetidResource import RammetidResource
from WeeklyRammetidSlotsResource import WeeklyRammetidSlotsResource
from RammetidToApplicationResource import RammetidToApplicationResource
from OrganisationStatisticResource import OrganisationStatisticResource
from ResourceStatisticResource import ResourceStatisticResource
from ArrangementNotificationResource import ArrangementNotificationResource
from ArrangementConflictsResource import ArrangementConflictsResource
from OrganisationResource import OrganisationResource
from SettingsResource import SettingsResource
from ExportReimbursementResource import ExportReimbursementResource
from ExportPeriodOverviewResource import ExportOverviewResource as ExpOverviewResource


def create_api(app, api_version):
    api = restful.Api(app)
    api.add_resource(ResourceResource,
                     '/api/%s/resources/<int:resource_id>' % api_version,
                     '/api/%s/resources/<path:resource_uri>' % api_version,
                     '/api/%s/resources/' % api_version)

    api.add_resource(WeeklyBlockedTimeResource,
                     '/api/%s/weeklyblockedtimes/' % api_version,
                     '/api/%s/weeklyblockedtimes/<int:id>' % api_version,
                     '/api/%s/resources/<int:resource_id>/weeklyblockedtimes/' % api_version,
                     '/api/%s/resources/<string:uri_name>/<int:uri_id>/weeklyblockedtimes/' % api_version,
                     '/api/%s/resources/<int:resource_id>/weeklyblockedtimes/<int:id>' % api_version)

    api.add_resource(BlockedTimeIntervalResource,
                     '/api/%s/blockedtimeintervals/' % api_version,
                     '/api/%s/blockedtimeintervals/<int:id>' % api_version,

                     '/api/%s/resources/<int:resource_id>/blockedtimeintervals/' % api_version,
                     '/api/%s/resources/<string:uri_name>/<int:uri_id>/blockedtimeintervals/' % api_version,
                     '/api/%s/resources/<int:resource_id>/blockedtimeintervals/<int:id>' % api_version)

    api.add_resource(BlockedTimeResource,
                     '/api/%s/resources/<int:resource_id>/blockedtimes/' % api_version,
                     '/api/%s/resources/<string:uri_name>/<int:uri_id>/blockedtimes/' % api_version)

    api.add_resource(ApplicationResource,
                     '/api/%s/applications/<int:application_id>' % api_version,
                     '/api/%s/applications/' % api_version)

    api.add_resource(
        SlotsForWeekResource,
        '/api/%s/slots/' % api_version
    )

    api.add_resource(
        WeeklyRepeatingSlotsForResource,
        '/api/%s/slots/repeating/' % api_version
    )

    api.add_resource(
        SingleApplicationResource,
        '/api/%s/applications/single/' % api_version
    )

    api.add_resource(
        RepeatingApplicationResource,
        '/api/%s/applications/repeating/' % api_version
    )

    api.add_resource(
        StrotimeApplicationResource,
        '/api/%s/applications/strotime/' % api_version,
        '/api/%s/applications/strotime/<int:application_id>' % api_version
    )

    api.add_resource(
        StrotimeApplicationNotificationsResource,
        '/api/%s/applications/strotime/notifications' % api_version
    )

    api.add_resource(OrganisationInternalNotesResource,
                     '/api/%s/organisations/<int:organisation_id>/notes/<int:note_id>' % api_version,
                     '/api/%s/organisations/<int:organisation_id>/notes/' % api_version)

    api.add_resource(RepeatingSlotReleaseTimeResource,
                     '/api/%s/repeating_slots/<int:slot_id>/release_time' % api_version)

    api.add_resource(RammetidResource,
                     '/api/%s/rammetid/<int:rammetid_id>' % api_version,
                     '/api/%s/rammetid/' % api_version)

    api.add_resource(
        WeeklyRammetidSlotsResource,
        '/api/%s/weeklyrammetidslots/' % api_version
    )

    api.add_resource(
        RammetidToApplicationResource,
        '/api/%s/rammetidtoapplication/' % api_version
    )

    api.add_resource(OrganisationStatisticResource,
                     '/api/%s/organisations/<int:organisation_id>/statistics' % api_version
                     )

    api.add_resource(OrganisationResource,
                     '/api/%s/organisations/<int:organisation_id>' % api_version
                     )

    api.add_resource(ResourceStatisticResource,
                     '/api/%s/facilities/<int:facility_id>/statistics' % api_version
                     )

    api.add_resource(ExportReimbursementResource,
                     '/api/%s/organisations/export/reimbursement/<string:start>/<string:end>/' % api_version
                     )

    api.add_resource(ExpOverviewResource,
                     '/api/%s/organisations/export/period_overview/<string:facilities_ids>/<string:start>/<string:end>/' % api_version
                     )

    api.add_resource(ArrangementNotificationResource,
                     '/api/%s/arrangement_notification/<int:application_id>' % api_version
                     )

    api.add_resource(ArrangementConflictsResource,
                     '/api/%s/arrangement_conflicts/<int:application_id>' % api_version
                     )

    api.add_resource(SettingsResource,
                     '/api/%s/adm_leieform/' % api_version
                     )

    return api
