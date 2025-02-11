import os
import logging

import sqlalchemy
import uvicorn as uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from starlette.responses import Response
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select


class Activity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: float = Field(index=True)
    user_sid: str = Field(index=True)
    user_ip: str = Field(index=True)
    user_name: str = Field(index=True)
    user_display_name: str = Field(index=True)
    sys_name: str = Field(index=True)
    sys_version: str = Field()


load_dotenv()
app = FastAPI()

sqlite_file_name = "users_dev.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


def get_session():
    with Session(engine) as session:
        yield session


ALLOWED_IP = os.environ.get("allowed_ip").split(',')

logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s %(message)s")
logging.basicConfig(filename="app.log", level=logging.ERROR, format="%(asctime)s %(message)s")

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionDep = Annotated[Session, Depends(get_session)]


@app.middleware("http")
async def log_permit_requests(request: Request, call_next):
    response = await call_next(request)
    logging.info(f"request: {request.method} {request.url} {response.status_code}")
    if request.client.host not in ALLOWED_IP:
        response = Response(content=f"Access denied: 403", status_code=403)
        logging.info(f"Access denied: {request.client.host} {response.status_code}")
    return response


@app.post("/api/v1/activity/")
def save_user_activity(activity: Activity, session: SessionDep):
    try:
        session.add(activity)
        session.commit()
        session.refresh(activity)
        logging.info(f"Activity saved: {activity}")
        return {"status": "success", "activity": activity}
    except sqlalchemy.exc.IntegrityError as err:
        logging.error(f"Error: {err}")
        return {"status": "error", "activity": activity}


@app.get("/api/v1/activity/user_sid/{user_sid}/")
def read_activity_by_sid(user_sid: str, session: SessionDep):
    statement = select(Activity).where(Activity.user_sid == user_sid)
    activity = session.exec(statement).all()
    logging.info(f"Activity by SID: {activity}")
    if not activity:
        logging.error(f"SID not found: {user_sid}")
        raise HTTPException(status_code=404, detail="SID not found")
    return activity


@app.get("/api/v1/activity/user_name/{user_name}/")
def read_activity_by_user_name(user_name: str, session: SessionDep):
    statement = select(Activity).where(Activity.user_name == user_name)
    activity = session.exec(statement).all()
    logging.info(f"Activity by user_name: {activity}")
    if not activity:
        logging.error(f"user_name not found: {user_name}")
        raise HTTPException(status_code=404, detail="user_name not found")
    return activity


@app.get("/api/v1/activity/user_ip/{user_ip}/")
def read_activity_by_user_ip(user_ip: str, session: SessionDep):
    statement = select(Activity).where(Activity.user_ip == user_ip)
    activity = session.exec(statement).all()
    logging.info(f"Activity by user_ip: {activity}")
    if not activity:
        logging.error(f"user_ip not found: {user_ip}")
        raise HTTPException(status_code=404, detail="user_ip not found")
    return activity


@app.get("/api/v1/activity/sys_name/{sys_name}/")
def read_activity_by_sys_name(request: Request,
                              sys_name: str,
                              session: SessionDep,
                              offset: int = 0,
                              limit: Annotated[int, Query(le=100)] = 100):
    statement = select(Activity).where(Activity.sys_name == sys_name).offset(offset).limit(limit).order_by(Activity.id)
    activity = session.exec(statement).all()
    logging.info(f"{request.client.host} Select activity by sys_name: {sys_name}, count:{len(activity)}")
    if not activity:
        logging.error(f"sys_name not found: {sys_name}")
        raise HTTPException(status_code=404, detail="sys_name not found")
    return activity



if __name__ == "__main__":
    uvicorn.run(app, host=os.environ.get("server_ip"), port=int(os.environ.get("server_port")))
