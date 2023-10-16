# This is a sample Python script.
from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from src.jira_service import JiraService, FixVersionModel
from src.mongo_service import MongoService
from src.release_task import ReleaseTaskModel, ConfigsMergeRequest
from src.utils import is_versions_cache_time_expired, str_is_not_empty_or_none
from src.config import BACKEND_HOST
from src.gitlab_service import GitlabService

app = FastAPI()

origins = [
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jira_service = JiraService()
mongo_service = MongoService()
gitlab_service = GitlabService()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/versions", response_class=HTMLResponse)
async def fix_versions_page(request: Request):
    versions = mongo_service.read_fix_versions()
    return templates.TemplateResponse("fix_versions.html", {'request': request,
                                                            'versions': versions,
                                                            'backend_host': BACKEND_HOST
                                                            })


@app.get("/", response_class=HTMLResponse)
async def entry(request: Request):
    return templates.TemplateResponse("loading_page.html", {'request': request,
                                                            'backend_host': BACKEND_HOST})


@app.get("/refresh_versions", response_class=JSONResponse)
async def refresh_versions(request: Request):
    versions = mongo_service.read_fix_versions()
    if len(versions) == 0 or is_versions_cache_time_expired(versions):
        mongo_service.clear_versions()
        versions = jira_service.get_versions()
        mongo_service.save_fix_versions(versions)
    return JSONResponse(content={'redirect': '/versions'}, headers={'Access-Control-Allow-Origin': '*'})


@app.get("/clear_cache_versions", response_class=JSONResponse)
async def clear_cache_versions(request: Request):
    mongo_service.clear_versions()
    return JSONResponse(content={'STATUS': 'OK'}, headers={'Access-Control-Allow-Origin': '*'})


@app.get("/debug_delete_tasks", response_class=JSONResponse)
async def debug_delete_tasks(request: Request):
    mongo_service.clear_tasks()
    return JSONResponse(content={'STATUS': 'OK'}, headers={'Access-Control-Allow-Origin': '*'})


@app.get("/create_task/{version_id}")
async def create_release_task(
        request: Request, version_id: str,
        action: Union[str, None] = None,
        service_name: Union[str, None] = None,
        service_version: Union[str, None] = None,
        configs_mr_name: Union[str, None] = None,
        sql_url: Union[str, None] = None
):
    print(f'service {service_name}, version: {service_version}, action: {action}')
    target_fix_version = mongo_service.read_fix_version_by_version_id(version_id)

    # список веток открытых МRов
    opened_configs_merge_requests = gitlab_service.configs_repository.get_mr_list()
    merge_requests_source_branches = [mr.attributes['source_branch'] for mr in opened_configs_merge_requests
                                      if mr.attributes['target_branch'] == 'master']
    merge_requests_source_branches.insert(0, '-')

    if target_fix_version.is_rt_exists is True:
        return templates.TemplateResponse("task_already_exists.html",
                                          {'request': request, 'version': target_fix_version})
    else:
        release_task = mongo_service.read_release_task_by_version_id(version_id)

        if release_task is None:
            rtm = ReleaseTaskModel(target_fix_version)
            mongo_service.save_release_task(rtm)
            release_task = mongo_service.read_release_task_by_version_id(target_fix_version.id)

        if action is not None and action == 'add_service':
            if str_is_not_empty_or_none(service_name) and str_is_not_empty_or_none(service_version):
                release_task.add_service(service_name, service_version)
                mongo_service.update_release_task(release_task)
            return RedirectResponse(f"/create_task/{version_id}")

        elif action is not None and action == 'set_configs':
            config_mrs = gitlab_service.configs_repository.get_mr_list()
            config_mr = [mr for mr in config_mrs if mr.attributes['source_branch']
                         == configs_mr_name and mr.attributes['target_branch'] == 'master'][0]
            release_task.set_configs_mr(config_mr)
            mongo_service.update_release_task(release_task)
            return RedirectResponse(f"/create_task/{version_id}")

        return templates.TemplateResponse("create_release_task.html",
                                          {'request': request,
                                           'version': target_fix_version,
                                           'release_task': release_task,
                                           'services': release_task.services,
                                           'opened_config_repo_mrs': merge_requests_source_branches
                                           })


@app.get("/add_service_to_task/{task_id}", response_class=HTMLResponse)
async def create_release_task(request: Request, version_id):
    target_fix_version = mongo_service.read_fix_version_by_version_id(version_id)
    if target_fix_version.is_rt_exists is True:
        return templates.TemplateResponse("task_already_exists.html",
                                          {'request': request, 'version': target_fix_version})
    else:
        return templates.TemplateResponse("create_release_task.html",
                                          {'request': request, 'version': target_fix_version})


if __name__ == '__main__':
    gitlab_service.__gitlab_service()
    pass
