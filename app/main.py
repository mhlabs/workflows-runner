import datetime
from decimal import Decimal
import logging
import os
from pydantic import BaseModel
from croniter import croniter_range
import json
from fastapi import FastAPI, HTTPException, Header, Request
from typing import Optional
from fastapi.logger import logger
from pydantic import BaseSettings
from cloud_logging.middleware import LoggingMiddleware
from cloud_logging.setup import setup_logging
from google.cloud import workflows_v1
from google.cloud.workflows import executions_v1
import pendulum
import traceback


class Settings(BaseSettings):
    environment: str = 'development'


class Range(BaseModel):
    start: datetime.datetime
    stop: datetime.datetime
    step: str


settings = Settings()
app = FastAPI()

publish_futures = []
DRIVER = os.environ.get('DRIVER')

if settings.environment == 'production':
    setup_logging()
    app.add_middleware(LoggingMiddleware)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)


def data_type_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    if isinstance(x, Decimal):
        return float(x)
    raise TypeError("Unknown type")


@app.post("/v1/projects/{project}/locations/{location}/workflows/{workflow}/executions")
async def headers(project, location, workflow, request: Request,
                  timezone: str = "UTC",
                  x_cloudScheduler_scheduleTime: Optional[str] = Header(None)):
    try:
        _date_obj = pendulum.parse(x_cloudScheduler_scheduleTime).in_timezone(timezone)

        body = await request.json()
        # body['scheduleTime']=x_cloudScheduler_scheduleTime
        body['scheduleTime'] = _date_obj.isoformat()
        # Set up API clients.
        execution_client = executions_v1.ExecutionsClient()
        workflows_client = workflows_v1.WorkflowsClient()

        # Construct the fully qualified location path.
        parent = workflows_client.workflow_path(project, location, workflow)

        # Execute the workflow.
        execution = execution_client.create_execution(
            request={
                "parent": parent,
                "execution": {
                    "argument": json.dumps(body, default=data_type_handler)
                }
            }
        )
        # logger.info(f"Created execution: {execution.name}")
        response = {
            "X-CloudScheduler-ScheduleTime": x_cloudScheduler_scheduleTime,
            "project": project,
            "location": location,
            "workflow": workflow,
            "execution": {
                "name": execution.name,
                "argument": execution.argument
            }
        }
        logger.info(response)
        return response
    except Exception as e:
        error_string = repr(e)
        # logger.error(error_string)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_string)


@app.post("/range")
async def return_range(range: Range):
    try:
        response = []
        for dt in croniter_range(range.start, range.stop, range.step):
            response.append(dt)
            logger.info(dt)
        return response
    except Exception as e:
        error_string = repr(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_string)
