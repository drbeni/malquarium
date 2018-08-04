import hashlib
import logging
import os
import pathlib
import string
from abc import ABCMeta, abstractmethod

import magic
import ssdeep

from malquarium.settings import STORAGE_BACKEND

STORAGE_BACKEND_MISCONFIGURATION_MESSAGE = 'settings.STORAGE_BACKEND is misconfigured'


class SampleStore:
    def __init__(self):
        if 'local' in STORAGE_BACKEND:
            self.backend = LocalStorageBackend()
        else:
            raise SampleStoreException(STORAGE_BACKEND_MISCONFIGURATION_MESSAGE)

    def get_sample_path(self, sha2):
        return self.backend.get_sample_path(sha2)

    def get_outer_sample_path(self, sha2):
        return self.backend.get_outer_sample_path(sha2)

    def handle_uploaded_file(self, uploaded_file):
        return self.backend.handle_uploaded_file(uploaded_file)

    def calculate_hashes(self, f):
        return self.backend.calculate_hashes(f)

    def calculate_magic(self, sha2):
        try:
            return self.backend.calculate_magic(sha2)
        except magic.MagicException as e:
            print("Magic Exception: {}".format(e))
            return ""

    def calculate_mime(self, sha2):
        try:
            return self.backend.calculate_mime(sha2)
        except magic.MagicException as e:
            print("Magic Exception: {}".format(e))
            return ""

    def persist_file(self, sha2):
        return self.backend.persist_file(sha2)

    def remove_file_from_cache(self, sha2):
        return self.backend.remove_file_from_cache(sha2)

    def delete_sample_file(self, sample):
        return self.backend.delete_sample_file(sample)


class StorageBackend(metaclass=ABCMeta):
    def calculate_hashes(self, f):
        data = f.read()
        if not data:
            f.seek(0)
            data = f.read()

        sha2 = hashlib.sha256(data)
        sha1 = hashlib.sha1(data)
        md5 = hashlib.md5(data)
        ssdeep_hash = ssdeep.hash(data)

        return sha2.hexdigest(), sha1.hexdigest(), md5.hexdigest(), ssdeep_hash

    @abstractmethod
    def get_sample_path(self, sha2):
        raise NotImplementedError

    @abstractmethod
    def get_outer_sample_path(self, sha2):
        raise NotImplementedError

    def calculate_magic(self, sha2):
        return magic.from_file(self.get_sample_path(sha2))

    def calculate_mime(self, sha2):
        mime = magic.Magic(mime=True)
        return mime.from_file(self.get_sample_path(sha2))

    def persist_file(self, sha2):
        return None

    def remove_file_from_cache(self, sha2):
        return True

    def delete_sample_file(self, sample):
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    def __init__(self):
        if 'local' not in STORAGE_BACKEND or 'SAMPLE_STORE' not in STORAGE_BACKEND['local']:
            raise SampleStoreException(STORAGE_BACKEND_MISCONFIGURATION_MESSAGE)

        self.local_dir = STORAGE_BACKEND['local']['SAMPLE_STORE']
        self.outer_dir = STORAGE_BACKEND['local']['OUTER_SAMPLE_STORE']
        self._init_local_sample_store()
        self.logger = logging.getLogger('LocalStorageBackend')

    def _init_local_sample_store(self):
        try:
            if not os.path.isdir(os.path.join(self.local_dir, 'a')):
                pathlib.Path(self.local_dir).mkdir(parents=True, exist_ok=True)

                for l1 in string.hexdigits.lower():
                    pathlib.Path(os.path.join(self.local_dir, l1)).mkdir(exist_ok=True)

                    for l2 in string.hexdigits.lower():
                        pathlib.Path(os.path.join(self.local_dir, l1, l2)).mkdir(exist_ok=True)

                        for l3 in string.hexdigits.lower():
                            pathlib.Path(os.path.join(self.local_dir, l1, l2, l3)).mkdir(exist_ok=True)

        except OSError as e:
            raise SampleStoreException("Failed to initialize sample store because of {}".format(e)) from e

    def handle_uploaded_file(self, uploaded_file):
        file_info = FileInfo(*self.calculate_hashes(uploaded_file))

        if not os.path.isfile(self.get_sample_path(file_info.sha2)):
            self.logger.info("Stored file {}".format(file_info.sha2))
            with open(self.get_sample_path(file_info.sha2), "w+b") as dest:
                if hasattr(uploaded_file, 'chunks'):
                    for chunk in uploaded_file.chunks():
                        dest.write(chunk)
                else:
                    uploaded_file.seek(0)
                    dest.write(uploaded_file.read())

        return file_info

    def get_sample_path(self, sha2):
        return os.path.join(self.local_dir, sha2[0], sha2[1], sha2[2], sha2)

    def get_outer_sample_path(self, sha2):
        return os.path.join(self.outer_dir, sha2[0], sha2[1], sha2[2], sha2)

    def delete_sample_file(self, sample):
        sample_path = self.get_sample_path(sample.sha2)
        if os.path.isfile(sample_path):
            os.remove(sample_path)

        sample.delete()


class FileInfo:
    def __init__(self, sha2, sha1, md5, ssdeep):
        self.sha2 = sha2
        self.sha1 = sha1
        self.md5 = md5
        self.ssdeep = ssdeep


class SampleStoreException(Exception):
    pass


class SampleNotFoundException(Exception):
    pass
