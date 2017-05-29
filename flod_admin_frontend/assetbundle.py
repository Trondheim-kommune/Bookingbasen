# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle

js_filters = ['jsmin']
css_filters = ['cssmin']

base_js_libs = Bundle(
    'js/lib/jquery-1.9.1.min.js',
    'js/lib/underscore-min.js',
    'js/lib/backbone-min.js',
    'js/lib/bootstrap.min.js',
    Bundle('js/lib/jquery.iframe-transport.js', filters=js_filters),
    output='gen/js/libs.js'
)

calendar_css = Bundle(
    'css/jquery/jquery-ui-1.10.3.custom.min.css',
    Bundle('css/flod_calendar.css', filters=css_filters),
    filters=['cssrewrite'],
    output='gen/css/calendar.css'
)

calendar_js = Bundle(
    'js/lib/moment.min.js',
    Bundle('js/lib/moment-range.js', filters=js_filters),
    'js/lib/FlodCalendar.min.js',
    output='gen/js/calendar.js'
)

facility_js = Bundle(
    Bundle('js/lib/bootstrap-timepicker.js',
           'js/src/notifier.js',
           'js/src/facility_page/FacilityRouter.js',
           'js/src/facility_page/FacilityImage.js',
           'js/src/facility_page/FacilityDocument.js',
           'js/src/Facility.js',
           'js/src/facility_page/WeeklyBlockedTimeModel.js',
           'js/src/facility_page/WeeklyBlockedTimeView.js',
           'js/src/facility_page/BlockedTimeIntervalModel.js',
           'js/src/facility_page/BlockedTimeIntervalView.js',
           'js/src/Resource.js',
           'js/src/RentalTypesView.js',
           'js/src/UserView.js',
           'js/src/facility_page/AddCredentialToUserView.js',
           'js/src/quicksearch.js',
           'js/src/facility_page/FacilityGeocoding.js',
           'js/lib/bootstrap-datepicker.js',
           'js/src/Message.js',
           'js/src/FormValidationMixin.js',
           'js/src/facility_page/FacilityHeaderView.js',
           'js/src/facility_page/FacilityInternalNotes.js',
           'js/src/facility_page/FacilityAdministratorView.js',
           'js/src/facility_page/FacilityBlockedTimeView.js',
           'js/src/facility_page/FacilityDocumentsMainView.js',
           'js/src/facility_page/FacilityImageMainView.js',
           'js/src/collision_detector.js',
           'js/src/CalendarCommon.js',
           'js/src/calendar_extensions.js',
           'js/src/facility_page/FacilityCalendarView.js',
           'js/src/facility_page/FacilityMainPage.js',
           filters=js_filters),
    output='gen/js/facility.js'
)

bootstrap_css = Bundle(
    'css/bootstrap/css/bootstrap.min.css',
    'css/bootstrap/css/bootstrap-responsive.min.css',
    Bundle('css/datepicker.css',
           'css/bootstrap-timepicker.css',
           'css/style.css',
           'css/flod_admin.css',
           filters=css_filters),
    filters=['cssrewrite'],
    output='gen/css/bootstrap.css'
)

applications_js = Bundle(
    'js/lib/moment.min.js',
    Bundle('js/lib/moment-nb.js',
           'js/lib/bootstrap-datepicker.js',
           'js/src/Resource.js',
           'js/src/Facility.js',
           'js/src/ApplicationCommon.js',
           'js/src/SimpleApplication.js',
           'js/src/ApplicationListView.js',
           filters=js_filters),
    output='gen/js/applications.js'
)

application_js = Bundle(
    'js/lib/moment-nb.js',
    'js/lib/bootstrap-datepicker.js',
    'js/src/modal.js',
    'js/src/notifier.js',
    'js/src/Resource.js',
    'js/src/facility_page/FacilityImage.js',
    'js/src/facility_page/FacilityDocument.js',
    'js/src/Facility.js',
    'js/src/collision_detector.js',
    'js/src/ApplicationCommon.js',
    'js/src/SimpleApplication.js',
    'js/src/ApplicationModel.js',
    'js/src/CalendarCommon.js',
    'js/src/ApplicationCalendar.js',
    'js/src/LegendView.js',
    'js/src/ApplicationView.js',
    'js/src/ApplicationListView.js',
    'js/lib/serialize_object.js',
    filters=js_filters,
    output='gen/js/application.js'
)

rammetid_js = Bundle(
    'js/src/notifier.js',
    'js/src/collision_detector.js',
    'js/lib/bootstrap-timepicker.js',
    'js/lib/bootstrap-datepicker.js',
    'js/src/CalendarCommon.js',
    'js/src/RammetidCalendar.js',
    'js/src/RammetidModel.js',
    'js/src/RammetidView.js',
    filters=js_filters,
    output='gen/js/Rammetid.js'
)

single_rammetid_js = Bundle(
    'js/lib/moment.min.js',
    'js/lib/moment-nb.js',
    'js/src/rammetid/Single.js',
    'js/src/RammetidModel.js',
    filters=js_filters,
    output='gen/js/SingleRammetid.js'
)

statistics_js = Bundle(
    'js/lib/bootstrap-datepicker.js',
    filters=js_filters,
    output='gen/js/statistics_js'
)

reimbursement_export_js = Bundle(
    'js/lib/moment.min.js',
    'js/src/ExportReimbursement.js',
    filters=js_filters,
    output='gen/js/reimbursement_export_js'
)

overview_export_js = Bundle(
    'js/lib/moment.min.js',
    'js/src/ExportOverview.js',
    filters=js_filters,
    output='gen/js/overview_export_js'
)

adm_leieform_js = Bundle(
    'js/lib/moment.min.js',
    Bundle(
        'js/lib/moment-nb.js',
        'js/lib/bootstrap-datepicker.js',
        'js/src/notifier.js',
        'js/src/AdministrerLeieform.js',
        filters=js_filters),
    output='gen/js/adm_leieform_js'
)

booking_for_actor_js = Bundle(
    'js/lib/moment-nb.js',
    'js/lib/bootstrap-datepicker.js',
    'js/src/notifier.js',
    'js/src/modal.js',
    'js/src/BookingApplication.js',
    'js/src/collision_detector.js',
    'js/src/CalendarCommon.js',
    'js/src/calendar_extensions.js',
    'js/src/BookingForActorCalendar.js',
    'js/src/LegendView.js',
    'js/src/BookingForActor.js',
    'js/lib/serialize_object.js',
    filters=js_filters,
    output='gen/js/booking_for_actor_js'
)

leaflet_js = Bundle(
    'js/lib/leaflet/leaflet.js',
    'js/lib/SpatialBB.min.js',
    filters=js_filters,
    output='gen/js/leaflet.js'
)

leaflet_css = Bundle(
    'js/lib/leaflet/leaflet.css',
    filters=css_filters + ['cssrewrite'],
    output='gen/css/leaflet.css'
)

organisation_email = Bundle(
    'js/src/modal.js',
    'js/src/email.js',
    filters=js_filters,
    output='gen/js/email.js'
)

release_time_repeating_application_js = Bundle(
    'js/lib/moment.min.js',
    Bundle(
        'js/src/notifier.js',
        'js/lib/moment-nb.js',
        'js/lib/moment-range.js',
        'js/lib/bootstrap-datepicker.js',
        'js/src/ApplicationCommon.js',
        'js/src/time-picker.js',
        'js/src/release_time_repeating_application.js',
        filters=js_filters),
    output='gen/js/release_time_repeating_application.js')
