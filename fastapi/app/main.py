from app.db import get_session, init_db
from app.models import Entity
from sqlmodel import select

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, FastAPI

from .task import sample_task

app = FastAPI()

"""
We have imported the sample_task from task.py and called it in the sync_data() function. 
This function will be called when the user hits the /api/start_sync endpoint.

We have also imported the get_session() function from db.py and used it in the entities() function.
This function will be called when the user hits the /api/entities endpoint.

TODO list:
- Add error handling
- Add logging
- Add unit tests
"""


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/api/start-worker")
async def sync_data():
    result = sample_task.apply_async()
    task_id = result.id
    return {
        "status": "Accepted", 
        "message": "Data sync process has been started. It may take 10-15 minutes to complete. Please check the status after some time.",
        "task_id": task_id,
        }


@app.get("/api/entities")
async def entities(session: AsyncSession = Depends(get_session), limit: int = 10, offset: int = 0):
    result = await session.execute(select(Entity).limit(limit).offset(offset))
    entities = result.scalars().all()
    return [Entity(id=entity.id, title=entity.title, description=entity.description, image=entity.image) for entity in entities]
