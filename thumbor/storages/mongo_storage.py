#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from datetime import datetime
from cStringIO import StringIO

from pymongo import Connection
import gridfs

from thumbor.storages import BaseStorage
from thumbor.config import conf

class Storage(BaseStorage):

    def __conn__(self):
        connection = Connection(conf.MONGO_STORAGE_SERVER_HOST, conf.MONGO_STORAGE_SERVER_PORT)
        db = connection[conf.MONGO_STORAGE_SERVER_DB]
        storage = db[conf.MONGO_STORAGE_SERVER_COLLECTION]

        return connection, db, storage

    def put(self, path, bytes):
        connection, db, storage = self.__conn__()

        doc = {
            'path': path,
            'created_at': datetime.now()
        }

        doc_with_crypto = dict(doc)
        if conf.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            if not conf.SECURITY_KEY:
                raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
            doc_with_crypto['crypto'] = conf.SECURITY_KEY
        

        fs = gridfs.GridFS(db)
        file_data = fs.put(StringIO(bytes), **doc)

        doc_with_crypto['file_id'] = file_data
        storage.insert(doc_with_crypto)

    def put_crypto(self, path):
        if not conf.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        connection, db, storage = self.__conn__()

        if not conf.SECURITY_KEY:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        crypto = storage.find_one({'path': path})

        crypto['crypto'] = conf.SECURITY_KEY
        storage.update(crypto)

    def get_crypto(self, path):
        connection, db, storage = self.__conn__()

        crypto = storage.find_one({'path': path})
        return crypto.get('crypto') if crypto else None

    def get(self, path):
        connection, db, storage = self.__conn__()

        stored = storage.find_one({'path': path})

        if not stored or self.__is_expired(stored):
            return None

        fs = gridfs.GridFS(db)

        contents = fs.get(stored['file_id']).read()

        return str(contents)

    def __is_expired(self, stored):
        timediff = datetime.now() - stored.get('created_at')
        return timediff.seconds > conf.STORAGE_EXPIRATION_SECONDS

