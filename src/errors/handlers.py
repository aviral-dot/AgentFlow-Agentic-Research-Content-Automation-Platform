import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.errors.exceptions import AgentFlowError
from src.utils.loggers import get_logger, log_event


logger = get_logger(__name__)


class ErrorDetails(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetails
    request_id: str


async def agentflow_exception_handler(
    request: Request,
    exc: AgentFlowError,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    log_event(
        logger,
        level=logging.ERROR,
        request_id=request_id,
        event="agentflow_error",
        error_code=exc.code.value,
        error_message=exc.message,
        path=request.url.path,
        context=exc.context,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code.value,
                "message": exc.message,
            },
            "request_id": request_id,
        },
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    logger.exception(
        "Unhandled AgentFlow exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "event": "unhandled_exception",
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected internal error occurred.",
            },
            "request_id": request_id,
        },
    )