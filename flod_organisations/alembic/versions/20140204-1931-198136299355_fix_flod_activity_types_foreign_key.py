# -*- coding: utf-8 -*-
"""fix flod_activity_types foreign key

Revision ID: 198136299355
Revises: 136f4368db57
Create Date: 2014-02-04 19:31:20.405774

"""

# revision identifiers, used by Alembic.
revision = '198136299355'
down_revision = '136f4368db57'

from alembic import op
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column


def get_brreg_activity_code_id(brreg_activity_codes_code):
    find_id_for = """
        SELECT id
        FROM   brreg_activity_codes
        WHERE  code like '%s'
    """

    connection = op.get_bind()
    result = connection.execute(find_id_for % brreg_activity_codes_code)
    if result.rowcount != 1:
        raise RuntimeError('The brreg_activity_codes with code %s does not exist!' % brreg_activity_codes_code)
    return result.first()['id']


def upgrade():
    kunst_og_kultur_id = get_brreg_activity_code_id('1 100')
    idrett_id = get_brreg_activity_code_id('1 200')

    op.execute('truncate flod_activity_type restart identity cascade;')

    flod_activity_type_table = table('flod_activity_type',
                                     column('name', String),
                                     column('brreg_activity_code_id', Integer))

    op.bulk_insert(
        flod_activity_type_table,
        [
            {'name': 'Aking, bob, skeleton', 'brreg_activity_code_id': idrett_id},
            {'name': 'Allidrett', 'brreg_activity_code_id': idrett_id},
            {'name': 'Amerikansk idrett', 'brreg_activity_code_id': idrett_id},
            {'name': 'Badminton', 'brreg_activity_code_id': idrett_id},
            {'name': 'Bandy', 'brreg_activity_code_id': idrett_id},
            {'name': 'Basketball', 'brreg_activity_code_id': idrett_id},
            {'name': 'Bedriftsidrett', 'brreg_activity_code_id': idrett_id},
            {'name': 'Biljard', 'brreg_activity_code_id': idrett_id},
            {'name': 'Boksing', 'brreg_activity_code_id': idrett_id},
            {'name': 'Bordtennis', 'brreg_activity_code_id': idrett_id},
            {'name': 'Bowling', 'brreg_activity_code_id': idrett_id},
            {'name': 'Bryting', 'brreg_activity_code_id': idrett_id},
            {'name': 'Bueskyting', 'brreg_activity_code_id': idrett_id},
            {'name': 'Casting', 'brreg_activity_code_id': idrett_id},
            {'name': 'Cheerleading', 'brreg_activity_code_id': idrett_id},
            {'name': 'Cricket', 'brreg_activity_code_id': idrett_id},
            {'name': 'Curling', 'brreg_activity_code_id': idrett_id},
            {'name': 'Dans', 'brreg_activity_code_id': idrett_id},
            {'name': 'Fekting', 'brreg_activity_code_id': idrett_id},
            {'name': 'Fotball', 'brreg_activity_code_id': idrett_id},
            {'name': 'Friidrett', 'brreg_activity_code_id': idrett_id},
            {'name': 'Håndball', 'brreg_activity_code_id': idrett_id},
            {'name': 'Ishockey', 'brreg_activity_code_id': idrett_id},
            {'name': 'Judo', 'brreg_activity_code_id': idrett_id},
            {'name': 'Kampsport', 'brreg_activity_code_id': idrett_id},
            {'name': 'Kickboksing', 'brreg_activity_code_id': idrett_id},
            {'name': 'Langrenn, hopp', 'brreg_activity_code_id': idrett_id},
            {'name': 'Orientering', 'brreg_activity_code_id': idrett_id},
            {'name': 'Skiskyting', 'brreg_activity_code_id': idrett_id},
            {'name': 'Skøytesport', 'brreg_activity_code_id': idrett_id},
            {'name': 'Softball og baseball', 'brreg_activity_code_id': idrett_id},
            {'name': 'Svømming', 'brreg_activity_code_id': idrett_id},
            {'name': 'Sykling', 'brreg_activity_code_id': idrett_id},
            {'name': 'Tennis', 'brreg_activity_code_id': idrett_id},
            {'name': 'Turn', 'brreg_activity_code_id': idrett_id},
            {'name': 'Volleyball', 'brreg_activity_code_id': idrett_id},
            {'name': 'Dans', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Festival', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Film/multimedia', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Historielag', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Hobby', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Husflid', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Kor', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Kulturminnevern', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Kunst', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Kurs/opplæring', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Litteratur', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Musikk/sang', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Scenekunst', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Skolekorps', 'brreg_activity_code_id': kunst_og_kultur_id},
            {'name': 'Ungdoms/voksenkorps', 'brreg_activity_code_id': kunst_og_kultur_id}
        ]
    )


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
