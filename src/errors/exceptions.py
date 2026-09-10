from typing import Any

from src.errors.codes import ErrorCode


class AgentFlowError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        status_code: int = 500,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code
        self.context = context or {}


class LLMFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.LLM_FAILURE,
            "Unable to generate a response.",
            **kwargs,
        )


class ResearchFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.RESEARCH_FAILED,
            "Unable to complete research.",
            **kwargs,
        )


class GmailFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.GMAIL_FAILURE,
            "Unable to send email.",
            **kwargs,
        )


class DatabaseFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.DATABASE_FAILURE,
            "Unable to access application data.",
            **kwargs,
        )


class PlannerFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.PLANNER_FAILURE,
            "Unable to create a workflow.",
            **kwargs,
        )


class InvalidWorkflowError(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.INVALID_WORKFLOW,
            "The generated workflow is invalid.",
            status_code=422,
            **kwargs,
        )


class ExecutorFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.EXECUTOR_FAILURE,
            "Unable to execute the workflow.",
            **kwargs,
        )


class UnknownTaskError(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.UNKNOWN_TASK,
            "The workflow contains an unsupported task.",
            status_code=422,
            **kwargs,
        )


class WorkflowDeadlockError(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.WORKFLOW_DEADLOCK,
            "Unable to continue workflow execution.",
            **kwargs,
        )


class GuardrailRejection(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.GUARDRAIL_REJECTION,
            "The request was rejected by the security guardrail.",
            status_code=400,
            **kwargs,
        )


class GuardrailFailure(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.GUARDRAIL_FAILURE,
            "Unable to verify the request.",
            **kwargs,
        )


class HITLTimeoutError(AgentFlowError):
    def __init__(self, **kwargs):
        super().__init__(
            ErrorCode.HITL_TIMEOUT,
            "Human approval timed out.",
            status_code=408,
            **kwargs,
        )