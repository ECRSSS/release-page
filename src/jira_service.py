from jira import JIRA
import pickle
import codecs
import datetime
from config import JIRA_USER, JIRA_TOKEN, JIRA_URL


class FixVersionModel:
    def __init__(self, jira_project_version, version_issues):
        self.url = f'{JIRA_URL}/projects/SMDEV/versions/{int(jira_project_version.id)}'
        self.id = jira_project_version.id
        self.issues = version_issues
        self.name = jira_project_version.raw['name']
        self.__set_teams()
        self.__set_release_task()

        self.created_at = datetime.datetime.now()

    def __set_teams(self):
        self.teams = set()
        for issue in self.issues:
            self.teams.add(issue.key.split('-')[0])
        self.teams_string = ', '.join(self.teams)

    def __set_release_task(self):
        release_task_list = [issue for issue in self.issues if
                             'Релиз' in issue.fields.summary or 'релиз' in issue.fields.summary]
        if len(release_task_list) > 0:
            self.is_rt_exists = True
            self.release_task = release_task_list[0]
        else:
            self.is_rt_exists = False
            self.release_task = None

    def pickle(self):  # -> returns serialized object
        # for decode -> pickle.loads(codecs.decode(pickled.encode(), "base64"))
        return codecs.encode(pickle.dumps(self), "base64").decode()


class JiraService:

    def __init__(self):
        self.jira_url = JIRA_URL
        self.username = JIRA_USER
        self.token = JIRA_TOKEN
        self.jira = JIRA(server=self.jira_url, basic_auth=(self.username, self.token))
        self.project_key = 'SMDEV'

    def get_versions(self) -> list[FixVersionModel]:
        versions = self.jira.project_versions(self.project_key)
        versions = [version for version in versions if version.archived is False and version.released is False]
        fix_version_objects: list[FixVersionModel] = list()
        for version in versions:
            issues = self.get_all_issues_with_version(version)
            fix_version_objects.append(FixVersionModel(version, issues))
        return fix_version_objects

    def get_all_issues_with_version(self, version):
        return self.jira.search_issues(jql_str=f'fixVersion = "{version.name}"')
