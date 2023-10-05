import codecs
import pickle

from src.jira_service import FixVersionModel

import re

VERSION_PATTERN = re.compile(r'\d+.\d+.\d+')


def validate_service_version(version):
    return VERSION_PATTERN.match(version)


class Service:
    def __init__(self, name: str, version: str):
        self.name = name,
        self.version = version

    def get_name(self):
        print(self.name)
        return self.name[0]


class ReleaseTaskModel:

    def __init__(self, fix_version: FixVersionModel):
        self.fix_version = fix_version
        self.name = f'Релиз {fix_version.name}'
        self.sql_branch_url = None
        self.services = []

    def add_service(self, service_name, service_version):
        if validate_service_version(service_version) is not None:
            print(service_name)
            self.services.append(Service(service_name, service_version))

    def pickle(self):  # -> returns serialized object
        # for decode -> pickle.loads(codecs.decode(pickled.encode(), "base64"))
        return codecs.encode(pickle.dumps(self), "base64").decode()

