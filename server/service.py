import os
import logging

import uvicorn as uvicorn
from fastapi import FastAPI, Request
from starlette.responses import Response
from pydantic import BaseModel
from dotenv import load_dotenv
from db import save_activity, get_activity_user_sid, get_activity_user_ip, get_activity_sys_name

load_dotenv()
app = FastAPI()

ALLOWED_IP = os.environ.get("allowed_ip").split(',')

logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s %(message)s")
logging.basicConfig(filename="app.log", level=logging.ERROR, format="%(asctime)s %(message)s")


class Activity(BaseModel):
    timestamp: float
    user_sid: str
    user_ip: str
    user_name: str
    user_display_name: str
    sys_name: str
    sys_version: str

    def save(self):
        return save_activity(
            timestamp=self.timestamp,
            user_sid=self.user_sid,
            user_name=self.user_name,
            user_display_name=self.user_display_name,
            user_ip=self.user_ip,
            sys_name=self.sys_name,
            sys_version=self.sys_version,

        )

    def get_user_sid(self):
        return get_activity_user_sid(
            user_sid=self.user_sid
        )

    def get_user_ip(self):
        return get_activity_user_ip(
            user_ip=self.user_ip
        )

    def get_sys_name(self):
        return get_activity_sys_name(
            sys_name=self.sys_name
        )


@app.middleware("http")
async def log_permit_requests(request: Request, call_next):
    response = await call_next(request)
    logging.info(f"request: {request.method} {request.url} {response.status_code}")
    if request.client.host not in ALLOWED_IP:
        response = Response(content=f"Access denied: 403", status_code=403)
        logging.info(f"Access denied: {request.client.host} {response.status_code}")
    return response


@app.post("/api/v1/activities/")
async def save_user_login(item: Activity):
    if item.save():
        return {"status": "success"}
    else:
        return {"status": "error"}


@app.get("/api/v1/activities/user_sid/{user_sid}/")
async def get_user_sid(user_sid):
    return get_activity_user_sid(user_sid=user_sid)


@app.get("/api/v1/activities/user_ip/{user_ip}/")
async def get_user_ip(user_ip: str):
    return get_activity_user_ip(user_ip=user_ip)


@app.get("/api/v1/activities/sys_name/{sys_name}/")
async def get_sys_name(sys_name):
    return get_activity_sys_name(sys_name=sys_name)


if __name__ == "__main__":
    uvicorn.run(app, host=os.environ.get("server_ip"), port=int(os.environ.get("server_port")))
