from jira import JIRA

jira_url = 'https://jira.mtsbank.ru'
username = 'user'
token = 'token'

jira = JIRA(server=jira_url, basic_auth=(username, token))
project_key = '*'


def get_versions():
    versions = jira.project_versions(project_key)
    versions = [version for version in versions if version.archived is False and version.released is False]
    fix_version_objects: list[FixVersionModel] = list()
    for version in versions:
        issues = get_all_issues_with_version(version)
        fix_version_objects.append(FixVersionModel(version, issues))
    return fix_version_objects


def get_all_issues_with_version(version):
    return jira.search_issues(jql_str=f'fixVersion = "{version.name}"')


class FixVersionModel:

    def __init__(self, jira_project_version, version_issues):
        self.url = jira_project_version.raw['self']
        self.issues = version_issues
        self.name = jira_project_version.raw['name']
        self.__set_teams()
        self.__set_release_task()

    def __set_teams(self):
        self.teams = set()
        for issue in self.issues:
            self.teams.add(issue.key.split('-')[0])
        self.teams_string = ', '.join(self.teams)

    def __set_release_task(self):
        release_task_list = [issue for issue in self.issues if 'Релиз' in issue.fields.summary or 'релиз' in issue.fields.summary]
        if len(release_task_list) > 0:
            self.is_rt_exists = True
            self.release_task = release_task_list[0]
        else:
            self.is_rt_exists = False
            self.release_task = None


if __name__ == '__main__':
    fix_versions = get_versions()
    pass
