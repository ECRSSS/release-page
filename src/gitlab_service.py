import gitlab
from gitlab.v4.objects.projects import Project
from config import GITLAB_URL, GITLAB_TOKEN
from config import GITLAB_CONSUL_PROJECT_ID, GITLAB_SQL_PROJECT_ID


class BaseRepo:

    def __init__(self, project):
        self.cached_mrs = None
        self.project = project

    def get_mr_list(self):
        self.cached_mrs = self.project.mergerequests.list(state='opened')
        return self.cached_mrs

    def get_cached_mr_list(self):
        return self.cached_mrs

    def get_mr_by_branch(self, branch):
        return next((mr for mr in self.cached_mrs if mr.source_branch == branch), None)


class ConfigsRepo(BaseRepo):
    pass


class SqlRepo(BaseRepo):
    pass


class GitlabService:

    def __init__(self):
        self.gc = gitlab.Gitlab(url=GITLAB_URL, oauth_token=GITLAB_TOKEN, ssl_verify=False)
        self.configs_repository = ConfigsRepo(self.gc.projects.get(id=GITLAB_CONSUL_PROJECT_ID))
        self.sql_scripts_repository = self.gc.projects.get(id=GITLAB_CONSUL_PROJECT_ID)


if __name__ == '__main__':
    mrs = GitlabService().configs_repository.get_mr_list()
    pass
