import asyncio
import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from src.auth.router import router as auth_router
from src.auth.dependencies import get_current_user
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from src.gateway.llm_gateway import LLMGateway
from src.graphs.graph_builder import GraphBuilder
from src.guardrails.guardrail import (
    check_input,
    check_output,
)
from src.utils.loggers import (
    get_logger,
    log_event,
)




load_dotenv()




logger = get_logger(__name__)




llm_gateway = LLMGateway()

log_event(
    logger,
    level=logging.INFO,
    event="llm_gateway_initialized",
)

llm = llm_gateway.get_llm(
    model_name="primary",
    temperature=0.2,
)

log_event(
    logger,
    level=logging.INFO,
    event="primary_llm_initialized",
)




graph = None
checkpointer = None





@asynccontextmanager
async def lifespan(app: FastAPI):

    global graph
    global checkpointer

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:

        log_event(
            logger,
            level=logging.ERROR,
            event="application_startup_failed",
            reason="database_url_not_configured",
        )

        raise RuntimeError(
            "DATABASE_URL environment variable "
            "is not configured."
        )

    log_event(
        logger,
        level=logging.INFO,
        event="application_startup_started",
    )

    try:

        log_event(
            logger,
            level=logging.INFO,
            event="postgres_checkpointer_initialization_started",
        )

        async with AsyncPostgresSaver.from_conn_string(
            database_url
        ) as saver:

            await saver.setup()

            log_event(
                logger,
                level=logging.INFO,
                event="postgres_checkpointer_initialized",
                status="success",
            )

            checkpointer = saver

           

            graph_builder = GraphBuilder(
                llm,
                checkpointer,
            )

            graph = graph_builder.setup_graph()

            log_event(
                logger,
                level=logging.INFO,
                event="langgraph_initialized",
                persistence="postgresql",
                architecture="planner_executor",
                workers=[
                    "research",
                    "blog",
                    "email",
                ],
                tools=[
                    "tavily_search",
                    "gmail",
                ],
                status="success",
            )

            log_event(
                logger,
                level=logging.INFO,
                event="application_startup_completed",
                status="success",
            )

            yield

    except Exception:

        logger.exception(
            "Application startup failed",
            extra={
                "event": "application_startup_failed",
                "context": {},
            },
        )

        raise

    finally:

        graph = None
        checkpointer = None

        log_event(
            logger,
            level=logging.INFO,
            event="postgres_checkpointer_closed",
        )

        log_event(
            logger,
            level=logging.INFO,
            event="application_shutdown_completed",
        )




app = FastAPI(
    title="Planner-Executor Research, Blog & Email Automation API",
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)



@app.get("/")
async def root():

    return {
        "message": (
            "Planner-Executor Multi-Agent "
            "Research, Blog & Email Workflow System "
            "is running"
        ),
        "architecture": "planner-executor",
        "workers": [
            "research",
            "blog",
            "email",
        ],
        "tools": [
            "tavily_search",
            "gmail",
        ],
    }





def build_response_text(
    workflow_results,
) -> str:
    """
    Build a simple human-readable response from
    completed workflow tasks.

    Structured task results remain available through
    workflow_results.
    """

    if not workflow_results:

        return (
            "Workflow completed successfully."
        )

    messages = []

    for task_result in workflow_results:

        task_type = task_result.get(
            "task_type"
        )

        status = task_result.get(
            "status"
        )

        

        if task_type == "research":

            if status == "completed":

                result = task_result.get(
                    "result"
                )

                if isinstance(
                    result,
                    dict,
                ):

                    topic = result.get(
                        "topic"
                    )

                    if topic:

                        messages.append(
                            f"Research completed for "
                            f"'{topic}'."
                        )

                    else:

                        messages.append(
                            "Research completed successfully."
                        )

                else:

                    messages.append(
                        "Research completed successfully."
                    )

            elif status == "rejected":

                messages.append(
                    "Research task was rejected."
                )

            elif status == "failed":

                messages.append(
                    "Research task failed."
                )

       

        elif task_type == "blog":

            if status == "completed":

                messages.append(
                    "Blog generated successfully."
                )

            elif status == "rejected":

                messages.append(
                    "Blog task was rejected."
                )

            elif status == "failed":

                messages.append(
                    "Blog task failed."
                )

      

        elif task_type == "email":

            if status == "completed":

                result = task_result.get(
                    "result"
                )

                if (
                    isinstance(result, dict)
                    and result.get("status") == "sent"
                ):

                    messages.append(
                        "Email sent successfully."
                    )

                else:

                    messages.append(
                        "Email workflow completed."
                    )

            elif status == "rejected":

                messages.append(
                    "Email was rejected. "
                    "Nothing was sent."
                )

            elif status == "failed":

                messages.append(
                    "Email task failed."
                )

    if not messages:

        return (
            "Workflow completed successfully."
        )

    return " ".join(messages)





@app.post("/chat")
async def chat(
    request: Request,
    current_user: dict = Depends(get_current_user),
):

    request_id = str(
        uuid4()
    )

    request_started = perf_counter()

    thread_id = None

    log_event(
        logger,
        level=logging.INFO,
        event="chat_request_started",
        request_id=request_id,
    )

    try:

        

        data = await request.json()

        query = data.get(
            "query",
            "",
        ).strip()

        client_thread_id= data.get(
            "thread_id"
        )

        

        if not query:

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_validation_failed",
                request_id=request_id,
                reason="query_missing",
            )

            raise HTTPException(
                status_code=400,
                detail="Query is required",
            )

        if not client_thread_id:

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_validation_failed",
                request_id=request_id,
                reason="thread_id_missing",
            )

            raise HTTPException(
                status_code=400,
                detail="thread_id is required",
            )
            
        thread_id = (
            f"{current_user['id']}:{client_thread_id}"
        )

        log_event(
            logger,
            level=logging.INFO,
            event="chat_request_validated",
            request_id=request_id,
            thread_id=thread_id,
        )

       

        input_safe = await check_input(
            query
        )

        if not input_safe:

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_blocked",
                request_id=request_id,
                thread_id=thread_id,
                stage="input",
                reason="security_guardrail",
                latency_ms=latency_ms,
                status="blocked",
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "input",
                "reason": (
                    "Input blocked by "
                    "security guardrail"
                ),
            }

        
        if graph is None:

            log_event(
                logger,
                level=logging.ERROR,
                event="graph_execution_failed",
                request_id=request_id,
                thread_id=thread_id,
                reason="graph_not_initialized",
            )

            raise HTTPException(
                status_code=503,
                detail="Application is not ready",
            )

        

        environment = os.getenv(
            "ENVIRONMENT",
            "development",
        )

        config = {
            "configurable": {
                "thread_id": thread_id,
            },
            "metadata": {
                "request_id": request_id,
                "user_id": current_user["id"],
                "workflow": "planner_executor",
                "feature": "chat",
                "environment": environment,
            },
            "tags": [
                "planner-executor",
                "research",
                "blog",
                "email",
                "chat",
            ],
        }

     

        graph_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_execution_started",
            request_id=request_id,
            user_id=current_user["id"],
            thread_id=thread_id,
        )

        result = await graph.ainvoke(
            {
                "query": query,
                "request_id": request_id,
            },
            config=config,
        )

        graph_latency_ms = round(
            (
                perf_counter()
                - graph_started
            )
            * 1000,
            2,
        )

       

        tasks = result.get(
            "tasks",
            [],
        )

        completed_tasks = result.get(
            "completed_tasks",
            [],
        )

        running_tasks = result.get(
            "running_tasks",
            [],
        )

        current_task = result.get(
            "current_task"
        )

        workflow_results = result.get(
            "workflow_results",
            [],
        )

        log_event(
            logger,
            level=logging.INFO,
            event="graph_execution_completed",
            request_id=request_id,
            thread_id=thread_id,
            task_count=len(tasks),
            completed_tasks=completed_tasks,
            running_tasks=running_tasks,
            current_task=current_task,
            workflow_results=workflow_results,
            latency_ms=graph_latency_ms,
            status="success",
        )

        
        if "__interrupt__" in result:

            interrupt_data = (
                result[
                    "__interrupt__"
                ][0].value
            )

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.INFO,
                event="email_approval_requested",
                request_id=request_id,
                thread_id=thread_id,
                current_task=current_task,
                completed_tasks=completed_tasks,
                latency_ms=latency_ms,
                status="approval_required",
            )

            return {
                "success": True,
                "blocked": False,
                "status": "approval_required",
                "thread_id": thread_id,
                "approval": interrupt_data,
                "workflow_results": workflow_results,
                "completed_tasks": completed_tasks,
                "current_task": current_task,
                "task_count": len(tasks),
            }

        

        response = build_response_text(
            workflow_results
        )

        

        output_safe = await check_output(
            response
        )

        if not output_safe:

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.WARNING,
                event="chat_request_blocked",
                request_id=request_id,
                thread_id=thread_id,
                stage="output",
                reason="security_guardrail",
                latency_ms=latency_ms,
                status="blocked",
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "output",
                "reason": (
                    "Generated response blocked "
                    "by security guardrail"
                ),
            }

       

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="chat_request_completed",
            request_id=request_id,
            thread_id=thread_id,
            completed_tasks=completed_tasks,
            task_count=len(tasks),
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "success": True,
            "blocked": False,
            "status": "completed",
            "data": {
                "response": response,
                "workflow_results": workflow_results,
                "completed_tasks": completed_tasks,
                "running_tasks": running_tasks,
                "current_task": current_task,
                "task_count": len(tasks),
                "query": result.get(
                    "query"
                ),
                "thread_id": thread_id,
            },
        }

   

    except HTTPException:

        raise

    

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        logger.exception(
            "Chat request failed",
            extra={
                "event": "chat_request_failed",
                "context": {
                    "request_id": request_id,
                    "thread_id": thread_id,
                    "latency_ms": latency_ms,
                },
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )





@app.post("/email/approval")
async def email_approval(
    request: Request,
):

    request_id = str(
        uuid4()
    )

    request_started = perf_counter()

    thread_id = None

    log_event(
        logger,
        level=logging.INFO,
        event="email_approval_request_started",
        request_id=request_id,
    )

    try:

       
        data = await request.json()

        thread_id = data.get(
            "thread_id"
        )

        decision = data.get(
            "decision"
        )

       

        if not thread_id:

            log_event(
                logger,
                level=logging.WARNING,
                event="email_approval_validation_failed",
                request_id=request_id,
                reason="thread_id_missing",
            )

            raise HTTPException(
                status_code=400,
                detail="thread_id is required",
            )

        

        if decision not in {
            "approve",
            "reject",
        }:

            log_event(
                logger,
                level=logging.WARNING,
                event="email_approval_validation_failed",
                request_id=request_id,
                thread_id=thread_id,
                reason="invalid_decision",
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    "decision must be "
                    "'approve' or 'reject'"
                ),
            )

       
        if graph is None:

            log_event(
                logger,
                level=logging.ERROR,
                event="graph_resume_failed",
                request_id=request_id,
                thread_id=thread_id,
                reason="graph_not_initialized",
            )

            raise HTTPException(
                status_code=503,
                detail="Application is not ready",
            )

       

        log_event(
            logger,
            level=logging.INFO,
            event="email_approval_decision_received",
            request_id=request_id,
            thread_id=thread_id,
            decision=decision,
        )

        

        environment = os.getenv(
            "ENVIRONMENT",
            "development",
        )

        config = {
            "configurable": {
                "thread_id": thread_id,
            },
            "metadata": {
                "request_id": request_id,
                "workflow": "planner_executor",
                "feature": "email_approval",
                "environment": environment,
            },
            "tags": [
                "planner-executor",
                "email",
                "hitl",
            ],
        }

        

        resume_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_resume_started",
            request_id=request_id,
            thread_id=thread_id,
            decision=decision,
        )

        result = await graph.ainvoke(
            Command(
                resume=decision
            ),
            config=config,
        )

        resume_latency_ms = round(
            (
                perf_counter()
                - resume_started
            )
            * 1000,
            2,
        )

       

        tasks = result.get(
            "tasks",
            [],
        )

        completed_tasks = result.get(
            "completed_tasks",
            [],
        )

        running_tasks = result.get(
            "running_tasks",
            [],
        )

        current_task = result.get(
            "current_task"
        )

        workflow_results = result.get(
            "workflow_results",
            [],
        )

        log_event(
            logger,
            level=logging.INFO,
            event="graph_resume_completed",
            request_id=request_id,
            thread_id=thread_id,
            decision=decision,
            completed_tasks=completed_tasks,
            current_task=current_task,
            workflow_results=workflow_results,
            latency_ms=resume_latency_ms,
            status="success",
        )

        

        if "__interrupt__" in result:

            interrupt_data = (
                result[
                    "__interrupt__"
                ][0].value
            )

            return {
                "success": True,
                "blocked": False,
                "status": "approval_required",
                "thread_id": thread_id,
                "approval": interrupt_data,
                "workflow_results": workflow_results,
                "completed_tasks": completed_tasks,
                "current_task": current_task,
                "task_count": len(tasks),
            }

       

        if decision == "reject":

            response = build_response_text(
                workflow_results
            )

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.INFO,
                event="email_rejected",
                request_id=request_id,
                thread_id=thread_id,
                completed_tasks=completed_tasks,
                latency_ms=latency_ms,
                status="rejected",
            )

            return {
                "success": True,
                "blocked": False,
                "status": "rejected",
                "thread_id": thread_id,
                "message": (
                    "Email rejected. "
                    "Nothing was sent."
                ),
                "data": {
                    "response": response,
                    "workflow_results": workflow_results,
                    "completed_tasks": completed_tasks,
                    "task_count": len(tasks),
                },
            }

        

        log_event(
            logger,
            level=logging.INFO,
            event="email_approved",
            request_id=request_id,
            thread_id=thread_id,
        )

        

        response = build_response_text(
            workflow_results
        )



        
        output_safe = await check_output(
            response
        )

        if not output_safe:

            latency_ms = round(
                (
                    perf_counter()
                    - request_started
                )
                * 1000,
                2,
            )

            log_event(
                logger,
                level=logging.WARNING,
                event="email_approval_blocked",
                request_id=request_id,
                thread_id=thread_id,
                stage="output",
                reason="security_guardrail",
                latency_ms=latency_ms,
                status="blocked",
            )

            return {
                "success": False,
                "blocked": True,
                "stage": "output",
                "thread_id": thread_id,
                "reason": (
                    "Generated response blocked "
                    "by security guardrail"
                ),
            }

        

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="email_approval_request_completed",
            request_id=request_id,
            thread_id=thread_id,
            decision="approve",
            completed_tasks=completed_tasks,
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "success": True,
            "blocked": False,
            "status": "completed",
            "thread_id": thread_id,
            "data": {
                "response": response,
                "workflow_results": workflow_results,
                "completed_tasks": completed_tasks,
                "running_tasks": running_tasks,
                "current_task": current_task,
                "task_count": len(tasks),
            },
        }

    

    except HTTPException:

        raise

   

    except Exception:

        latency_ms = round(
            (
                perf_counter()
                - request_started
            )
            * 1000,
            2,
        )

        logger.exception(
            "Email approval request failed",
            extra={
                "event": (
                    "email_approval_request_failed"
                ),
                "context": {
                    "request_id": request_id,
                    "thread_id": thread_id,
                    "latency_ms": latency_ms,
                },
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )





if __name__ == "__main__":

    asyncio.run(
        uvicorn.Server(
            uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8000,
                loop="asyncio",
            )
        ).serve(),
        loop_factory=asyncio.SelectorEventLoop,
    )