# This is a sample Python script.

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.jira_service import JiraService, FixVersionModel
from src.mongo_service import MongoService
from src.utils import is_versions_cache_time_expired

app = FastAPI()

jira_service = JiraService()
mongo_service = MongoService()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def fix_versions_page(request: Request):
    versions = mongo_service.read_fix_versions()
    if len(versions) == 0 or is_versions_cache_time_expired(versions):
        mongo_service.clear_versions()
        versions = jira_service.get_versions()
        mongo_service.save_fix_versions(versions)
    return templates.TemplateResponse("fix_versions.html", {'request': request,
                                                            'versions': versions
                                                            })


@app.get("/create/{version_id}", response_class=HTMLResponse)
async def create_release_task(request: Request):
    return templates.TemplateResponse("create_release.html", {'request': request})
