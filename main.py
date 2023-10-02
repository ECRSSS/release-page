# This is a sample Python script.
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/index/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("index.html", {"request": request, "id": id,
                                                     "results": [
                                                         {"name": "Example", "status": "Accepted", "number": 34, "task_exists": False}
                                                     ]})
