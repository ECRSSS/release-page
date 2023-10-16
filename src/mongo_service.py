import codecs
import datetime
import pickle
import re

from pymongo import MongoClient
from jira_service import FixVersionModel, JiraService
from config import MONGO_DB_NAME
from release_task import ReleaseTaskModel


class MongoService:
    FIX_VERSIONS_COLLECTION = 'fix_versions'
    RELEASE_TASKS_COLLECTION = 'release_tasks'

    def __init__(self):
        self.client = MongoClient('mongodb://root:example@127.0.0.1:27017/')

    def save_fix_versions(self, versions: list[FixVersionModel]):
        fv_collection = self.client[MONGO_DB_NAME][self.FIX_VERSIONS_COLLECTION]
        fv_collection.insert_many(
            [{'data': version.pickle(), 'version_id': version.id} for version in versions]
        )

    def read_fix_version_by_version_id(self, version_id) -> FixVersionModel:
        version_id = f'{version_id}'
        versions = [version for version in self.read_fix_versions() if version.id == version_id]
        if len(versions) > 0:
            return versions[0]
        else:
            return None

    def read_fix_versions(self):
        fv_collection = self.client[MONGO_DB_NAME][self.FIX_VERSIONS_COLLECTION]
        versions_pickled = [ver for ver in fv_collection.find()]
        return [pickle.loads(codecs.decode(pickled['data'].encode(), "base64")) for pickled in versions_pickled]

    def clear_versions(self):  # clear fix versions in mongo and return num of deleted rows
        return self.client[MONGO_DB_NAME][self.FIX_VERSIONS_COLLECTION].delete_many({}).deleted_count

    def read_release_tasks(self):
        rt_collection = self.client[MONGO_DB_NAME][self.RELEASE_TASKS_COLLECTION]
        rtasks_pickled = [task for task in rt_collection.find()]
        release_tasks = []
        for pickled_task in rtasks_pickled:
            rtask = pickle.loads(codecs.decode(pickled_task['data'].encode(), "base64"))
            release_tasks.append(rtask)
        return release_tasks

    def read_release_task_by_version_id(self, version_id) -> ReleaseTaskModel:
        version_id = f'{version_id}'
        versions = [task for task in self.read_release_tasks() if task.fix_version.id == version_id]
        if len(versions) > 0:
            return versions[0]
        else:
            return None

    def save_release_task(self, release_task_model: ReleaseTaskModel):
        rt_collection = self.client[MONGO_DB_NAME][self.RELEASE_TASKS_COLLECTION]
        rt_collection.insert_one({'data': release_task_model.pickle(), 'release_version_id': release_task_model.fix_version.id})

    def update_release_task(self, release_task_model):
        rt_collection = self.client[MONGO_DB_NAME][self.RELEASE_TASKS_COLLECTION]
        rt_collection.update_one(filter={'release_version_id': release_task_model.fix_version.id},
                                 update={'$set':{'data': release_task_model.pickle(),
                                         'release_version_id': release_task_model.fix_version.id}})

    def clear_tasks(self):  # clear fix versions in mongo and return num of deleted rows
        return self.client[MONGO_DB_NAME][self.RELEASE_TASKS_COLLECTION].delete_many({}).deleted_count


if __name__ == '__main__':
    # MongoService().clear_tasks()
    pass
