# -*- coding: utf-8 -*-
"""Converting brreg_activity_codes from fixture to alembic migration

Revision ID: 56aa02f54e74
Revises: 357cc9fc466b
Create Date: 2014-01-23 08:21:22.953015

"""

# revision identifiers, used by Alembic.
from sqlalchemy.sql import table, column
from sqlalchemy import String

revision = '56aa02f54e74'
down_revision = '357cc9fc466b'

from alembic import op


def upgrade():
    brreg_activity_codes_table = table('brreg_activity_codes',
                                       column('code', String),
                                       column('description')
    )

    op.bulk_insert(
        brreg_activity_codes_table,
        [
            {
                'code': '1 100',
                'description': 'Kunst og kultur'
            },
            {
                'code': '1 200',
                'description': 'Idrett'
            },
            {
                'code': '1 300',
                'description': 'Rekreasjon og sosiale foreninger'
            },
            {
                'code': '2 100',
                'description': 'Grunn- og videregående utdanning'
            },
            {
                'code': '2 200',
                'description': 'Høgskole og universitet'
            },
            {
                'code': '2 300',
                'description': 'Annen utdanning'
            },
            {
                'code': '2 400',
                'description': 'Andre helsetjenester'
            },
            {
                'code': '3 100',
                'description': 'Sykehus og rehabilitering'
            },
            {
                'code': '3 200',
                'description': 'Sykehjem'
            },
            {
                'code': '3 300',
                'description': 'Psykiatriske institusjoner'
            },
            {
                'code': '3 400',
                'description': 'Andre helsetjenester'
            },
            {
                'code': '4 100',
                'description': 'Sosiale tjenester'
            },
            {
                'code': '4 200',
                'description': 'Krisehjelp og støttearbeid'
            },
            {
                'code': '4 300',
                'description': 'Økonomisk og materiell støtte'
            },
            {
                'code': '5 100',
                'description': 'Natur- og miljøvern'
            },
            {
                'code': '5 200',
                'description': 'Dyrevern'
            },
            {
                'code': '6 100',
                'description': 'Lokalsamfunnsutvikling'
            },
            {
                'code': '6 200',
                'description': 'Bolig- og lokalmiljø'
            },
            {
                'code': '6 300',
                'description': 'Arbeidsopplæring'
            },
            {
                'code': '7 100',
                'description': 'Interesseorganisasjoner'
            },
            {
                'code': '7 200',
                'description': 'Juridisk rådgivning'
            },
            {
                'code': '7 300',
                'description': 'Politiske organisasjoner'
            },
            {
                'code': '8 100',
                'description': 'Pengeutdelende stiftelser'
            },
            {
                'code': '8 200',
                'description': 'Frivillighetssentraler'
            },
            {
                'code': '9 100',
                'description': 'Internasjonale organisasjoner'
            },
            {
                'code': '10 100',
                'description': 'Tros- og livssynsorganisasjoner'
            },
            {
                'code': '11 100',
                'description': 'Næringslivs- og arbeidsgiverorganisasjoner'
            },
            {
                'code': '11 200',
                'description': 'Yrkessammenslutninger'
            },
            {
                'code': '11 300',
                'description': 'Arbeidstakerorganisasjoner'
            },
            {
                'code': '12 100',
                'description': 'Andre'
            },
            {
                'code': '13 100',
                'description': 'Barne- og ungdomsorganisasjoner'
            },
            {
                'code': '14 100',
                'description': 'Mangfold og inkludering'
            }
        ]
    )


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
