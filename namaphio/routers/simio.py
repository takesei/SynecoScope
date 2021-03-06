from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import ORJSONResponse
from fastapi import Query, Path, Depends, Response, status, Body, HTTPException

from typing import List, Dict, Any, Optional, Union, Callable

from uuid import uuid4

from ..dependencies import connect_database
from .. import runner

router = APIRouter(
    prefix="/simulator",
    tags=['simulator'],
    default_response_class=ORJSONResponse,
)


@router.get('/start/{table}')
def start_sim(
    background_tasks: BackgroundTasks,
    table: Optional[str] = Path(..., title="Table name in DB", example='roppongi'),
    sims: Optional[List[str]] = Query(None, title="List Of SimulationName", example=['Ecoimpact']),
    db: Optional[Any] = Depends(connect_database)
):
    id = str(uuid4().hex)
    background_tasks.add_task(
        runner.simulator.run,
        id=id,
        names=sims,
        db=db,
        table=table,
    )
    return id


@router.get('/stop')
def stop_sim(
    ids: Optional[List[str]] = Query(None, title="List Of Session ID"),
    db: Optional[Any] = Depends(connect_database)
):
    res = status.HTTP_202_ACCEPTED if runner.simulator.stop(db, sims) else status.HTTP_403_FORBIDDEN
    return Response(status_code=res)


@router.get('/status')
def get_status(
    db: Optional[Any] = Depends(connect_database)
):
    return runner.simulator.get_jobs(db)
