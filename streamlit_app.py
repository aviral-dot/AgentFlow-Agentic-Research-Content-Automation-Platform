# import time
# import uuid

# import requests
# import streamlit as st




# FASTAPI_URL = "http://localhost:8000"




# st.set_page_config(
#     page_title="AgentFlow AI",
#     page_icon="🤖",
#     layout="centered",
# )




# st.markdown(
#     """
#     <style>

#     .stButton > button {
#         width: 100%;
#         font-weight: bold;
#     }

#     .workflow-card {
#         padding: 10px;
#         border-radius: 8px;
#         margin-bottom: 8px;
#     }

#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# if "access_token" not in st.session_state:
#     st.session_state.access_token = None

# if "user" not in st.session_state:
#     st.session_state.user = None

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "pending_approval" not in st.session_state:
#     st.session_state.pending_approval = None

# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = str(uuid.uuid4())

# if "workflow" not in st.session_state:
#     st.session_state.workflow = None


# def login_user(
#     email: str,
#     password: str,
# ) -> bool:

#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/auth/login",
#             json={
#                 "email": email,
#                 "password": password,
#             },
#             timeout=10,
#         )

#         if response.status_code == 200:
#             result = response.json()

#             st.session_state.access_token = result[
#                 "access_token"
#             ]

#             st.session_state.user = result[
#                 "user"
#             ]

#             return True

#         if response.status_code == 401:
#             st.error(
#                 "❌ Invalid email or password."
#             )

#         else:
#             try:
#                 detail = response.json().get(
#                     "detail",
#                     "Login failed.",
#                 )
#             except ValueError:
#                 detail = "Login failed."

#             st.error(
#                 f"❌ {detail}"
#             )

#         return False

#     except requests.exceptions.RequestException as exc:
#         st.error(
#             f"❌ Unable to connect to the backend: {exc}"
#         )

#         return False


# def check_backend() -> bool:

#     try:

#         response = requests.get(
#             FASTAPI_URL,
#             timeout=5,
#         )

#         return response.status_code == 200

#     except requests.exceptions.RequestException:

#         return False




# def send_message(
#     query: str,
# ) -> dict:

#     try:

#         response = requests.post(
#     f"{FASTAPI_URL}/chat",
#     headers={
#         "Authorization": (
#             f"Bearer {st.session_state.access_token}"
#         ),
#     },
#     json={
#         "query": query,
#         "thread_id": st.session_state.thread_id,
#     },
#     timeout=180,
# )
 
#         if response.status_code == 401:
#          st.session_state.access_token = None
#          st.session_state.user = None
#          st.session_state.messages = []
#          st.session_state.pending_approval = None
#          st.session_state.workflow = None
#          st.rerun()

#         response.raise_for_status()

#         return response.json()

#     except requests.exceptions.RequestException as exc:

#         return {
#             "success": False,
#             "blocked": False,
#             "error": str(exc),
#         }




# def send_email_decision(
#     thread_id: str,
#     decision: str,
# ) -> dict:

#     try:

#         response = requests.post(
#             f"{FASTAPI_URL}/email/approval",
#             json={
#                 "thread_id": thread_id,
#                 "decision": decision,
#             },
#             timeout=180,
#         )

#         response.raise_for_status()

#         return response.json()

#     except requests.exceptions.RequestException as exc:

#         return {
#             "success": False,
#             "blocked": False,
#             "error": str(exc),
#         }




# def extract_workflow(
#     result: dict,
# ) -> dict:

#     data = result.get(
#         "data",
#         {},
#     )

#     return {
#         "tasks": result.get(
#             "tasks",
#             data.get(
#                 "tasks",
#                 [],
#             ),
#         ),
#         "completed_tasks": result.get(
#             "completed_tasks",
#             data.get(
#                 "completed_tasks",
#                 [],
#             ),
#         ),
#         "task_count": result.get(
#             "task_count",
#             data.get(
#                 "task_count",
#                 0,
#             ),
#         ),
#         "current_task": result.get(
#             "current_task",
#             data.get(
#                 "current_task",
#             ),
#         ),
#         "workflow_results": result.get(
#             "workflow_results",
#             data.get(
#                 "workflow_results",
#                 [],
#             ),
#         ),
#     }




# def display_workflow(
#     workflow: dict | None,
# ):

#     if not workflow:
#         return

#     tasks = workflow.get(
#         "tasks",
#         [],
#     )

#     completed_tasks = workflow.get(
#         "completed_tasks",
#         [],
#     )

#     task_count = workflow.get(
#         "task_count",
#         len(tasks),
#     )

#     current_task = workflow.get(
#         "current_task",
#     )

#     workflow_results = workflow.get(
#         "workflow_results",
#         [],
#     )

#     if not tasks:
#         return

#     with st.expander(
#         "🔎 Planner → Executor Workflow",
#         expanded=False,
#     ):

       

#         st.markdown(
#             "### 📋 Workflow Summary"
#         )

#         col1, col2, col3 = st.columns(3)

#         with col1:

#             st.metric(
#                 "Tasks",
#                 task_count,
#             )

#         with col2:

#             st.metric(
#                 "Completed",
#                 len(completed_tasks),
#             )

#         with col3:

#             if current_task:
#                 current_display = current_task
#             else:
#                 current_display = "None"

#             st.metric(
#                 "Current",
#                 current_display,
#             )

#         st.divider()

       

#         st.markdown(
#             "### 🧠 Planned Tasks"
#         )

#         for task in tasks:

#             if isinstance(
#                 task,
#                 dict,
#             ):

#                 task_id = task.get(
#                     "id",
#                     "unknown",
#                 )

#                 task_type = task.get(
#                     "type",
#                     "unknown",
#                 )

#                 description = task.get(
#                     "description",
#                     "",
#                 )

#                 depends_on = task.get(
#                     "depends_on",
#                     [],
#                 )

#                 use_blog = task.get(
#                     "use_blog",
#                     False,
#                 )

#                 status = task.get(
#                     "status",
#                     "unknown",
#                 )

#             else:

#                 task_id = getattr(
#                     task,
#                     "id",
#                     "unknown",
#                 )

#                 task_type = getattr(
#                     task,
#                     "type",
#                     "unknown",
#                 )

#                 description = getattr(
#                     task,
#                     "description",
#                     "",
#                 )

#                 depends_on = getattr(
#                     task,
#                     "depends_on",
#                     [],
#                 )

#                 use_blog = getattr(
#                     task,
#                     "use_blog",
#                     False,
#                 )

#                 status = getattr(
#                     task,
#                     "status",
#                     "unknown",
#                 )

#             status_icons = {
#                 "pending": "⏳",
#                 "running": "🔄",
#                 "completed": "✅",
#                 "rejected": "🚫",
#                 "failed": "❌",
#             }

#             icon = status_icons.get(
#                 status,
#                 "❔",
#             )

#             st.markdown(
#                 f"**{icon} {task_id} — "
#                 f"{task_type.upper()}**"
#             )

#             if description:

#                 st.caption(
#                     description
#                 )

#             if depends_on:

#                 st.caption(
#                     "🔗 Depends on: "
#                     + ", ".join(depends_on)
#                 )

#             else:

#                 st.caption(
#                     "🔗 Depends on: None"
#                 )

#             if task_type == "email":

#                 if use_blog:

#                     st.caption(
#                         "📨 Uses generated blog: Yes"
#                     )

#                 else:

#                     st.caption(
#                         "📨 Uses generated blog: No"
#                     )

#             st.caption(
#                 f"Status: `{status}`"
#             )

#             st.divider()

        

#         if workflow_results:

#             st.markdown(
#                 "### 📦 Task Results"
#             )

#             for item in workflow_results:

#                 if isinstance(
#                     item,
#                     dict,
#                 ):

#                     task_id = item.get(
#                         "task_id",
#                         "unknown",
#                     )

#                     task_type = item.get(
#                         "task_type",
#                         "unknown",
#                     )

#                     status = item.get(
#                         "status",
#                         "unknown",
#                     )

#                     result_data = item.get(
#                         "result",
#                     )

#                 else:

#                     task_id = getattr(
#                         item,
#                         "task_id",
#                         "unknown",
#                     )

#                     task_type = getattr(
#                         item,
#                         "task_type",
#                         "unknown",
#                     )

#                     status = getattr(
#                         item,
#                         "status",
#                         "unknown",
#                     )

#                     result_data = getattr(
#                         item,
#                         "result",
#                         None,
#                     )

#                 st.markdown(
#                     f"**{task_id} — "
#                     f"{task_type.upper()} — "
#                     f"`{status}`**"
#                 )

#                 if task_type == "blog" and isinstance(
#                     result_data,
#                     dict,
#                 ):

#                     title = result_data.get(
#                         "title",
#                         "",
#                     )

#                     content = result_data.get(
#                         "content",
#                         "",
#                     )

#                     if title:

#                         st.caption(
#                             f"Title: {title}"
#                         )

#                     if content:

#                         st.caption(
#                             "Blog generated successfully."

#                         )

#                 elif task_type == "email" and isinstance(
#                     result_data,
#                     dict,
#                 ):

#                     recipient = result_data.get(
#                         "to",
#                         "",
#                     )

#                     subject = result_data.get(
#                         "subject",
#                         "",
#                     )

#                     if recipient:

#                         st.caption(
#                             f"To: {recipient}"
#                         )

#                     if subject:

#                         st.caption(
#                             f"Subject: {subject}"
#                         )

#                 st.divider()


# if not st.session_state.access_token:

#     st.title("🔐 AgentFlow AI")

#     st.markdown(
#         "### Login"
#     )

#     st.caption(
#         "Sign in to access your AgentFlow workspace."
#     )

#     with st.form("login_form"):

#         email = st.text_input(
#             "Email",
#             placeholder="you@example.com",
#         )

#         password = st.text_input(
#             "Password",
#             type="password",
#             placeholder="Enter your password",
#         )

#         login_clicked = st.form_submit_button(
#             "🔐 Login",
#             use_container_width=True,
#         )

#     if login_clicked:

#         if not email or not password:

#             st.error(
#                 "❌ Please enter your email and password."
#             )

#         else:

#             with st.spinner(
#                 "Authenticating..."
#             ):

#                 if login_user(
#                     email,
#                     password,
#                 ):
#                     st.success(
#                         "✅ Login successful."
#                     )

#                     st.rerun()

#     st.stop()

# with st.sidebar:

#     st.title(
#         "⚙️ AgentFlow"
#     )

   

#     if check_backend():

#         st.success(
#             "🟢 FastAPI Connected"
#         )

#     else:

#         st.error(
#             "🔴 FastAPI Offline"
#         )

   

#     st.markdown("---")

#     st.markdown(
#         "### Architecture"
#     )

#     st.markdown(
#         """
#         **User Request**
#         ↓

#         **FastAPI**
#         ↓

#         **Input Guardrail**
#         ↓

#         **Workflow Planner**
#         ↓

#         **Dependency Graph**
#         ↓

#         **Workflow Executor**
#         ↓

#         **Blog / Email Worker**
#         ↓

#         **Task Result**
#         ↓

#         **Next Ready Task**
#         ↓

#         **Human Approval**
#         ↓

#         **Gmail**
#         """
#     )

    

#     st.markdown("---")

#     st.markdown(
#         "### Supported Workflows"
#     )

#     st.markdown(
#         """
#         **📝 Blog only**

#         Generate a brief blog about a topic.

#         **📧 Email only**

#         Generate and send an email.

#         **📝 + 📧 Independent**

#         Generate a blog and send an unrelated email.

#         **📝 → 📧 Dependent**

#         Generate a blog and email the generated blog.
#         """
#     )

   

#     st.markdown("---")

#     st.caption(
#         "Conversation ID"
#     )

#     st.code(
#         st.session_state.thread_id,
#         language=None,
#     )

   

#     st.markdown("---")

#     if st.button(
#         "🗑️ New Conversation",
#         use_container_width=True,
#     ):

#         st.session_state.messages = []

#         st.session_state.pending_approval = None

#         st.session_state.workflow = None

#         st.session_state.thread_id = str(
#             uuid.uuid4()
#         )

#         st.rerun()


#     st.markdown("---")

#     st.caption(
#         f"Signed in as: {st.session_state.user['email']}"
#     )

#     if st.button(
#         "🚪 Logout",
#         use_container_width=True,
#     ):

#         st.session_state.access_token = None

#         st.session_state.user = None

#         st.session_state.messages = []

#         st.session_state.pending_approval = None

#         st.session_state.workflow = None

#         st.session_state.thread_id = str(
#             uuid.uuid4()
#         )

#         st.rerun()




# st.title(
#     "🤖 AgentFlow AI"
# )

# st.markdown(
#     "Planner–Executor automation for "
#     "**brief blog generation and email communication.**"
# )

# st.markdown("---")



# for message in st.session_state.messages:

#     with st.chat_message(
#         message["role"]
#     ):

#         st.markdown(
#             message["content"]
#         )




# display_workflow(
#     st.session_state.workflow
# )




# if st.session_state.pending_approval:

#     approval_data = (
#         st.session_state.pending_approval
#     )

#     approval = approval_data.get(
#         "approval",
#         {},
#     )

#     email = approval.get(
#         "email",
#         {},
#     )

#     thread_id = approval_data.get(
#         "thread_id",
#         st.session_state.thread_id,
#     )

#     st.markdown("---")

#     st.warning(
#         "⚠️ Human approval required before sending this email."
#     )

#     st.markdown(
#         "### 📧 Email Preview"
#     )

#     st.markdown(
#         f"**To:** `{email.get('to', '')}`"
#     )

#     st.markdown(
#         f"**Subject:** {email.get('subject', '')}"
#     )

#     st.markdown(
#         "**Body:**"
#     )

#     st.text_area(
#         "Email Body",
#         value=email.get(
#             "body",
#             "",
#         ),
#         height=250,
#         disabled=True,
#         label_visibility="collapsed",
#     )

#     st.caption(
#         "Review the email carefully before approving."
#     )

#     st.markdown("---")

#     col1, col2 = st.columns(2)

    

#     with col1:

#         approve_clicked = st.button(
#             "✅ Approve & Send",
#             key=f"approve_{thread_id}",
#             use_container_width=True,
#         )

    
#     with col2:

#         reject_clicked = st.button(
#             "❌ Reject",
#             key=f"reject_{thread_id}",
#             use_container_width=True,
#         )

   

#     if approve_clicked:

#         with st.spinner(
#             "Sending approved email..."
#         ):

#             decision_result = (
#                 send_email_decision(
#                     thread_id,
#                     "approve",
#                 )
#             )

#         if decision_result.get(
#             "success"
#         ):

#             st.session_state.pending_approval = None

#             st.session_state.workflow = extract_workflow(
#                 decision_result
#             )

#             st.session_state.messages.append(
#                 {
#                     "role": "assistant",
#                     "content": (
#                         "✅ **Email approved and "
#                         "sent successfully.**"
#                     ),
#                 }
#             )

#             st.success(
#                 "Email approved and sent successfully."
#             )

#             st.rerun()

#         else:

#             error_message = decision_result.get(
#                 "error",
#                 decision_result.get(
#                     "message",
#                     "Failed to approve the email.",
#                 ),
#             )

#             st.error(
#                 f"❌ {error_message}"
#             )

   
#     if reject_clicked:

#         with st.spinner(
#             "Rejecting email..."
#         ):

#             decision_result = (
#                 send_email_decision(
#                     thread_id,
#                     "reject",
#                 )
#             )

#         if decision_result.get(
#             "success"
#         ):

#             st.session_state.pending_approval = None

#             st.session_state.workflow = extract_workflow(
#                 decision_result
#             )

#             st.session_state.messages.append(
#                 {
#                     "role": "assistant",
#                     "content": (
#                         "❌ **Email rejected. "
#                         "Nothing was sent.**"
#                     ),
#                 }
#             )

#             st.info(
#                 "Email rejected. Nothing was sent."
#             )

#             st.rerun()

#         else:

#             error_message = decision_result.get(
#                 "error",
#                 decision_result.get(
#                     "message",
#                     "Failed to reject the email.",
#                 ),
#             )

#             st.error(
#                 f"❌ {error_message}"
#             )




# query = st.chat_input(
#     "e.g. Generate a brief blog about AI agents..."
# )




# if query:

    

#     if st.session_state.pending_approval:

#         st.warning(
#             "⚠️ Please approve or reject the pending email first."
#         )

#         st.stop()

    

#     st.session_state.messages.append(
#         {
#             "role": "user",
#             "content": query,
#         }
#     )

    

#     with st.chat_message(
#         "user"
#     ):

#         st.markdown(
#             query
#         )

   

#     with st.chat_message(
#         "assistant"
#     ):

#         start_time = time.time()

#         with st.spinner(
#             "🤔 Planning and executing..."
#         ):

#             result = send_message(
#                 query
#             )

#         elapsed_time = (
#             time.time() - start_time
#         )

        

#         workflow = extract_workflow(
#             result
#         )

#         st.session_state.workflow = workflow

       
#         if result.get(
#             "error"
#         ):

#             answer = (
#                 "❌ **Unable to connect "
#                 "to the backend.**\n\n"
#                 f"`{result['error']}`"
#             )

#             st.error(
#                 answer
#             )

        

#         elif result.get(
#             "blocked"
#         ):

#             stage = result.get(
#                 "stage",
#                 "security",
#             )

#             reason = result.get(
#                 "reason",
#                 "Request blocked by security guardrail.",
#             )

#             if stage == "input":

#                 answer = (
#                     "🛡️ **Request blocked**\n\n"
#                     "Your request was blocked by "
#                     "the **input security guardrail**."
#                 )

#             elif stage == "output":

#                 answer = (
#                     "🛡️ **Response blocked**\n\n"
#                     "The generated response was blocked "
#                     "by the **output security guardrail**."
#                 )

#             else:

#                 answer = (
#                     "🛡️ **Request blocked**\n\n"
#                     f"{reason}"
#                 )

#             st.warning(
#                 answer
#             )

#             st.caption(
#                 f"Security stage: `{stage}` • "
#                 f"Response time: "
#                 f"`{elapsed_time:.2f}s`"
#             )

       

#         elif (
#             result.get("success")
#             and result.get("status")
#             == "approval_required"
#         ):

#             st.session_state.pending_approval = result

#             approval = result.get(
#                 "approval",
#                 {},
#             )

#             email = approval.get(
#                 "email",
#                 {},
#             )

#             answer = (
#                 "⚠️ **Email generated successfully. "
#                 "Human approval is required "
#                 "before sending.**"
#             )

#             st.warning(
#                 answer
#             )

#             if email:

#                 st.info(
#                     f"📧 Email prepared for "
#                     f"`{email.get('to', '')}`"
#                 )

#             st.caption(
#                 "👤 Human approval required • "
#                 f"⏱️ Response time: "
#                 f"`{elapsed_time:.2f}s`"
#             )

       

#         elif result.get(
#             "success"
#         ):

#             data = result.get(
#                 "data",
#                 {},
#             )

#             answer = data.get(
#                 "response",
#                 "Request completed successfully.",
#             )

#             completed_tasks = workflow.get(
#                 "completed_tasks",
#                 [],
#             )

#             task_count = workflow.get(
#                 "task_count",
#                 0,
#             )

#             st.markdown(
#                 answer
#             )

#             st.caption(
#                 f"✅ Completed "
#                 f"{len(completed_tasks)} "
#                 f"of {task_count} tasks"
#             )

#             st.caption(
#                 "🤖 Planner → Executor • "
#                 f"⏱️ Response time: "
#                 f"`{elapsed_time:.2f}s`"
#             )

        
#         else:

#             answer = (
#                 "⚠️ **Unexpected response "
#                 "from backend.**"
#             )

#             st.warning(
#                 answer
#             )

    

#     st.session_state.messages.append(
#         {
#             "role": "assistant",
#             "content": answer,
#         }
#     )

    

#     if (
#         result.get("status")
#         == "approval_required"
#     ):

#         st.rerun()


import time
import uuid

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

FASTAPI_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AgentFlow — Orchestration Console",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# ------------------------------------------------------------
# Subject: a console for operators who dispatch and supervise
# AI agent workflows — closer to a build/deploy log or a
# mission-control panel than a marketing site. The palette and
# type system below are built around that: monospace for
# anything that is data (ids, counts, status), a plain humanist
# sans for anything that is prose. Status color is the only
# color language in the UI — amber means "needs you", blue
# means "in progress", green means "done", red means "stopped".
#
# NOTE ON MARKUP: every HTML string below is left-flush (no
# leading indentation on content lines). Streamlit's markdown
# renderer treats 4+ leading spaces as a code fence, which is
# what caused raw tags to print on screen previously — this is
# the actual fix, not just a restyle.
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #15140f;
  --bg-raised: #1b1a14;
  --surface: #201f18;
  --surface-hover: #262419;
  --border: #34322a;
  --border-strong: #4a4738;

  --text: #ece8db;
  --text-dim: #a6a290;
  --muted: #726f60;

  --accent: #e8a33d;
  --accent-soft: rgba(232, 163, 61, 0.13);
  --success: #6fa287;
  --success-soft: rgba(111, 162, 135, 0.13);
  --info: #6c93a8;
  --info-soft: rgba(108, 147, 168, 0.13);
  --danger: #c2695a;
  --danger-soft: rgba(194, 105, 90, 0.13);

  --sans: 'IBM Plex Sans', -apple-system, sans-serif;
  --mono: 'IBM Plex Mono', 'SFMono-Regular', monospace;

  --r-sm: 4px;
  --r-md: 8px;
}

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
header { background: transparent !important; }

html, body, .stApp { background: var(--bg); color: var(--text); font-family: var(--sans); }
.stApp { background-image: none; }

.block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 6rem; }

h1, h2, h3, h4, h5, h6 { font-family: var(--sans); color: var(--text); }
p, span, div, label { font-family: var(--sans); }

::selection { background: var(--accent-soft); color: var(--text); }

/* ---------------- sidebar ---------------- */

[data-testid="stSidebar"] {
  background: var(--bg-raised);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.75rem; }

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 26px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.brand-mark {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-strong);
  border-radius: var(--r-sm);
  font-family: var(--mono);
  font-weight: 600;
  font-size: 13px;
  color: var(--accent);
  background: var(--surface);
}
.brand-name { font-weight: 600; font-size: 15px; color: var(--text); line-height: 1.2; }
.brand-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 1px; }

.rail-heading {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
  margin: 4px 0 10px 0;
}

.status-line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
  font-size: 12px;
  color: var(--text-dim);
  padding: 9px 11px;
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  background: var(--surface);
}
.status-line.ok { color: var(--success); border-color: rgba(111,162,135,0.3); }
.status-line.err { color: var(--danger); border-color: rgba(194,105,90,0.3); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

.capability { padding: 9px 0; border-bottom: 1px solid var(--border); }
.capability:last-child { border-bottom: none; }
.capability-name { font-size: 13px; font-weight: 600; color: var(--text); }
.capability-desc { font-size: 12px; color: var(--muted); margin-top: 2px; line-height: 1.5; }

.flow-line {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--text-dim);
  padding: 5px 0 5px 14px;
  border-left: 1px solid var(--border);
  margin-left: 3px;
}
.flow-line.terminal { color: var(--muted); }

/* ---------------- header / hero ---------------- */

.console-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 22px;
  margin-bottom: 22px;
  border-bottom: 1px solid var(--border);
}
.console-title {
  font-size: 27px;
  font-weight: 600;
  letter-spacing: -0.3px;
  color: var(--text);
  margin: 0;
}
.console-desc {
  max-width: 560px;
  margin-top: 9px;
  color: var(--text-dim);
  font-size: 14px;
  line-height: 1.6;
}

/* ---------------- stepper ---------------- */

.stepper {
  display: flex;
  align-items: center;
  margin-bottom: 26px;
  overflow-x: auto;
}
.step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 2px;
  white-space: nowrap;
}
.step-index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-size: 10px;
  color: var(--muted);
  flex-shrink: 0;
}
.step.is-active .step-index { border-color: var(--accent); color: var(--accent); }
.step-label { font-size: 12.5px; color: var(--muted); }
.step.is-active .step-label { color: var(--text); font-weight: 500; }
.step-connector { width: 28px; height: 1px; background: var(--border); margin: 0 4px; flex-shrink: 0; }

/* ---------------- stat strip ---------------- */

.stat-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  overflow: hidden;
  margin-bottom: 22px;
}
.stat {
  padding: 14px 16px;
  border-right: 1px solid var(--border);
  background: var(--surface);
}
.stat:last-child { border-right: none; }
.stat-label { font-size: 11px; color: var(--muted); }
.stat-value {
  font-family: var(--mono);
  font-size: 21px;
  font-weight: 600;
  color: var(--text);
  margin-top: 3px;
  font-variant-numeric: tabular-nums;
}
.stat-value.accent { color: var(--accent); }

.panel-heading {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-dim);
  margin: 4px 0 10px 0;
}

/* ---------------- task rows ---------------- */

.task-row {
  border: 1px solid var(--border);
  border-left: 3px solid var(--border-strong);
  border-radius: var(--r-sm);
  padding: 13px 15px;
  margin-bottom: 8px;
  background: var(--surface);
}
.task-row.status-running { border-left-color: var(--info); }
.task-row.status-completed { border-left-color: var(--success); }
.task-row.status-pending { border-left-color: var(--accent); }
.task-row.status-failed, .task-row.status-rejected { border-left-color: var(--danger); }

.task-row-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.task-id { font-family: var(--mono); font-size: 13px; font-weight: 600; color: var(--text); }
.task-type { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-left: 9px; }
.task-desc { font-size: 13px; color: var(--text-dim); line-height: 1.55; margin: 8px 0 0 0; }
.task-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 9px; }
.task-meta span:not(:last-child)::after { content: '  /  '; color: var(--border-strong); }

.tag {
  display: inline-block;
  font-family: var(--mono);
  font-size: 10.5px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: var(--r-sm);
  border: 1px solid transparent;
}
.tag-completed { color: var(--success); background: var(--success-soft); border-color: rgba(111,162,135,0.25); }
.tag-running { color: var(--info); background: var(--info-soft); border-color: rgba(108,147,168,0.25); }
.tag-pending { color: var(--accent); background: var(--accent-soft); border-color: rgba(232,163,61,0.25); }
.tag-failed, .tag-rejected { color: var(--danger); background: var(--danger-soft); border-color: rgba(194,105,90,0.25); }

/* ---------------- results ---------------- */

.result-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  padding: 11px 14px;
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  margin-top: 7px;
  background: var(--bg-raised);
}
.result-title { font-size: 13px; color: var(--text); }
.result-title span { color: var(--success); font-family: var(--mono); margin-right: 6px; }
.result-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); flex-shrink: 0; }

/* ---------------- approval ---------------- */

.approval-panel {
  border: 1px solid rgba(232, 163, 61, 0.35);
  border-radius: var(--r-md);
  padding: 20px;
  background: var(--accent-soft);
}
.approval-title { font-size: 15px; font-weight: 600; color: var(--text); }
.approval-desc { font-size: 13px; color: var(--text-dim); margin-top: 5px; line-height: 1.6; max-width: 640px; }
.approval-field-label { font-family: var(--mono); font-size: 10.5px; color: var(--muted); margin-top: 15px; }
.approval-field-value { font-size: 13.5px; color: var(--text); margin-top: 2px; }

/* ---------------- empty state ---------------- */

.empty {
  padding: 52px 10px 28px 10px;
  border: 1px dashed var(--border);
  border-radius: var(--r-md);
  text-align: left;
}
.empty-title { font-size: 18px; font-weight: 600; color: var(--text); }
.empty-desc { max-width: 520px; margin-top: 8px; color: var(--text-dim); font-size: 13.5px; line-height: 1.65; }

/* ---------------- chat ---------------- */

[data-testid="stChatMessage"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 13px 15px;
}
[data-testid="stChatMessage"] p { line-height: 1.65; font-size: 14px; }

[data-testid="stChatInput"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--r-md) !important;
}
[data-testid="stChatInput"] > div:focus-within { border-color: var(--accent) !important; }
[data-testid="stChatInput"] textarea { color: var(--text) !important; font-family: var(--sans) !important; }

/* ---------------- buttons / inputs ---------------- */

.stButton > button {
  width: 100%;
  min-height: 40px;
  border-radius: var(--r-sm) !important;
  border: 1px solid var(--border-strong) !important;
  background: var(--surface) !important;
  color: var(--text) !important;
  font-family: var(--sans) !important;
  font-weight: 500 !important;
  font-size: 13.5px !important;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.stButton > button:hover { border-color: var(--accent) !important; background: var(--surface-hover) !important; }

.stButton > button[kind="primaryFormSubmit"],
div[data-testid="stFormSubmitButton"] button {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #17140b !important;
  font-weight: 600 !important;
}
div[data-testid="stFormSubmitButton"] button:hover { opacity: 0.92; }

input, textarea { border-radius: var(--r-sm) !important; font-family: var(--sans) !important; }
div[data-baseweb="input"] { background: var(--surface) !important; border-color: var(--border) !important; }

[data-testid="stExpander"] { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); }

hr { border-color: var(--border) !important; }

code, .stCode, [data-testid="stCodeBlock"] { font-family: var(--mono) !important; }

@media (max-width: 900px) {
  .stat-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .stat:nth-child(2) { border-right: none; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "workflow" not in st.session_state:
    st.session_state.workflow = None


# ============================================================
# API FUNCTIONS
# ============================================================

def login_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{FASTAPI_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            result = response.json()
            st.session_state.access_token = result["access_token"]
            st.session_state.user = result["user"]
            return True
        if response.status_code == 401:
            st.error("Invalid email or password.")
        else:
            try:
                detail = response.json().get("detail", "Login failed.")
            except ValueError:
                detail = "Login failed."
            st.error(detail)
        return False
    except requests.exceptions.RequestException as exc:
        st.error(f"Unable to reach the backend: {exc}")
        return False


def check_backend() -> bool:
    try:
        response = requests.get(FASTAPI_URL, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def send_message(query: str) -> dict:
    try:
        response = requests.post(
            f"{FASTAPI_URL}/chat",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json={"query": query, "thread_id": st.session_state.thread_id},
            timeout=180,
        )
        if response.status_code == 401:
            st.session_state.access_token = None
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.pending_approval = None
            st.session_state.workflow = None
            st.rerun()
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"success": False, "blocked": False, "error": str(exc)}


def send_email_decision(thread_id: str, decision: str) -> dict:
    try:
        response = requests.post(
            f"{FASTAPI_URL}/email/approval",
            json={"thread_id": thread_id, "decision": decision},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"success": False, "blocked": False, "error": str(exc)}


# ============================================================
# DATA HELPERS
# ============================================================

def extract_workflow(result: dict) -> dict:
    data = result.get("data", {})
    return {
        "tasks": result.get("tasks", data.get("tasks", [])),
        "completed_tasks": result.get("completed_tasks", data.get("completed_tasks", [])),
        "task_count": result.get("task_count", data.get("task_count", 0)),
        "current_task": result.get("current_task", data.get("current_task")),
        "workflow_results": result.get("workflow_results", data.get("workflow_results", [])),
    }


def get_task_value(task, key, default=None):
    if isinstance(task, dict):
        return task.get(key, default)
    return getattr(task, key, default)


def esc(value) -> str:
    """Minimal HTML escaping for values interpolated into markup."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ============================================================
# UI COMPONENTS
# ============================================================

def render_brand():
    st.markdown("""
<div class="brand">
<div class="brand-mark">AF</div>
<div>
<div class="brand-name">AgentFlow</div>
<div class="brand-sub">orchestration console</div>
</div>
</div>
""", unsafe_allow_html=True)


def render_stepper():
    steps = [
        ("1", "Planner", True),
        ("2", "Executor", True),
        ("3", "Tasks", True),
        ("4", "Approval", False),
        ("5", "Delivery", False),
    ]
    parts = ['<div class="stepper">']
    for i, (index, label, active) in enumerate(steps):
        cls = "step is-active" if active else "step"
        parts.append(f'<div class="{cls}"><span class="step-index">{index}</span><span class="step-label">{label}</span></div>')
        if i < len(steps) - 1:
            parts.append('<div class="step-connector"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_empty_state():
    st.markdown("""
<div class="empty">
<div class="empty-title">No workflow running yet</div>
<div class="empty-desc">Describe what you want done in plain language. The planner breaks it into tasks, the executor runs them in dependency order, and anything leaving the system — like an email — waits for your sign-off below.</div>
</div>
""", unsafe_allow_html=True)


STATUS_TAG = {
    "pending": ("tag-pending", "Queued"),
    "running": ("tag-running", "Running"),
    "completed": ("tag-completed", "Completed"),
    "rejected": ("tag-rejected", "Rejected"),
    "failed": ("tag-failed", "Failed"),
}


def render_task_row(task):
    task_id = esc(get_task_value(task, "id", "unknown"))
    task_type = esc(get_task_value(task, "type", "unknown")).lower()
    description = esc(get_task_value(task, "description", ""))
    depends_on = get_task_value(task, "depends_on", [])
    use_blog = get_task_value(task, "use_blog", False)
    status = str(get_task_value(task, "status", "unknown")).lower()

    tag_class, tag_text = STATUS_TAG.get(status, ("tag-pending", status.title() or "Unknown"))
    dependency_text = esc(", ".join(depends_on)) if depends_on else "none"
    blog_text = "uses generated blog" if use_blog else "independent input"

    st.markdown(f"""
<div class="task-row status-{status}">
<div class="task-row-top">
<div><span class="task-id">{task_id}</span><span class="task-type">{task_type}</span></div>
<span class="tag {tag_class}">{tag_text}</span>
</div>
<p class="task-desc">{description}</p>
<div class="task-meta"><span>depends on {dependency_text}</span><span>{blog_text}</span></div>
</div>
""", unsafe_allow_html=True)


def render_workflow_results(workflow_results):
    if not workflow_results:
        return

    st.markdown('<div class="panel-heading">Output</div>', unsafe_allow_html=True)

    for item in workflow_results:
        task_id = esc(get_task_value(item, "task_id", "unknown"))
        task_type = get_task_value(item, "task_type", "unknown")
        status = get_task_value(item, "status", "unknown")
        result_data = get_task_value(item, "result", None)

        if task_type == "blog" and isinstance(result_data, dict):
            title = result_data.get("title", "Blog generated")
            meta = "content generated"
        elif task_type == "email" and isinstance(result_data, dict):
            recipient = result_data.get("to", "")
            subject = result_data.get("subject", "")
            title = subject if subject else "Email prepared"
            meta = f"to {recipient}" if recipient else "prepared"
        else:
            title = f"{str(task_type).lower()} result"
            meta = f"status: {status}"

        st.markdown(f"""
<div class="result-row">
<div class="result-title"><span>✓</span>{esc(title)}<span style="color:var(--muted); margin-left:8px;">{esc(task_id)}</span></div>
<div class="result-meta">{esc(meta)}</div>
</div>
""", unsafe_allow_html=True)


def display_workflow(workflow):
    if not workflow:
        return

    tasks = workflow.get("tasks", [])
    if not tasks:
        return

    completed_tasks = workflow.get("completed_tasks", [])
    task_count = workflow.get("task_count", len(tasks))
    current_task = workflow.get("current_task")
    workflow_results = workflow.get("workflow_results", [])
    completed_count = len(completed_tasks)

    if completed_count >= task_count and task_count:
        workflow_status = ("ok", "Complete")
    elif current_task:
        workflow_status = ("", "In progress")
    else:
        workflow_status = ("", "Ready")

    progress_pct = round(completed_count / task_count * 100) if task_count else 0

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown('<div class="panel-heading">Execution</div>', unsafe_allow_html=True)
    with top_right:
        status_class, status_text = workflow_status
        st.markdown(
            f'<div class="status-line {status_class}" style="justify-content:center;">'
            f'<span class="status-dot"></span>{status_text}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f"""
<div class="stat-strip">
<div class="stat"><div class="stat-label">Tasks</div><div class="stat-value">{task_count}</div></div>
<div class="stat"><div class="stat-label">Completed</div><div class="stat-value">{completed_count}</div></div>
<div class="stat"><div class="stat-label">Current</div><div class="stat-value accent" style="font-size:14px;">{esc(current_task) if current_task else "—"}</div></div>
<div class="stat"><div class="stat-label">Progress</div><div class="stat-value">{progress_pct}%</div></div>
</div>
""", unsafe_allow_html=True)

    for task in tasks:
        render_task_row(task)

    render_workflow_results(workflow_results)


def render_approval():
    if not st.session_state.pending_approval:
        return

    approval_data = st.session_state.pending_approval
    approval = approval_data.get("approval", {})
    email = approval.get("email", {})
    thread_id = approval_data.get("thread_id", st.session_state.thread_id)

    st.markdown(f"""
<div class="approval-panel">
<div class="approval-title">Authorization needed</div>
<div class="approval-desc">AgentFlow drafted an email that will leave the system. Review it below — nothing sends until you approve it.</div>
<div class="approval-field-label">To</div>
<div class="approval-field-value">{esc(email.get("to", "—"))}</div>
<div class="approval-field-label">Subject</div>
<div class="approval-field-value">{esc(email.get("subject", "—"))}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")

    st.text_area(
        "Generated email",
        value=email.get("body", ""),
        height=220,
        disabled=True,
        label_visibility="collapsed",
    )

    approve_col, reject_col = st.columns(2)
    with approve_col:
        approve_clicked = st.button("Approve and send", key=f"approve_{thread_id}", use_container_width=True)
    with reject_col:
        reject_clicked = st.button("Reject", key=f"reject_{thread_id}", use_container_width=True)

    if approve_clicked:
        with st.spinner("Sending approved email..."):
            decision_result = send_email_decision(thread_id, "approve")
        if decision_result.get("success"):
            st.session_state.pending_approval = None
            st.session_state.workflow = extract_workflow(decision_result)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Email approved and sent.",
            })
            st.rerun()
        else:
            st.error(decision_result.get("error", decision_result.get("message", "Failed to approve the email.")))

    if reject_clicked:
        with st.spinner("Rejecting email..."):
            decision_result = send_email_decision(thread_id, "reject")
        if decision_result.get("success"):
            st.session_state.pending_approval = None
            st.session_state.workflow = extract_workflow(decision_result)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Email rejected. Nothing was sent.",
            })
            st.rerun()
        else:
            st.error(decision_result.get("error", decision_result.get("message", "Failed to reject the email.")))


def render_sidebar():
    with st.sidebar:
        render_brand()

        backend_up = check_backend()
        if backend_up:
            st.markdown(
                '<div class="status-line ok"><span class="status-dot"></span>Backend connected</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-line err"><span class="status-dot"></span>Backend unreachable</div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        if st.button("New workflow", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_approval = None
            st.session_state.workflow = None
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

        st.markdown('<div class="rail-heading">Capabilities</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="capability"><div class="capability-name">Blog generation</div><div class="capability-desc">Drafts short structured posts from a topic.</div></div>
<div class="capability"><div class="capability-name">Email automation</div><div class="capability-desc">Writes outbound messages for your review.</div></div>
<div class="capability"><div class="capability-name">Dependency graphs</div><div class="capability-desc">Chains tasks that rely on each other's output.</div></div>
<div class="capability"><div class="capability-name">Human approval</div><div class="capability-desc">Pauses before anything leaves the system.</div></div>
""", unsafe_allow_html=True)

        st.markdown('<div class="rail-heading" style="margin-top:20px;">Pipeline</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="flow-line">request</div>
<div class="flow-line">input guardrail</div>
<div class="flow-line">planner</div>
<div class="flow-line">dependency graph</div>
<div class="flow-line">executor</div>
<div class="flow-line">task workers</div>
<div class="flow-line">human approval</div>
<div class="flow-line terminal">gmail</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="rail-heading" style="margin-top:20px;">Session</div>', unsafe_allow_html=True)
        st.code(st.session_state.thread_id, language=None)

        user_email = (
            st.session_state.user.get("email", "Authenticated")
            if st.session_state.user
            else "Authenticated"
        )
        st.caption(user_email)

        if st.button("Log out", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.pending_approval = None
            st.session_state.workflow = None
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.access_token:

    st.markdown("""
<div style="max-width:420px; margin:64px auto 0 auto;">
<div style="display:flex; align-items:center; gap:11px; margin-bottom:30px;">
<div class="brand-mark" style="width:38px; height:38px; font-size:14px;">AF</div>
<div>
<div style="font-weight:600; font-size:17px; color:var(--text);">AgentFlow</div>
<div style="font-family:var(--mono); font-size:11.5px; color:var(--muted); margin-top:1px;">orchestration console</div>
</div>
</div>
<div style="color:var(--text-dim); font-size:13.5px; line-height:1.6; margin-bottom:28px;">Sign in to plan, execute and approve automated workflows.</div>
</div>
""", unsafe_allow_html=True)

    _, login_center, _ = st.columns([1, 1.3, 1])

    with login_center:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_clicked = st.form_submit_button("Sign in", use_container_width=True)

        if login_clicked:
            if not email or not password:
                st.error("Enter your email and password.")
            else:
                with st.spinner("Authenticating..."):
                    if login_user(email, password):
                        st.rerun()

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

render_sidebar()


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown("""
<div class="console-header" style="border-bottom:none; margin-bottom:6px; padding-bottom:0;">
<div>
<h1 class="console-title">Command your workflow</h1>
<div class="console-desc">Describe a task in plain language. AgentFlow plans it, executes it, and stops for your approval before anything leaves the system.</div>
</div>
</div>
""", unsafe_allow_html=True)

with header_right:
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if check_backend():
        st.markdown(
            '<div class="status-line ok"><span class="status-dot"></span>Operational</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-line err"><span class="status-dot"></span>Offline</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

render_stepper()


# ============================================================
# CHAT / EMPTY STATE
# ============================================================

if not st.session_state.messages:
    render_empty_state()

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    prompt_col1, prompt_col2, prompt_col3 = st.columns(3)

    with prompt_col1:
        if st.button("Generate a blog", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Generate a brief blog about AI agents.",
            })
            st.rerun()

    with prompt_col2:
        if st.button("Draft an email", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Create an email about AI agents.",
            })
            st.rerun()

    with prompt_col3:
        if st.button("Blog, then email", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Generate a brief blog about AI agents and email the generated blog.",
            })
            st.rerun()

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ============================================================
# MESSAGE HISTORY
# ============================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# WORKFLOW + APPROVAL
# ============================================================

display_workflow(st.session_state.workflow)
render_approval()


# ============================================================
# CHAT INPUT
# ============================================================

query = st.chat_input("Ask AgentFlow to research, create or automate...")


# ============================================================
# QUERY EXECUTION
# ============================================================

if query:

    if st.session_state.pending_approval:
        st.warning("Approve or reject the pending email first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        start_time = time.time()

        with st.spinner("Planning and executing..."):
            result = send_message(query)

        elapsed_time = time.time() - start_time
        workflow = extract_workflow(result)
        st.session_state.workflow = workflow

        if result.get("error"):
            answer = f"**Couldn't reach the workflow backend.**\n\n`{result['error']}`"
            st.error(answer)

        elif result.get("blocked"):
            stage = result.get("stage", "security")
            reason = result.get("reason", "Request blocked by a security guardrail.")

            if stage == "input":
                answer = "**Request blocked.** The input guardrail stopped this request before it ran."
            elif stage == "output":
                answer = "**Response blocked.** The output guardrail stopped the generated response."
            else:
                answer = f"**Request blocked.**\n\n{reason}"

            st.warning(answer)
            st.caption(f"stage: {stage} · {elapsed_time:.2f}s")

        elif result.get("success") and result.get("status") == "approval_required":
            st.session_state.pending_approval = result
            approval = result.get("approval", {})
            email = approval.get("email", {})

            answer = "**Paused for approval.** AgentFlow prepared the email and is waiting on your decision before it sends."
            st.warning(answer)

            if email:
                st.caption(f"prepared for {email.get('to', '')} · {elapsed_time:.2f}s")

        elif result.get("success"):
            data = result.get("data", {})
            answer = data.get("response", "Workflow completed.")

            completed_tasks = workflow.get("completed_tasks", [])
            task_count = workflow.get("task_count", 0)

            st.markdown(answer)
            st.caption(f"{len(completed_tasks)} / {task_count} tasks completed · {elapsed_time:.2f}s")

        else:
            answer = "**Unexpected response from AgentFlow.**"
            st.warning(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    if result.get("status") == "approval_required":
        st.rerun()