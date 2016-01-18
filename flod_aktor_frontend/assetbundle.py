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

css = Bundle(
    'css/bootstrap/css/bootstrap.min.css',
    'css/bootstrap/css/bootstrap-responsive.min.css',
    Bundle('css/datepicker.css',
           'css/flod.css',
           filters=css_filters),
    filters=['cssrewrite'],
    output='gen/css/bootstrap.css'
)

organisationpage_js = Bundle(
    'js/lib/serialize_object.js',
    'js/src/notifier.js',
    'js/src/activity_code_models.js',
    'js/src/modal.js',
    'js/src/organisation-activity.js',
    'js/src/organisation-model.js',
    'js/src/organisation-form.js',
    filters=js_filters,
    output='gen/js/organisation.js'
)

organisation_email = Bundle(
    'js/src/modal.js',
    'js/src/email.js',
    filters=js_filters,
    output='gen/js/email.js'
)

organisation_export = Bundle(
    'js/src/export_report.js',
    filters=js_filters,
    output='gen/js/export_report.js'
)

registerorganisation_js = Bundle(
    'js/src/modal.js',
    'js/src/register_org.js',
    filters=js_filters,
    output='gen/js/register_organisation.js'
)

profilepage_js = Bundle(
    'js/src/notifier.js',
    'js/lib/serialize_object.js',
    'js/src/profile_page.js',
    filters=js_filters,
    output='gen/js/profile.js'

)

organisation_members_js = Bundle(
    'js/src/modal.js',
    'js/src/notifier.js',
    'js/src/organisation-members.js',
    filters=js_filters,
    output='gen/js/profile.js'
)

umbrella_organisation_js = Bundle(

    Bundle('js/src/notifier.js',
           'js/src/organisation-model.js',
           'js/src/Message.js',
           'js/src/FormValidationMixin.js',
           'js/src/UmbrellaOrganisation.js',
           'js/src/umbrella_organisation_page/MemberOrganisationsView.js',
           'js/src/umbrella_organisation_page/ResponsiblePersonsView.js',
           'js/src/umbrella_organisation_page/InformationView.js',
           'js/src/umbrella_organisation_page/Router.js',
           'js/src/umbrella_organisation_page/MainPage.js',
           'js/src/umbrella_organisation_page/UmbrellaOrganisationHeaderView.js',
           filters=js_filters),
    output='gen/js/umbrella_organisation.js'
)

organisation_internal_notes_js = Bundle(
    'js/lib/moment.min.js',
    Bundle(
        'js/lib/moment-nb.js',
        'js/src/organisation-model.js',
        'js/src/organisation_internal_notes.js',
        filters=js_filters,
        output='gen/js/organisation_internal_notes.js'
    )
)
