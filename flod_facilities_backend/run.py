# -*- coding: utf-8 -*-
import os

from app import create_app


application = create_app(os.environ['DATABASE_URL'])
