# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle

js_filters = ['jsmin']
css_filters = ['cssmin']

js_libs = Bundle(
    'js/lib/jquery-1.9.1.min.js',
    'js/lib/underscore-min.js',
    'js/lib/backbone-min.js',
    'js/lib/bootstrap.min.js',
    output='gen/js/libs.js'
)

common_js = Bundle(
    'js/src/quicksearch.js',
    filters=js_filters,
    output='gen/js/common.js'
)

css = Bundle(
    'css/bootstrap/css/bootstrap.min.css',
    'css/bootstrap/css/bootstrap-responsive.min.css',
    Bundle('css/datepicker.css',
           'css/flod.css',
           filters=css_filters),
    filters=['cssrewrite'],
    output='gen/css/bootstrap.css'
)

calendar_css = Bundle(
    'css/jquery/jquery-ui-1.10.3.custom.min.css',
    Bundle('css/flod_calendar.css', filters=css_filters),
    filters=['cssrewrite'],
    output='gen/css/calendar.css'
)

leaflet_css = Bundle(
    'js/lib/leaflet/leaflet.css',
    filters=css_filters + ['cssrewrite'],
    output='gen/css/leaflet.css'
)

leaflet_js = Bundle(
    'js/lib/leaflet/leaflet.js',
    'js/lib/SpatialBB.min.js',
    output='gen/js/leaflet.js'
)

facilitypage_js = Bundle(
    'js/src/Documents.js',
    'js/src/Image.js',
    'js/src/image_viewer.js',
    'js/src/map.js',
    'js/src/rammetid-model.js',
    'js/src/collision_detector.js',
    'js/src/CalendarCommon.js',
    'js/src/calendar_extensions.js',
    'js/src/facility.js',
    filters=js_filters,
    output='gen/js/facility.js'
)

searchpage_js = Bundle(
    'js/lib/moment.min.js',
    Bundle('js/lib/moment-nb.js',
           'js/lib/bootstrap-datepicker.js',
           'js/src/Image.js',
           'js/src/map.js',
           'js/src/form_elements.js',
           'js/src/search.js',
           filters=js_filters),
    output='gen/js/search.js'
)

calendar_js = Bundle(
    'js/lib/moment.min.js',
    Bundle('js/lib/moment-nb.js',
           'js/lib/moment-range.js',
           filters=js_filters),
    'js/lib/FlodCalendar.min.js',
    output='gen/js/calendar.js'
)

strotime_js = Bundle(
    'js/src/application.js',
    'js/src/modal.js',
    'js/src/notifier.js',
    'js/src/facility_model.js',
    'js/src/facility_type_selector.js',
    'js/src/time-picker.js',
    'js/src/collision_detector.js',
    'js/src/CalendarCommon.js',
    'js/src/strotime_booking.js',
    filters=js_filters,
    output='gen/js/strotime.js'
)

bookingpage_js = Bundle(
    'js/lib/bootstrap-datepicker.js',
    'js/src/collision_detector.js',
    'js/src/calendar_extensions.js',
    'js/lib/serialize_object.js',
    'js/src/notifier.js',
    'js/src/modal.js',
    'js/src/facility_model.js',
    'js/src/facility_type_selector.js',
    'js/src/application.js',
    'js/src/CalendarCommon.js',
    'js/src/booking.js',
    filters=js_filters,
    output='gen/js/booking.js'
)

applicationpage_js = Bundle(
    'js/lib/moment.min.js',
    Bundle('js/lib/moment-nb.js',
           'js/src/facility_model.js',
           'js/src/application_common.js',
           'js/src/application_list.js',
           'js/src/notifier.js',
           'js/src/modal.js',
           filters=js_filters),
    output='gen/js/applicationpage.js'
)

profilepage_js = Bundle(
    'js/src/notifier.js',
    'js/lib/serialize_object.js',
    'js/src/profile_page.js',
    filters=js_filters,
    output='gen/js/profile.js'

)

release_time_repeating_application_js = Bundle(
    'js/lib/moment.min.js',
    Bundle(
        'js/src/notifier.js',
        'js/lib/moment-nb.js',
        'js/lib/moment-nb.js',
        'js/lib/moment-range.js',
        'js/lib/bootstrap-datepicker.js',
        'js/src/application_common.js',
        'js/src/time-picker.js',
        'js/src/release_time_repeating_application.js',
        filters=js_filters),
    output='gen/js/release_time_repeating_application.js')

rammetid_js = Bundle(
    'js/src/notifier.js',
    'js/src/CalendarCommon.js',
    'js/src/calendar_extensions.js',
    'js/src/rammetid-model.js',
    'js/src/rammetid-calendar.js',
    'js/src/rammetid-view.js',
    filters=js_filters,
    output='gen/js/my_umbrella_organisation.js'
)

forsiden_js = Bundle(
    'js/lib/moment.min.js',
    Bundle(
        'js/lib/moment-nb.js',
        'js/lib/moment.min.js',
        'js/src/forside_bokser.js',
        'js/src/settings_model.js',
        filters=js_filters),
    output='gen/js/forsiden_js'
)
