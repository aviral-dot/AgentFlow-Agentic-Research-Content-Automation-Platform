# AgentFlow — Agentic Research, Content & Communication Automation

> **AgentFlow** is a planner-executor AI automation platform built with **LangGraph, FastAPI, PostgreSQL, LiteLLM, MCP, NeMo Guardrails, Tavily, Gmail, Streamlit, and DeepEval**.
>
> Instead of sending every request directly to one LLM, AgentFlow converts a natural-language request into a validated workflow, schedules dependent tasks, executes specialized workers, persists workflow state, applies security guardrails, and pauses for explicit human approval before external email actions.

[View the AgentFlow repository](https://github.com/aviral-dot/AgentFlow-Agentic-Research-Content-Automation-Platform?utm_source=chatgpt.com)

---

## Overview

AgentFlow is designed around a simple idea:

```text
Natural Language Request
          │
          ▼
   Workflow Planner
          │
          ▼
Dependency Validation
          │
          ▼
 Task Scheduler / Executor
          │
     ┌────┼─────────────┐
     │    │             │
     ▼    ▼             ▼
 Research Blog        Email
     │    │             │
     │    │        Human Approval
     │    │             │
     │    │          ┌──┴──┐
     │    │       Reject  Approve
     │    │                 │
     │    │                 ▼
     │    │             Gmail MCP
     │    │                 │
     │    │                 ▼
     │    │             Gmail API
     │    │
     └────┴──────────────┐
                         ▼
                  Workflow Results
                         │
                         ▼
                   Output Safety
                         │
                         ▼
                       User
```

The system separates:

* Workflow planning
* Dependency validation
* Task scheduling
* Agent execution
* LLM infrastructure
* External tools
* Human authorization
* Security guardrails
* Persistence
* Authentication
* Observability
* Evaluation
* Frontend presentation

---

# Architecture

AgentFlow currently uses a **planner-executor architecture**, rather than a fixed supervisor that directly chooses one agent.

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Streamlit UI     │
                         └──────────┬──────────┘
                                    │ HTTP
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI API      │
                         │  Authentication     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Input Guardrails  │
                         │     NeMo / NVIDIA   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   LangGraph Graph   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Workflow Planner   │
                         │ Structured Output   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Dependency Validator│
                         │  Cycle Detection   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Workflow Executor   │
                         │ + Task Scheduler    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              Research Worker  Blog Worker   Email Worker
                    │               │               │
                    ▼               ▼               ▼
                 Tavily          LLM         Human Approval
                                                    │
                                              ┌─────┴─────┐
                                              │           │
                                           Reject      Approve
                                              │           │
                                              ▼           ▼
                                             END      Gmail MCP
                                                         │
                                                         ▼
                                                     Gmail API
                                                         │
                                                         ▼
                                              External Side Effect
```

---

# Core Workflow Model

The planner generates structured tasks rather than directly selecting an agent.

A task contains:

```text
id
type
description
depends_on
use_blog
status
result
```

Supported task types:

```text
research
blog
email
```

Example workflow:

```text
task_1: research
        depends_on: []

        ↓

task_2: blog
        depends_on: [task_1]

        ↓

task_3: email
        depends_on: [task_2]
        use_blog: true
```

This allows AgentFlow to represent workflows such as:

### Research

```text
research
```

### Research → Blog

```text
research → blog
```

### Blog → Email

```text
blog → email
```

### Research → Blog → Email

```text
research → blog → email
```

### Independent tasks

```text
research
   │
   └──────────────┐
                  ▼
                email
```

The scheduler can identify multiple ready tasks when their dependencies are satisfied.

---

# Workflow Planner

The `WorkflowPlanner` converts a natural-language request into a structured executable workflow.

The planner uses Pydantic structured output and validates the resulting workflow before execution.

## Planner responsibilities

* Determine required task types
* Create task IDs
* Define dependencies
* Decide whether an email consumes a generated blog
* Avoid unnecessary tasks
* Reject invalid task combinations
* Detect circular dependencies

The planner explicitly constrains the supported workflow model.

For example:

```text
User:

"Research AI agents, write a blog about the findings,
and email the blog to Rahul."

Planner:

task_1
type = research
depends_on = []

task_2
type = blog
depends_on = ["task_1"]

task_3
type = email
depends_on = ["task_2"]
use_blog = true
```

---

# Dependency Validation

Generated workflows are validated before execution.

AgentFlow checks for:

### Duplicate task IDs

```text
task_1
task_1
```

→ rejected.

### Missing dependencies

```text
task_2 depends_on task_99
```

→ rejected.

### Self-dependencies

```text
task_1 depends_on task_1
```

→ rejected.

### Invalid dependency types

For example, a blog task cannot directly depend on an email task.

### Invalid email workflows

An email task using:

```text
use_blog = true
```

must depend on a blog task.

### Circular dependencies

The planner performs DFS-based cycle detection.

Example:

```text
task_1 → task_2
task_2 → task_1
```

→ rejected before execution.

---

# Dependency-Aware Task Scheduler

The `TaskScheduler` is responsible for deciding which tasks are ready to execute.

It does not:

* Call an LLM
* Search the web
* Generate blogs
* Send emails
* Modify task state

Instead, it answers questions such as:

```text
Which tasks are ready?
Are all dependencies satisfied?
Is the workflow complete?
Did a task fail?
Is the workflow deadlocked?
```

A task becomes executable when:

```text
status == pending
```

and:

```text
all dependencies ∈ completed_tasks
```

---

# Workflow Executor

The `WorkflowExecutor` manages task lifecycle transitions.

Tasks move through states such as:

```text
pending
   │
   ▼
running
   │
   ├───────────┐
   ▼           ▼
completed    failed
```

Email approval can additionally produce:

```text
running
   │
   ▼
rejected
```

The executor maintains:

* `tasks`
* `current_task`
* `completed_tasks`
* `running_tasks`
* `task_results`
* `workflow_results`

This keeps workflow state separate from the actual business logic performed by the workers.

---

# LangGraph Workflow

The current LangGraph graph contains:

```text
START
  │
  ▼
Planner
  │
  ▼
Executor
  │
  ├───────────────┐
  │               │
  ▼               ▼
Research         Blog
  │               │
  └───────┬───────┘
          │
          ▼
        Advance
          │
          ▼
       Executor
```

Email follows a separate approval path:

```text
Executor
   │
   ▼
Draft Email
   │
   ▼
Human Approval
   │
   ├───────────────┐
   │               │
 Reject          Approve
   │               │
   ▼               ▼
 Advance        Send Email
                   │
                   ▼
                Advance
                   │
                   ▼
                Executor
```

This creates a reusable workflow loop:

```text
Planner
   ↓
Executor
   ↓
Worker
   ↓
Advance
   ↓
Executor
   ↓
Worker
   ↓
...
```

---

# Research Agent

The Research Agent separates external search from research synthesis.

```text
Research Task
     │
     ▼
ResearchTool
     │
     ▼
Tavily
     │
     ▼
Search Results
     │
     ▼
Source Ranking
     │
     ▼
Top Evidence
     │
     ▼
Structured LLM Synthesis
     │
     ▼
Compact Research Artifact
```

## Tavily integration

The research tool uses the asynchronous Tavily client.

The current implementation:

* Uses advanced search
* Requests up to 5 search results
* Requests Tavily's answer field
* Extracts title, URL, content and score
* Ranks sources using their search score
* Passes only the strongest sources into the synthesis step

The synthesis stage intentionally keeps the context compact.

Current limits include:

```text
Maximum search sources:       5
Sources sent to synthesis:    2
Characters/source:          1000
Maximum query length:         400
Maximum key findings:           3
Maximum summary words:         70
```

The resulting research artifact contains:

```json
{
  "query": "...",
  "summary": "...",
  "key_findings": [
    "...",
    "...",
    "..."
  ]
}
```

The research node intentionally does not pass raw URLs into the synthesized downstream artifact.

---

# Blog Agent

The current Blog Agent uses **one structured LLM generation step**.

It is no longer the old:

```text
Title Generation
      ↓
Content Generation
```

implementation.

The current flow is:

```text
Blog Task
    │
    ▼
Research Context
    │
    ▼
Structured LLM
    │
    ▼
Blog
 ┌─────────────┐
 │ title       │
 │ content     │
 └─────────────┘
```

The blog output is represented by:

```python
class Blog(BaseModel):
    title: str
    content: str
```

The generated content is constrained to:

* Markdown
* Concise structure
* Professional writing
* SEO-friendly title
* 250–500 words
* No unnecessary repetition
* No discussion of internal agents/workflow
* No unsupported factual claims when research is supplied

The blog node can also consume research context from an earlier workflow task.

---

# Email Agent

The Email Agent converts a natural-language email request into a validated structured draft.

Example:

```text
Send Rahul an email about tomorrow's meeting.
```

becomes:

```json
{
  "to": "rahul@example.com",
  "subject": "Tomorrow's Meeting",
  "body": "..."
}
```

The email schema uses Pydantic validation:

```python
class EmailDraft(BaseModel):
    to: EmailStr
    subject: str
    body: str
```

Current constraints include:

```text
Valid email address required
Subject: 1–200 characters
Body: 1–10,000 characters
```

The LLM therefore does not directly control the external Gmail API.

---

# Human-in-the-Loop Email Authorization

Email sending is treated as an external side effect.

AgentFlow therefore introduces an explicit approval boundary:

```text
User Request
     │
     ▼
Email Draft
     │
     ▼
Structured Validation
     │
     ▼
LangGraph interrupt()
     │
     ▼
Human Decision
     │
 ┌───┴────┐
 ▼        ▼
Reject   Approve
 │        │
 ▼        ▼
END    Send Email
```

The approval payload contains:

```text
Recipient
Subject
Body
```

The graph pauses using LangGraph's:

```python
interrupt(...)
```

The workflow can later be resumed using:

```python
Command(resume=decision)
```

Supported decisions:

```text
approve
reject
```

If rejected:

```text
No email is sent.
```

---

# MCP Gmail Integration

AgentFlow isolates Gmail operations behind the **Model Context Protocol (MCP)**.

```text
EmailNode
    │
    ▼
EmailTool
    │
    ▼
MCP Client
    │
    │ stdio
    ▼
gmail_mcp_server.py
    │
    ▼
Gmail API
```

The MCP server exposes:

```text
send_email
```

with:

```text
to
subject
body
```

The server creates a MIME message, encodes it using URL-safe Base64, and sends it using the Gmail API.

This keeps:

```text
Agent workflow
```

separate from:

```text
Gmail implementation details
```

---

# Gmail OAuth

Gmail authentication uses Google's OAuth flow.

Required files:

```text
credentials.json
token.json
```

Authentication is initiated with:

```bash
python gmail_auth.py
```

The application requests:

```text
https://www.googleapis.com/auth/gmail.send
```

The resulting OAuth token is stored locally in:

```text
token.json
```

These credentials must never be committed to Git.

---

# Centralized LLM Gateway

AgentFlow does not make every worker responsible for selecting a model provider.

Instead:

```text
Worker
   │
   ▼
LLM Gateway
   │
   ▼
LiteLLM Router
   │
   ├──────────────┐
   ▼              ▼
Primary        Fallback
Model           Model
```

The `LLMGateway` provides:

* Centralized model configuration
* LiteLLM routing
* Primary model selection
* Optional fallback
* Retry configuration
* Timeout configuration
* Routing strategy
* Cached LangChain-compatible LLM instances

Agents obtain their LLM through:

```python
LLMGateway.get_llm(...)
```

rather than directly depending on a provider.

---

# LLM Configuration

Example:

```env
PRIMARY_LLM_MODEL=groq/openai/gpt-oss-20b
FALLBACK_LLM_MODEL=gemini/gemini-3.7-flash

LLM_ROUTING_STRATEGY=simple-shuffle
LLM_NUM_RETRIES=2
LLM_TIMEOUT=60
```

The current gateway:

```text
Primary:
Groq

Optional fallback:
Gemini

Routing:
LiteLLM Router

Retries:
Configurable

Timeout:
Configurable

Client cache:
Enabled in gateway implementation
```

The primary Groq credential is required by the current configuration.

---

# AI Safety Architecture

AgentFlow applies security at multiple layers.

```text
                  USER
                    │
                    ▼
             Input Guardrail
                    │
                    ▼
             Workflow Planner
                    │
                    ▼
             Agent Execution
                    │
                    ▼
             External Tools
                    │
                    ▼
             Workflow Result
                    │
                    ▼
             Output Guardrail
                    │
                    ▼
                  USER
```

---

# Input Guardrails

The input layer uses **NeMo Guardrails**.

It is designed to identify unsafe or unsupported requests before they enter the workflow.

The guardrail configuration covers categories such as:

* Harmful activity
* Violence
* Weapons-related harmful requests
* Controlled substances
* Self-harm
* Sexual safety categories
* Hate/identity-based violence
* Threats
* Harassment
* Privacy abuse
* Criminal planning
* Jailbreak attempts
* Prompt extraction
* Credential extraction
* Security bypass attempts
* Internal tool manipulation
* Unsupported topics

The guardrail layer is designed to fail closed:

```text
Guardrail succeeds
      │
      ▼
Continue

Guardrail rejects
      │
      ▼
Block

Guardrail fails
      │
      ▼
Block
```

---

# Jailbreak Protection

The guardrail prompts also address attempts to:

```text
Extract system prompts
Extract hidden instructions
Obtain credentials
Disable safety controls
Override internal policies
Manipulate internal tools
Bypass guardrails
```

This creates a dedicated security layer before workflow planning.

---

# Output Safety

Generated application responses are checked separately.

The current implementation calls:

```text
nvidia/llama-3.1-nemotron-safety-guard-8b-v3
```

through NVIDIA's API.

The flow is:

```text
Generated Output
      │
      ▼
NVIDIA Safety Model
      │
 ┌────┴────┐
 ▼         ▼
safe     unsafe
 │         │
 ▼         ▼
return    block
```

Output guardrail failures are also handled fail-closed.

This means a failed safety verification does not silently allow the generated response through.

---

# Authentication

The current backend includes authentication infrastructure.

```text
Register
   │
   ▼
Argon2 Password Hash
   │
   ▼
PostgreSQL
```

and:

```text
Login
  │
  ▼
Password Verification
  │
  ▼
JWT Access Token
  │
  ▼
Authenticated API Request
```

The implementation includes:

* User registration
* User login
* JWT access tokens
* Active-user validation
* Argon2 password hashing
* Bearer authentication
* User lookup through PostgreSQL

JWT configuration requires:

```env
JWT_SECRET_KEY=...
```

The current implementation requires the JWT secret to contain at least 32 characters.

---

# User-Scoped Workflow Threads

The `/chat` endpoint requires authentication.

The client supplies a thread identifier:

```text
client_thread_id
```

The backend scopes it using the authenticated user:

```text
<user_id>:<client_thread_id>
```

This allows LangGraph checkpoint state to be separated between users.

---

# PostgreSQL Persistence

AgentFlow currently uses **PostgreSQL-backed LangGraph checkpointing**.

This is implemented through:

```python
AsyncPostgresSaver
```

At application startup:

```text
FastAPI startup
      │
      ▼
DATABASE_URL
      │
      ▼
AsyncPostgresSaver
      │
      ▼
saver.setup()
      │
      ▼
GraphBuilder
      │
      ▼
Compiled LangGraph
```

This allows workflow state and interrupted execution state to persist through the LangGraph checkpoint mechanism.

The project therefore no longer treats persistent checkpointing as a future feature.

---

# Docker PostgreSQL

The repository includes a PostgreSQL Docker Compose service.

```yaml
postgres:
  image: postgres:16
```

Start PostgreSQL with:

```bash
docker compose up -d postgres
```

The service exposes:

```text
localhost:5432
```

with the development database configuration defined in `docker-compose.yml`.

For production deployments, credentials should be replaced with secure environment-managed secrets.

---

# FastAPI Backend

FastAPI provides the application API.

## Health endpoint

```http
GET /
```

Returns information about the running architecture and enabled workflow workers.

---

## Authentication

### Register

```http
POST /auth/register
```

Example:

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

### Login

```http
POST /auth/login
```

Returns:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "user@example.com",
    "is_active": true
  }
}
```

---

## Chat

```http
POST /chat
```

Authenticated request:

```json
{
  "query": "Research AI agents and create a blog",
  "thread_id": "my-thread"
}
```

The request passes through:

```text
Authentication
      ↓
Input Validation
      ↓
Input Guardrails
      ↓
LangGraph
      ↓
Planner
      ↓
Executor
      ↓
Workers
      ↓
Output Safety
      ↓
Response
```

---

## Email Approval

```http
POST /email/approval
```

Request:

```json
{
  "thread_id": "user-thread-id",
  "decision": "approve"
}
```

or:

```json
{
  "thread_id": "user-thread-id",
  "decision": "reject"
}
```

The endpoint resumes the persisted LangGraph execution using:

```python
Command(resume=decision)
```

> **Production security note:** the current approval endpoint should be hardened with explicit authentication and thread-ownership validation before exposing it to an untrusted network. The `/chat` path already authenticates and user-scopes workflow threads.

---

# Request ID & Structured Logging

The FastAPI application generates or propagates an:

```text
X-Request-ID
```

for each request.

The identifier is returned in the response headers and propagated through workflow logging.

The application also uses structured event logging for events such as:

```text
application_startup
graph_execution_started
workflow_plan_created
workflow_task_selected
research_started
research_completed
blog_generation_started
blog_generation_completed
email_approval_requested
graph_resume_started
graph_resume_completed
guardrail_passed
guardrail_blocked
```

Sensitive email contents and API credentials are intentionally not logged by the email tool.

---

# LangSmith Observability

AgentFlow integrates LangSmith tracing through `@traceable`.

Traced operations include components such as:

```text
workflow planner
research agent
Tavily search
blog agent
Gmail tool
input guardrail
output guardrail
```

LangSmith can therefore be used to inspect:

* Workflow execution
* LLM calls
* Tool calls
* Latency
* Failures
* Agent traces
* Retrieval/search operations

Configuration:

```env
LANGCHAIN_API_KEY=your_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentFlow
```

---

# Error Handling

The project contains a dedicated error taxonomy.

Examples include:

```text
LLMFailure
ResearchFailure
GmailFailure
DatabaseFailure
PlannerFailure
InvalidWorkflowError
ExecutorFailure
UnknownTaskError
WorkflowDeadlockError
GuardrailRejection
GuardrailFailure
HITLTimeoutError
```

This prevents every failure from becoming a generic exception.

FastAPI also registers application-level exception handlers for:

```text
AgentFlowError
Exception
```

---

# Streamlit Frontend

The Streamlit frontend acts as the AgentFlow orchestration console.

The current UI provides:

* Authentication
* Backend connectivity status
* Chat-based workflow execution
* Workflow task visualization
* Task status
* Workflow results
* Response timing
* Guardrail notifications
* Email approval UI
* Email rejection
* Conversation history
* Clear-chat functionality
* Responsive operator-console styling

The UI communicates with FastAPI through HTTP.

---

# Frontend Workflow

```text
User
 │
 ▼
Streamlit Chat
 │
 ▼
POST /chat
 │
 ▼
FastAPI
 │
 ▼
LangGraph
 │
 ▼
Workflow Result
 │
 ├───────────────┐
 │               │
 ▼               ▼
Completed     Approval Required
                 │
                 ▼
          Email Preview
                 │
          ┌──────┴──────┐
          ▼             ▼
       Reject         Approve
          │             │
          ▼             ▼
         END        POST /email/approval
```

The interface exposes the workflow state instead of behaving like a black-box chatbot.

---

# Evaluation & Testing

The repository contains multiple layers of tests and evaluations.

```text
tests/
├── unit/
├── integration/
└── evals/
```

---

## Unit Tests

Unit coverage includes components such as:

```text
BlogNode
ResearchNode
ResearchTool
EmailNode
TaskScheduler
GraphBuilder
LLM Gateway
Gateway Configuration
Guardrails
PostgreSQL
Blog State
```

---

# Integration Tests

Integration coverage includes workflows such as:

```text
Full workflow
Planner → Executor workflow
Research workflow
Blog workflow
Email workflow
Email approval / interrupt flow
```

The email approval path specifically tests the LangGraph interrupt/resume lifecycle.

---

# LLM Evaluation

The repository contains DeepEval-based evaluation suites for:

```text
Planner
Research
Blog
Email
MCP
End-to-End workflow
Agent trajectory
```

The evaluation structure includes:

```text
tests/evals/
│
├── component_eval/
│   ├── test_blog_eval.py
│   ├── test_email_eval.py
│   ├── test_planner_eval.py
│   └── test_research_eval.py
│
├── E2E_eval/
│
├── trajectory_evals/
│
├── mcp/
│
├── datasets/
│
├── metrics/
└── helpers/
```

This is intended to evaluate more than simple string equality.

The project evaluates characteristics such as:

* Relevance
* Content quality
* Workflow correctness
* Planner behavior
* Research quality
* Email quality
* Tool behavior
* Agent trajectory

---

# Project Structure

The current repository is organized approximately as follows:

```text
AgentFlow-Agentic-Research-Content-Automation-Platform/
│
├── app.py
├── streamlit_app.py
├── gmail_auth.py
├── gmail_mcp_server.py
├── langgraph.json
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── uv.lock
│
├── scripts/
│   ├── create_auth_user.py
│   └── init_auth_db.py
│
├── src/
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── password.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── service.py
│   │   └── user_repository.py
│   │
│   ├── database/
│   │   └── postgres.py
│   │
│   ├── errors/
│   │   ├── codes.py
│   │   ├── exceptions.py
│   │   └── handlers.py
│   │
│   ├── executors/
│   │   ├── task_scheduler.py
│   │   └── workflow_executor.py
│   │
│   ├── gateway/
│   │   ├── config.py
│   │   └── llm_gateway.py
│   │
│   ├── graphs/
│   │   ├── graph.py
│   │   └── graph_builder.py
│   │
│   ├── guardrails/
│   │   ├── config.yml
│   │   ├── guardrail.py
│   │   └── prompts.yml
│   │
│   ├── HITL_middleware/
│   │   └── mail_approval_human_in_the_loop.py
│   │
│   ├── llms/
│   │
│   ├── nodes/
│   │   ├── blog_node.py
│   │   ├── mail_node.py
│   │   └── research_node.py
│   │
│   ├── planners/
│   │   └── workflow_planner.py
│   │
│   ├── states/
│   │   └── blogstate.py
│   │
│   ├── tools/
│   │   ├── email_tool.py
│   │   └── research_tool.py
│   │
│   └── utils/
│       └── loggers.py
│
├── tests/
│   │
│   ├── unit/
│   ├── integration/
│   └── evals/
│       ├── component_eval/
│       ├── E2E_eval/
│       ├── trajectory_evals/
│       ├── mcp/
│       ├── datasets/
│       ├── metrics/
│       └── helpers/
│
└── .github/
    └── workflows/
```

---

# Technology Stack

| Technology              | Role                                              |
| ----------------------- | ------------------------------------------------- |
| **Python**              | Application language                              |
| **LangGraph**           | Stateful workflow orchestration                   |
| **LangChain**           | LLM/agent abstractions                            |
| **LiteLLM**             | Model routing, retries and fallback               |
| **Groq**                | Primary LLM provider                              |
| **Gemini**              | Optional fallback provider                        |
| **FastAPI**             | Backend API                                       |
| **Streamlit**           | Frontend / orchestration console                  |
| **PostgreSQL**          | Authentication + LangGraph checkpoint persistence |
| **Pydantic**            | Structured validation                             |
| **Tavily**              | Web research                                      |
| **MCP**                 | Gmail tool isolation                              |
| **Gmail API**           | Email delivery                                    |
| **Google OAuth**        | Gmail authorization                               |
| **NeMo Guardrails**     | Input safety and policy controls                  |
| **NVIDIA Safety Guard** | Output safety                                     |
| **LangSmith**           | LLM/workflow observability                        |
| **DeepEval**            | LLM evaluation                                    |
| **PyJWT**               | JWT authentication                                |
| **pwdlib / Argon2**     | Password hashing                                  |
| **Docker Compose**      | Local PostgreSQL infrastructure                   |
| **uv**                  | Dependency/environment management                 |
| **Uvicorn**             | ASGI server                                       |

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/aviral-dot/AgentFlow-Agentic-Research-Content-Automation-Platform.git

cd AgentFlow-Agentic-Research-Content-Automation-Platform
```

---

## 2. Install dependencies

Using `uv`:

```bash
uv sync
```

Or using a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

Then install:

```bash
pip install -r requirements.txt
```

The project currently targets:

```text
Python >= 3.13
```

---

# Environment Variables

Create:

```text
.env
```

Example:

```env
# ============================================================
# LLM
# ============================================================

GROQ_API_KEY=your_groq_api_key

# Optional fallback
GEMINI_API_KEY=your_gemini_api_key

PRIMARY_LLM_MODEL=groq/openai/gpt-oss-20b
FALLBACK_LLM_MODEL=gemini/gemini-3.7-flash

LLM_ROUTING_STRATEGY=simple-shuffle
LLM_NUM_RETRIES=2
LLM_TIMEOUT=60


# ============================================================
# NVIDIA SAFETY
# ============================================================

NVIDIA_API_KEY=your_nvidia_api_key


# ============================================================
# RESEARCH
# ============================================================

TAVILY_API_KEY=your_tavily_api_key


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL=postgresql://agentflow:agentflow_password@localhost:5432/agentflow


# ============================================================
# AUTHENTICATION
# ============================================================

JWT_SECRET_KEY=your-long-random-secret-at-least-32-characters


# ============================================================
# LANGSMITH
# ============================================================

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentFlow


# ============================================================
# APPLICATION
# ============================================================

ENVIRONMENT=development
```

Do not commit:

```text
.env
credentials.json
token.json
```

---

# Start PostgreSQL

The easiest local setup is:

```bash
docker compose up -d postgres
```

Check the container:

```bash
docker ps
```

The database should be available on:

```text
localhost:5432
```

---

# Initialize Authentication Database

The repository includes authentication database initialization scripts.

```bash
python scripts/init_auth_db.py
```

A user can be created with:

```bash
python scripts/create_auth_user.py
```

---

# Configure Gmail

Create Gmail OAuth credentials through Google Cloud and save them as:

```text
credentials.json
```

Then run:

```bash
python gmail_auth.py
```

This creates:

```text
token.json
```

The application uses the Gmail:

```text
gmail.send
```

scope.

---

# Run the Backend

Start FastAPI:

```bash
python app.py
```

Or:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# Run the Frontend

In another terminal:

```bash
streamlit run streamlit_app.py
```

Frontend:

```text
http://localhost:8501
```

---

# Example Requests

## Research

```text
Research the latest developments in AI agents.
```

AgentFlow can create:

```text
Planner
   ↓
Research Task
   ↓
Tavily
   ↓
Research Synthesis
```

---

## Blog

```text
Write a professional blog about RAG systems.
```

The planner creates a blog workflow:

```text
Planner
   ↓
Blog Task
   ↓
Blog Agent
   ↓
Structured Blog
```

---

## Research + Blog

```text
Research AI agents and then write a blog based on the findings.
```

Workflow:

```text
Research
   ↓
Blog
```

---

## Email

```text
Send Rahul an email saying the meeting has been moved to tomorrow.
```

Workflow:

```text
Planner
   ↓
Email Draft
   ↓
Human Approval
   ↓
Approve
   ↓
MCP
   ↓
Gmail
```

---

## Blog + Email

```text
Create a blog about AI agents and email it to Rahul.
```

Workflow:

```text
Blog
   ↓
Email
   ↓
Human Approval
   ↓
Gmail
```

---

# Design Principles

## 1. Plan before execution

The system does not blindly execute every request.

The planner first creates a structured workflow.

---

## 2. Validate before running

Generated workflows are validated for:

```text
Invalid dependencies
Duplicate IDs
Unsupported task combinations
Self-dependencies
Cycles
```

---

## 3. Separate orchestration from business logic

The executor controls:

```text
task lifecycle
```

while worker nodes control:

```text
research
blog generation
email generation
email delivery
```

---

## 4. Structured LLM outputs

Critical LLM decisions use structured schemas.

Examples:

```text
WorkflowPlan
EmailDraft
Blog
ResearchSynthesis
```

This reduces reliance on arbitrary free-form model output.

---

## 5. External side effects require human approval

Sending an email is not treated as an ordinary generation step.

The workflow pauses before the side effect.

```text
LLM-generated email
       ↓
Human approval
       ↓
External action
```

---

## 6. Centralized model infrastructure

Workers do not need to know whether the underlying model comes from:

```text
Groq
Gemini
OpenAI-compatible APIs
```

The gateway abstracts model routing.

---

## 7. Defense in depth

Security does not rely on one model.

AgentFlow combines:

```text
Authentication
      +
Input Guardrails
      +
Jailbreak Protection
      +
Structured Validation
      +
Human Approval
      +
Output Safety
      +
Error Handling
```

---

## 8. Persist workflow state

LangGraph execution state is persisted through PostgreSQL checkpointing.

This is especially important for interrupted human-in-the-loop workflows.

---

## 9. Evaluate AI behavior

The repository includes DeepEval suites for multiple parts of the system instead of relying exclusively on manual inspection.

---

# Current Implementation Status

| Component                            | Status                       |
| ------------------------------------ | ---------------------------- |
| Planner-executor architecture        | ✅ Implemented                |
| Structured workflow planning         | ✅ Implemented                |
| Dependency validation                | ✅ Implemented                |
| Cycle detection                      | ✅ Implemented                |
| Dependency-aware scheduler           | ✅ Implemented                |
| Deadlock detection                   | ✅ Implemented                |
| Research worker                      | ✅ Implemented                |
| Tavily integration                   | ✅ Implemented                |
| Blog worker                          | ✅ Implemented                |
| Structured blog output               | ✅ Implemented                |
| Email worker                         | ✅ Implemented                |
| Structured email output              | ✅ Implemented                |
| Gmail MCP integration                | ✅ Implemented                |
| Gmail OAuth                          | ✅ Implemented                |
| Human-in-the-loop approval           | ✅ Implemented                |
| PostgreSQL LangGraph checkpointing   | ✅ Implemented                |
| User authentication                  | ✅ Implemented                |
| JWT authorization for `/chat`        | ✅ Implemented                |
| Argon2 password hashing              | ✅ Implemented                |
| LLM Gateway                          | ✅ Implemented                |
| LiteLLM routing                      | ✅ Implemented                |
| Optional model fallback              | ✅ Implemented                |
| NeMo input guardrails                | ✅ Implemented                |
| NVIDIA output safety                 | ✅ Implemented                |
| LangSmith tracing                    | ✅ Implemented                |
| Structured application logging       | ✅ Implemented                |
| Unit tests                           | ✅ Implemented                |
| Integration tests                    | ✅ Implemented                |
| DeepEval component evaluations       | ✅ Implemented                |
| E2E evaluation infrastructure        | ✅ Implemented                |
| Trajectory evaluation                | ✅ Implemented                |
| MCP evaluation                       | ✅ Implemented                |
| Distributed rate limiting            | 🚧 Not currently implemented |
| Redis production cache               | 🚧 Not currently implemented |
| Prometheus/Grafana metrics           | 🚧 Not currently implemented |
| Full production container deployment | 🚧 Not currently implemented |

---

# Known Engineering Considerations

AgentFlow is deliberately positioned as a **production-oriented AI engineering project**, but it should not be represented as a fully hardened production SaaS platform yet.

### Email approval authorization

The current `/email/approval` endpoint validates the thread ID and decision but does not currently enforce the same bearer authentication and user-ownership checks used by `/chat`.

Before public deployment, approval requests should be authenticated and the thread should be verified as belonging to the authenticated user.

### Research → Blog state contract

The current research worker produces:

```text
query
summary
key_findings
```

while the blog context adapter still contains legacy lookups for fields such as:

```text
topic
key_points
sources
```

This contract should be unified before relying on research-backed blog generation as a production-critical path.

### Streamlit legacy code

`streamlit_app.py` currently contains a substantial amount of older commented-out UI code alongside the active console implementation.

Removing obsolete commented implementations would reduce maintenance overhead and make the frontend easier to understand.

### Evaluation status

The repository contains extensive evaluation infrastructure, but the presence of evaluation files should not be interpreted as proof that every evaluation currently passes. Evaluation results should be regenerated against the current code before publishing numerical claims.

---

# Production Hardening Roadmap

## Security

* [ ] Authenticate `/email/approval`
* [ ] Validate thread ownership before resuming workflows
* [ ] Introduce per-user Gmail credentials
* [ ] Add tool-level authorization
* [ ] Add secret-management integration
* [ ] Add audit logs for external side effects
* [ ] Add CSRF/session hardening where appropriate

---

## Reliability

* [ ] Add idempotency protection for email sends
* [ ] Add explicit workflow cancellation
* [ ] Add configurable task timeouts
* [ ] Add retry policies per worker
* [ ] Improve interrupted-workflow recovery
* [ ] Add stronger state/schema contract validation
* [ ] Add regression tests for research → blog composition

---

## Performance

* [ ] Add distributed caching
* [ ] Add request rate limiting
* [ ] Add connection pooling
* [ ] Add background execution for long workflows
* [ ] Track model token usage
* [ ] Track model/provider costs

---

## Observability

* [x] Structured application logging
* [x] Request IDs
* [x] LangSmith tracing
* [ ] Prometheus metrics
* [ ] Grafana dashboards
* [ ] Centralized error tracking
* [ ] Per-workflow latency dashboards
* [ ] Token/cost dashboards

---

## Evaluation

* [x] Planner evaluation
* [x] Research evaluation
* [x] Blog evaluation
* [x] Email evaluation
* [x] MCP evaluation
* [x] Trajectory evaluation
* [x] E2E evaluation infrastructure
* [ ] Guardrail benchmark suite
* [ ] Prompt-injection regression suite
* [ ] CI evaluation gates
* [ ] Automated regression reporting

---

## Deployment

* [ ] Production application Docker image
* [ ] Production Docker Compose/Kubernetes configuration
* [ ] HTTPS
* [ ] Readiness probes
* [ ] Liveness probes
* [ ] Managed PostgreSQL
* [ ] Secret manager
* [ ] CI/CD
* [ ] Automated database migrations
* [ ] Production domain configuration

---

# Why AgentFlow Is More Than a Chatbot

AgentFlow demonstrates several important AI engineering patterns in one system:

```text
                    AI ENGINEERING
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   Orchestration     LLM Infra       AI Safety
        │                │                │
        ▼                ▼                ▼
   LangGraph          LiteLLM       NeMo/NVIDIA
        │                │                │
        └────────────┬───┴────────────────┘
                     │
                     ▼
              Tool Integration
                     │
                MCP + Gmail
                     │
                     ▼
             Human Authorization
                     │
                     ▼
                Persistence
                     │
                 PostgreSQL
                     │
                     ▼
                Evaluation
                     │
                 DeepEval
```

The project demonstrates:

* Agentic workflow orchestration
* Planner-executor architecture
* Dependency-aware scheduling
* Structured LLM outputs
* Multi-provider model routing
* LLM fallback architecture
* Async LLM execution
* Web research
* Tool isolation through MCP
* Gmail API integration
* Human-in-the-loop execution
* Stateful workflow persistence
* JWT authentication
* Argon2 password hashing
* AI safety guardrails
* Jailbreak protection
* Output moderation
* Structured error handling
* LangSmith observability
* DeepEval evaluation
* FastAPI backend engineering
* Streamlit frontend engineering

---

# Future Architecture

The long-term direction is to evolve AgentFlow from a research/content/email automation system into a broader agentic automation platform.

```text
                           USER
                            │
                            ▼
                  ┌──────────────────┐
                  │ Web / Streamlit  │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   API Gateway    │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Auth & Security  │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Workflow Planner │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Workflow Executor│
                  └────────┬─────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Research           Blog            Email
          │                │                │
          ▼                ▼                ▼
       Search           Content       Human Approval
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                       MCP Tools
                           │
                           ▼
                    External Systems
                           │
                           ▼
                    Output Safety
                           │
                           ▼
                    Observability
                           │
                           ▼
                         USER
```

Future workers can be added without fundamentally changing the planner/executor architecture.

Potential future capabilities include:

```text
Calendar Agent
CRM Agent
Slack Agent
Notion Agent
Document Agent
Data Analysis Agent
Browser Agent
Research Agent
Report Generation Agent
Customer Support Agent
```

---

# LangGraph Configuration

The repository exposes the graph through:

```text
langgraph.json
```

Current graph:

```text
blog_generator_agent
```

mapped to:

```text
src/graphs/graph.py
```

This allows the workflow graph to be integrated with LangGraph tooling.

---

# Development Commands

Install:

```bash
uv sync
```

Run tests:

```bash
pytest
```

Run a specific unit test:

```bash
pytest tests/unit/test_task_scheduler.py
```

Run integration tests:

```bash
pytest tests/integration/
```

Run evaluation tests:

```bash
pytest tests/evals/
```

Run the backend:

```bash
python app.py
```

Run Streamlit:

```bash
streamlit run streamlit_app.py
```

Run PostgreSQL:

```bash
docker compose up -d postgres
```

---

# Security Checklist

Before committing or deploying:

```text
[ ] .env is ignored
[ ] credentials.json is ignored
[ ] token.json is ignored
[ ] JWT_SECRET_KEY is strong
[ ] PostgreSQL credentials are not default
[ ] Gmail OAuth credentials are protected
[ ] NVIDIA API key is protected
[ ] Groq API key is protected
[ ] Tavily API key is protected
[ ] LangSmith key is protected
[ ] Email approval endpoint is authenticated
[ ] Thread ownership is validated
[ ] Email sending is idempotent
[ ] Production HTTPS is enabled
```

---

# Project Philosophy

AgentFlow is built around one principle:

> **LLMs should generate decisions and content, but deterministic software should control execution, validation, authorization, persistence, and external side effects.**

That principle is reflected throughout the architecture:

```text
LLM
 │
 │ generates
 ▼
Structured Output
 │
 │ validated by
 ▼
Application Logic
 │
 │ controlled by
 ▼
Workflow Executor
 │
 │ authorized by
 ▼
Human / Policy Boundary
 │
 │ executes
 ▼
External Tool
```

This makes the system easier to reason about than a single autonomous LLM loop while still providing the flexibility of agentic workflows.

---

# Author

**Aviral Bagjani**

B.Tech — Electronics & Communication Engineering
Indian Institute of Information Technology Bhagalpur

Focused on:

```text
AI Engineering
LLM Applications
Agentic Systems
RAG
LLMOps
AI Safety
Workflow Automation
```

---

# Repository

[AgentFlow — Agentic Research, Content & Communication Automation](https://github.com/aviral-dot/AgentFlow-Agentic-Research-Content-Automation-Platform?utm_source=chatgpt.com)

---

## License

Add the project's chosen license here before publishing the repository as an open-source project.

