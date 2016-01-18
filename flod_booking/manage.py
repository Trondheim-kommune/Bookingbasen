# -*- coding: utf-8 -*-
import os

from flask.ext.script import Manager
from isodate import parse_datetime

from app import app
from domain import models
from database import init_db


manager = Manager(app)
import json


def no_map(model, mapped_models):
    return model


def map_slot(model, mapped_models):
    resource = model.get("resource", None)
    if resource:
        model["resource"] = mapped_models["resource_models"][resource]

    person = model.get("person", None)
    if person:
        model["person"] = mapped_models["person_models"][person]

    organisation = model.get("organisation", None)
    if organisation:
        model["organisation"] = mapped_models["organisation_models"][organisation]

    model["start_time"] = parse_datetime(model["start_time"])
    model["end_time"] = parse_datetime(model["end_time"])
    return model


def map_block(model, mapped_models):
    resource = model.get("resource", None)
    if resource:
        model["resource"] = mapped_models["resource_models"][resource]

    model["start_time"] = parse_datetime(model["start_time"])
    model["end_time"] = parse_datetime(model["end_time"])
    return model


model_mapping = {
    "resource": {"model": models.Resource, "map_model": no_map},
    "person": {"model": models.Person, "map_model": no_map},
    "organisation": {"model": models.Organisation, "map_model": no_map},
    "slot": {"model": models.Slot, "map_model": map_slot},
    "blocked_time_intervals": {"model": models.BlockedTimeInterval, "map_model": map_block}
}


def setup_db():
    app.db_session.remove()
    app.db_metadata.drop_all(app.db_engine)
    db_url = os.environ.get('BOOKING_DATABASE_URL', 'sqlite:////tmp/flod_booking.db')
    init_db(db_url)


def map_to_models(fixtures, type, mapped_models):
    models = {}
    mapping = model_mapping[type]
    for fixture in fixtures:
        fixture_id = fixture.pop("id")
        models[fixture_id] = mapping["model"](**mapping["map_model"](fixture, mapped_models))
        app.db_session.add(models[fixture_id])
    return models


@manager.command
def fixtures():
    """Install test data fixtures into the configured database."""
    print "installing fixtures.."
    setup_db()

    fixture_data = json.load(open('./fixtures.json'))

    created_models = {}
    if "resources" in fixture_data:
        resources = fixture_data["resources"]
        created_models["resource_models"] = map_to_models(resources, "resource", created_models)

    if "persons" in fixture_data:
        persons = fixture_data["persons"]
        created_models["person_models"] = map_to_models(persons, "person", created_models)

    if "organisations" in fixture_data:
        organisations = fixture_data["organisations"]
        created_models["organisation_models"] = map_to_models(organisations, "organisation", created_models)

    if "requested_slots" in fixture_data:
        slots = fixture_data["requested_slots"]
        created_models["slot_models"] = map_to_models(slots, "slot", created_models)

    if "blocked_time_intervals" in fixture_data:
        blocked_time_intervals = fixture_data["blocked_time_intervals"]
        created_models["blocked_time_intervals"] = map_to_models(blocked_time_intervals, "blocked_time_intervals",
                                                                 created_models)

    app.db_session.commit()
    print "Done!"


if __name__ == "__main__":
    manager.run()
