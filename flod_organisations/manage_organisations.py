# -*- coding: utf-8 -*-
import os
import copy

from flask.ext.script import Manager
from isodate import parse_datetime

from app import app
from domain import models
from database import init_db


manager = Manager(app)
import json


def no_map(model, mapped_models):
    return model

def map_organisation(model, mapped_models):

    business_address = model.get("business_address_id", None)
    if business_address:
        model["business_address"] = mapped_models["addresses"][business_address]

    postal_address = model.get("postal_address_id", None)
    if postal_address:
        model["postal_address"] = mapped_models["addresses"][postal_address]

    # skipping organisation_brreg_activities and organisation_flod_activity_types for now. not needed yet...

    return model

def map_organisation_person_associations(model, mapped_models):

    person_id = model.get("person_id", None)
    if person_id:
        model["person"] = mapped_models["persons"][person_id]
        # Just add random role...
        model["roles"] = [mapped_models["person_org_assoc_roles"][1]]
        del model["person_id"]
        del model["organisation_id"]

    return model


model_mapping = {
    "addresses": {"model": models.Address, "map_model": no_map},
    "organisations": {"model": models.Organisation, "map_model": map_organisation},
    "persons": {"model": models.Person, "map_model": no_map},
    "organisation_person_associations": {"model": models.OrganisationPersonAssociation, "map_model": map_organisation_person_associations},
    "person_org_assoc_roles": {"model": models.PersonOrgAssociationRole, "map_model": no_map},
}


def setup_db():
    app.db_session.remove()
    #app.db_metadata.drop_all(app.db_engine)
    db_url = os.environ.get('ORGANISATIONS_DATABASE_URL', 'sqlite:////tmp/flod_organisations.db')
    init_db(db_url)


def map_to_models(fixtures, type, mapped_models):
    models = {}
    mapping = model_mapping[type]
    for fixture in fixtures:
        fixture_id = fixture.pop("id")
        backup_fixture = copy.deepcopy(fixture)
        models[fixture_id] = mapping["model"](**mapping["map_model"](fixture, mapped_models))

        if type == "organisation_person_associations":
            models[fixture_id].organisation_id = backup_fixture["organisation_id"]
        app.db_session.add(models[fixture_id])
    return models


@manager.command
def fixtures():
    """Install test data fixtures into the configured database."""
    print "installing fixtures.."
    setup_db()

    fixture_data = json.load(open('./fixtures_organisations.json'))

    created_models = {}

    if "addresses" in fixture_data:
        addresses = fixture_data["addresses"]
        created_models["addresses"] = map_to_models(addresses, "addresses", created_models)

    if "organisations" in fixture_data:
        organisations = fixture_data["organisations"]
        created_models["organisations"] = map_to_models(organisations, "organisations", created_models)

    if "persons" in fixture_data:
        persons = fixture_data["persons"]
        created_models["persons"] = map_to_models(persons, "persons", created_models)

    if "person_org_assoc_roles" in fixture_data:
        person_org_assoc_roles = fixture_data["person_org_assoc_roles"]
        created_models["person_org_assoc_roles"] = map_to_models(person_org_assoc_roles, "person_org_assoc_roles", created_models)

    if "organisation_person_associations" in fixture_data:
        organisation_person_associations = fixture_data["organisation_person_associations"]
        created_models["organisation_person_associations"] = map_to_models(organisation_person_associations, "organisation_person_associations", created_models)



    app.db_session.commit()
    print "Done!"


if __name__ == "__main__":
    manager.run()
