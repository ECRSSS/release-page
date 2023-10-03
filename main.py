# This is a sample Python script.
import requests_cache
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src import jira_facade

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Storage:
    FIX_VERSIONS = []


@app.get("/", response_class=HTMLResponse)
async def fix_versions_page(request: Request):
    Storage.FIX_VERSIONS = jira_facade.get_versions()
    return templates.TemplateResponse("fix_versions.html", {'request': request,
                                                            'versions': jira_facade.get_versions()
                                                            })


@app.get("/", response_class=HTMLResponse)
async def create_release_task(request: Request):
    return templates.TemplateResponse("create_release.html", {'request': request})
