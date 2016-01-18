# -*- coding: utf-8 -*-
import os

from app import create_app


application = create_app(os.environ['ORGANISATIONS_DATABASE_URL'])
