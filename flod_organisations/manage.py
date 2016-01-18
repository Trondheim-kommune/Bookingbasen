# -*- coding: utf-8 -*-
import os

from flask.ext.script import Manager

from run import application
from domain import models
from database import init_db


manager = Manager(application)
import json


def no_map(model, mapped_models):
    return model


def map_activity_type(model, mapped_models):
    if "brreg_activity_code" in model:
        brreg_activity_code = model["brreg_activity_code"]
        model["brreg_activity_code"] = mapped_models["brreg_activity_codes"][brreg_activity_code]
    return model


model_mapping = {
    "brreg_activity_codes": {"model": models.BrregActivityCode, "map_model": no_map},
    "flod_activity_types": {"model": models.FlodActivityType, "map_model": map_activity_type},
}


def setup_db():
    db_url = os.environ.get('ORGANISATIONS_DATABASE_URL', 'sqlite:////tmp/flod_organisations.db')
    init_db(db_url)


def map_to_models(fixtures, type, mapped_models):
    models = {}
    mapping = model_mapping[type]
    if not application.db_session.query(mapping["model"]).count():
        for fixture in fixtures:
            fixture_id = fixture.pop("id")
            models[fixture_id] = mapping["model"](**mapping["map_model"](fixture, mapped_models))
            application.db_session.add(models[fixture_id])
    else:
        print "%s is already loaded" % type
    return models


@manager.command
def fixtures():
    """Install test data fixtures into the configured database."""
    print("installing fixtures..")
    setup_db()

    fixture_data = json.load(open('./fixtures.json'))

    created_models = {}

    if "brreg_activity_codes" in fixture_data:
        activity_codes = fixture_data["brreg_activity_codes"]
        created_models["brreg_activity_codes"] = map_to_models(activity_codes, "brreg_activity_codes", created_models)

    if "flod_activity_types" in fixture_data:
        activity_types = fixture_data["flod_activity_types"]
        created_models["flod_activity_types"] = map_to_models(activity_types, "flod_activity_types", created_models)

    application.db_session.commit()
    print("Done!")


if __name__ == "__main__":
    manager.run()
