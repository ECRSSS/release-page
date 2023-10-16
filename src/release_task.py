import codecs
import pickle
from ctypes import Union

from gitlab.v4.objects import ProjectMergeRequest

from src.jira_service import FixVersionModel

import re

VERSION_PATTERN = re.compile(r'\d+.\d+.\d+')


def validate_service_version(version):
    return VERSION_PATTERN.match(version)


class ConfigsMergeRequest:
    def __init__(self, mr: ProjectMergeRequest):
        self.mr: ProjectMergeRequest = mr

    def get_source_branch(self):
        return self.mr.attributes['source_branch']

    def get_configuration_changes(self):
        return self.mr.changes()['changes']

    def get_services_with_changes_prod(self):
        changes = self.get_configuration_changes()
        return [change['new_path'].split('/')[1].replace('.yaml', '') for change in changes if
                change['new_path'].startswith('dev/')]  # TODO change dev/ to prod/


class Service:
    def __init__(self, name: str, version: str):
        self.name = name,
        self.version = version
        self.is_config_changes = None

    def get_name(self):
        print(self.name)
        return self.name[0]

    def set_is_config_changes(self, is_changes):
        self.is_config_changes = is_changes

    def get_configuration_change_view(self):
        if self.is_config_changes is None:
            return '-'
        elif self.is_config_changes is True:
            return 'Да'
        else:
            return 'Нет изменений'


class ReleaseTaskModel:

    def __init__(self, fix_version: FixVersionModel):
        self.fix_version = fix_version
        self.name = f'Релиз {fix_version.name}'
        self.sql_branch_url = None
        self.services = []

        self.configs_mr = None

    def __updates_service_changes(self):
        if self.configs_mr is not None:
            list_services_with_config_updates = self.configs_mr.get_services_with_changes_prod()
        else:
            list_services_with_config_updates = None

        for service in self.services:
            if list_services_with_config_updates is None:
                service.set_is_config_changes(None)
            elif service in list_services_with_config_updates:
                service.set_is_config_changes(True)
            else:
                service.set_is_config_changes(False)

    def set_configs_mr(self, configs_mr):
        if configs_mr is None:
            self.configs_mr = None
        else:
            self.configs_mr = ConfigsMergeRequest(configs_mr)
        self.__updates_service_changes()

    def add_service(self, service_name, service_version):
        if validate_service_version(service_version) is not None:
            print(service_name)
            self.services.append(Service(service_name, service_version))

    def pickle(self):  # -> returns serialized object
        # for decode -> pickle.loads(codecs.decode(pickled.encode(), "base64"))
        return codecs.encode(pickle.dumps(self), "base64").decode()
