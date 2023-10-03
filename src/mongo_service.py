import codecs
import datetime
import pickle

from pymongo import MongoClient
from jira_service import FixVersionModel, JiraService
from config import MONGO_DB_NAME


class MongoService:
    FIX_VERSIONS_COLLECTION = 'fix_versions'

    def __init__(self):
        self.client = MongoClient('mongodb://root:example@localhost:27017/')

    def save_fix_versions(self, versions: list[FixVersionModel]):
        fv_collection = self.client[MONGO_DB_NAME][self.FIX_VERSIONS_COLLECTION]
        fv_collection.insert_many(
            [{'data': version.pickle()} for version in versions]
        )

    def read_fix_versions(self):
        fv_collection = self.client[MONGO_DB_NAME][self.FIX_VERSIONS_COLLECTION]
        versions_pickled = [ver for ver in fv_collection.find()]
        return [pickle.loads(codecs.decode(pickled['data'].encode(), "base64")) for pickled in versions_pickled]

    def clear_versions(self): # clear fix versions in mongo and return num of deleted rows
        return self.client[MONGO_DB_NAME][self.FIX_VERSIONS_COLLECTION].delete_many({}).deleted_count


if __name__ == '__main__':
     js = JiraService()
     ms = MongoService()
     # versions = ms.read_fix_versions()
     #
     # ms.clear_versions()

     vers = js.get_versions()
     # d = ms.save_fix_versions(vers)
     ms.clear_versions()
     pass
