import logging

from shared.initialization.database import get_database

import uvicorn
from fastapi import FastAPI

from database import merge_unmerged_measurements, rename_issue_lead_time
from routes import health, measurements, metrics, reports

internal_api = FastAPI()
DATABASE = get_database()

@internal_api.on_event("startup")
def startup_db_client():
    init_database()
    merge_unmerged_measurements(DATABASE)
    rename_issue_lead_time(DATABASE)


@internal_api.on_event("shutdown")
def cleanup():
    logging.info("Cleanup ... ")


internal_api.include_router(health)
internal_api.include_router(metrics)
internal_api.include_router(reports)
internal_api.include_router(measurements)

if __name__ == '__main__':
    uvicorn.run("quality_time_server:internal_api", host="localhost",
                port=5002, log_level="info", reload=True)
