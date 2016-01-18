#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from abc import ABCMeta, abstractmethod
from os import environ
from uuid import uuid4

from boto.s3.connection import Location, S3Connection
from boto.s3.key import Key
from flask import current_app, url_for
from werkzeug import secure_filename


def uuid_with_ext(filename):
    return str(uuid4()) + os.path.splitext(secure_filename(filename))[1]


class Backend(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def get_url(self):
        pass


class FileBackend(Backend):
    name = 'file'

    def __init__(self, file, filename, path):
        self.file = file
        self.filename = filename
        self.upload_path = os.path.join(path, self.filename)

    def save(self):
        if not os.path.isfile(self.upload_path):
            self.file.save(self.upload_path)

    def delete(self):
        if os.path.isfile(self.upload_path):
            os.remove(self.upload_path)

    def get_url(self, route):
        return url_for(route, filename=self.filename)


class S3Backend(Backend):
    name = 's3'

    def __init__(self, file, filename, path=None):
        self.file = file
        self.filename = filename

    def _get_bucket(self):
        bucket_name = environ.get('S3_BUCKET', 'flod')
        if self.s3.lookup(bucket_name) is None:
            current_app.logger.info('Bucket %s does not exist, will create it',
                                    bucket_name)
            return self.s3.create_bucket(bucket_name, location=Location.EU,
                                         policy='public-read')
        else:
            return self.s3.get_bucket(bucket_name)

    def _connect_s3(self):
        # S3Connection will use the environment variables AWS_ACCESS_KEY_ID and
        # AWS_SECRET_ACCESS_KEY to authenticate
        if not hasattr(self, 's3'):
            self.s3 = S3Connection()
        if not hasattr(self, 'bucket'):
            self.bucket = self._get_bucket()

    def save(self):
        self._connect_s3()
        key = Key(self.bucket, self.filename)
        key.set_contents_from_file(self.file.stream)
        self.key = key

    def delete(self):
        self._connect_s3()
        key = Key(self.bucket, self.filename)
        self.bucket.delete_key(key)

    def get_url(self):
        if not hasattr(self, 'key'):
            return ''
        return self.key.generate_url(expires_in=0, query_auth=False)


def get_backend(file, filename, path):
    backend = environ.get('FILE_BACKEND', '').lower()
    if backend == S3Backend.name:
        return S3Backend(file, filename, path)
    return FileBackend(file, filename, path)


def get_backend_for_model(model, path):
    if model.storage_backend == 's3':
        return S3Backend(None, filename=model.filename, path=path)
    elif model.storage_backend == 'file':
        return FileBackend(None, filename=model.filename, path=path)
    return None
