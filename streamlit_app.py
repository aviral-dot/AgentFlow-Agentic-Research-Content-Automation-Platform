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

###################################################3


# import time
# import uuid

# import requests
# import streamlit as st


# # ============================================================
# # CONFIGURATION
# # ============================================================

# FASTAPI_URL = "http://localhost:8000"

# st.set_page_config(
#     page_title="AgentFlow — Orchestration Console",
#     page_icon="◆",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# # ============================================================
# # DESIGN SYSTEM
# # ------------------------------------------------------------
# # Subject: a console for operators who dispatch and supervise
# # AI agent workflows — closer to a build/deploy log or a
# # mission-control panel than a marketing site. The palette and
# # type system below are built around that: monospace for
# # anything that is data (ids, counts, status), a plain humanist
# # sans for anything that is prose. Status color is the only
# # color language in the UI — amber means "needs you", blue
# # means "in progress", green means "done", red means "stopped".
# #
# # NOTE ON MARKUP: every HTML string below is left-flush (no
# # leading indentation on content lines). Streamlit's markdown
# # renderer treats 4+ leading spaces as a code fence, which is
# # what caused raw tags to print on screen previously — this is
# # the actual fix, not just a restyle.
# # ============================================================

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

# :root {
#   --bg: #15140f;
#   --bg-raised: #1b1a14;
#   --surface: #201f18;
#   --surface-hover: #262419;
#   --border: #34322a;
#   --border-strong: #4a4738;

#   --text: #ece8db;
#   --text-dim: #a6a290;
#   --muted: #726f60;

#   --accent: #e8a33d;
#   --accent-soft: rgba(232, 163, 61, 0.13);
#   --success: #6fa287;
#   --success-soft: rgba(111, 162, 135, 0.13);
#   --info: #6c93a8;
#   --info-soft: rgba(108, 147, 168, 0.13);
#   --danger: #c2695a;
#   --danger-soft: rgba(194, 105, 90, 0.13);

#   --sans: 'IBM Plex Sans', -apple-system, sans-serif;
#   --mono: 'IBM Plex Mono', 'SFMono-Regular', monospace;

#   --r-sm: 4px;
#   --r-md: 8px;
# }

# #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
# header { background: transparent !important; }

# html, body, .stApp { background: var(--bg); color: var(--text); font-family: var(--sans); }
# .stApp { background-image: none; }

# .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 6rem; }

# h1, h2, h3, h4, h5, h6 { font-family: var(--sans); color: var(--text); }
# p, span, div, label { font-family: var(--sans); }

# ::selection { background: var(--accent-soft); color: var(--text); }

# /* ---------------- sidebar ---------------- */

# [data-testid="stSidebar"] {
#   background: var(--bg-raised);
#   border-right: 1px solid var(--border);
# }
# [data-testid="stSidebar"] .block-container { padding-top: 1.75rem; }

# .brand {
#   display: flex;
#   align-items: center;
#   gap: 11px;
#   margin-bottom: 26px;
#   padding-bottom: 18px;
#   border-bottom: 1px solid var(--border);
# }
# .brand-mark {
#   width: 34px;
#   height: 34px;
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   border: 1px solid var(--border-strong);
#   border-radius: var(--r-sm);
#   font-family: var(--mono);
#   font-weight: 600;
#   font-size: 13px;
#   color: var(--accent);
#   background: var(--surface);
# }
# .brand-name { font-weight: 600; font-size: 15px; color: var(--text); line-height: 1.2; }
# .brand-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 1px; }

# .rail-heading {
#   font-family: var(--mono);
#   font-size: 11px;
#   color: var(--muted);
#   margin: 4px 0 10px 0;
# }

# .status-line {
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   font-family: var(--mono);
#   font-size: 12px;
#   color: var(--text-dim);
#   padding: 9px 11px;
#   border: 1px solid var(--border);
#   border-radius: var(--r-sm);
#   background: var(--surface);
# }
# .status-line.ok { color: var(--success); border-color: rgba(111,162,135,0.3); }
# .status-line.err { color: var(--danger); border-color: rgba(194,105,90,0.3); }
# .status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

# .capability { padding: 9px 0; border-bottom: 1px solid var(--border); }
# .capability:last-child { border-bottom: none; }
# .capability-name { font-size: 13px; font-weight: 600; color: var(--text); }
# .capability-desc { font-size: 12px; color: var(--muted); margin-top: 2px; line-height: 1.5; }

# .flow-line {
#   font-family: var(--mono);
#   font-size: 12px;
#   color: var(--text-dim);
#   padding: 5px 0 5px 14px;
#   border-left: 1px solid var(--border);
#   margin-left: 3px;
# }
# .flow-line.terminal { color: var(--muted); }

# /* ---------------- header / hero ---------------- */

# .console-header {
#   display: flex;
#   align-items: flex-start;
#   justify-content: space-between;
#   gap: 20px;
#   padding-bottom: 22px;
#   margin-bottom: 22px;
#   border-bottom: 1px solid var(--border);
# }
# .console-title {
#   font-size: 27px;
#   font-weight: 600;
#   letter-spacing: -0.3px;
#   color: var(--text);
#   margin: 0;
# }
# .console-desc {
#   max-width: 560px;
#   margin-top: 9px;
#   color: var(--text-dim);
#   font-size: 14px;
#   line-height: 1.6;
# }

# /* ---------------- stepper ---------------- */

# .stepper {
#   display: flex;
#   align-items: center;
#   margin-bottom: 26px;
#   overflow-x: auto;
# }
# .step {
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   padding: 6px 2px;
#   white-space: nowrap;
# }
# .step-index {
#   width: 20px;
#   height: 20px;
#   border-radius: 50%;
#   border: 1px solid var(--border-strong);
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   font-family: var(--mono);
#   font-size: 10px;
#   color: var(--muted);
#   flex-shrink: 0;
# }
# .step.is-active .step-index { border-color: var(--accent); color: var(--accent); }
# .step-label { font-size: 12.5px; color: var(--muted); }
# .step.is-active .step-label { color: var(--text); font-weight: 500; }
# .step-connector { width: 28px; height: 1px; background: var(--border); margin: 0 4px; flex-shrink: 0; }

# /* ---------------- stat strip ---------------- */

# .stat-strip {
#   display: grid;
#   grid-template-columns: repeat(4, minmax(0, 1fr));
#   border: 1px solid var(--border);
#   border-radius: var(--r-md);
#   overflow: hidden;
#   margin-bottom: 22px;
# }
# .stat {
#   padding: 14px 16px;
#   border-right: 1px solid var(--border);
#   background: var(--surface);
# }
# .stat:last-child { border-right: none; }
# .stat-label { font-size: 11px; color: var(--muted); }
# .stat-value {
#   font-family: var(--mono);
#   font-size: 21px;
#   font-weight: 600;
#   color: var(--text);
#   margin-top: 3px;
#   font-variant-numeric: tabular-nums;
# }
# .stat-value.accent { color: var(--accent); }

# .panel-heading {
#   font-size: 13px;
#   font-weight: 600;
#   color: var(--text-dim);
#   margin: 4px 0 10px 0;
# }

# /* ---------------- task rows ---------------- */

# .task-row {
#   border: 1px solid var(--border);
#   border-left: 3px solid var(--border-strong);
#   border-radius: var(--r-sm);
#   padding: 13px 15px;
#   margin-bottom: 8px;
#   background: var(--surface);
# }
# .task-row.status-running { border-left-color: var(--info); }
# .task-row.status-completed { border-left-color: var(--success); }
# .task-row.status-pending { border-left-color: var(--accent); }
# .task-row.status-failed, .task-row.status-rejected { border-left-color: var(--danger); }

# .task-row-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
# .task-id { font-family: var(--mono); font-size: 13px; font-weight: 600; color: var(--text); }
# .task-type { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-left: 9px; }
# .task-desc { font-size: 13px; color: var(--text-dim); line-height: 1.55; margin: 8px 0 0 0; }
# .task-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 9px; }
# .task-meta span:not(:last-child)::after { content: '  /  '; color: var(--border-strong); }

# .tag {
#   display: inline-block;
#   font-family: var(--mono);
#   font-size: 10.5px;
#   font-weight: 500;
#   padding: 3px 8px;
#   border-radius: var(--r-sm);
#   border: 1px solid transparent;
# }
# .tag-completed { color: var(--success); background: var(--success-soft); border-color: rgba(111,162,135,0.25); }
# .tag-running { color: var(--info); background: var(--info-soft); border-color: rgba(108,147,168,0.25); }
# .tag-pending { color: var(--accent); background: var(--accent-soft); border-color: rgba(232,163,61,0.25); }
# .tag-failed, .tag-rejected { color: var(--danger); background: var(--danger-soft); border-color: rgba(194,105,90,0.25); }

# /* ---------------- results ---------------- */

# .result-row {
#   display: flex;
#   align-items: baseline;
#   justify-content: space-between;
#   gap: 14px;
#   padding: 11px 14px;
#   border: 1px solid var(--border);
#   border-radius: var(--r-sm);
#   margin-top: 7px;
#   background: var(--bg-raised);
# }
# .result-title { font-size: 13px; color: var(--text); }
# .result-title span { color: var(--success); font-family: var(--mono); margin-right: 6px; }
# .result-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); flex-shrink: 0; }

# /* ---------------- approval ---------------- */

# .approval-panel {
#   border: 1px solid rgba(232, 163, 61, 0.35);
#   border-radius: var(--r-md);
#   padding: 20px;
#   background: var(--accent-soft);
# }
# .approval-title { font-size: 15px; font-weight: 600; color: var(--text); }
# .approval-desc { font-size: 13px; color: var(--text-dim); margin-top: 5px; line-height: 1.6; max-width: 640px; }
# .approval-field-label { font-family: var(--mono); font-size: 10.5px; color: var(--muted); margin-top: 15px; }
# .approval-field-value { font-size: 13.5px; color: var(--text); margin-top: 2px; }

# /* ---------------- empty state ---------------- */

# .empty {
#   padding: 52px 10px 28px 10px;
#   border: 1px dashed var(--border);
#   border-radius: var(--r-md);
#   text-align: left;
# }
# .empty-title { font-size: 18px; font-weight: 600; color: var(--text); }
# .empty-desc { max-width: 520px; margin-top: 8px; color: var(--text-dim); font-size: 13.5px; line-height: 1.65; }

# /* ---------------- chat ---------------- */

# [data-testid="stChatMessage"] {
#   background: var(--surface);
#   border: 1px solid var(--border);
#   border-radius: var(--r-md);
#   padding: 13px 15px;
# }
# [data-testid="stChatMessage"] p { line-height: 1.65; font-size: 14px; }

# [data-testid="stChatInput"] > div {
#   background: var(--surface) !important;
#   border: 1px solid var(--border-strong) !important;
#   border-radius: var(--r-md) !important;
# }
# [data-testid="stChatInput"] > div:focus-within { border-color: var(--accent) !important; }
# [data-testid="stChatInput"] textarea { color: var(--text) !important; font-family: var(--sans) !important; }

# /* ---------------- buttons / inputs ---------------- */

# .stButton > button {
#   width: 100%;
#   min-height: 40px;
#   border-radius: var(--r-sm) !important;
#   border: 1px solid var(--border-strong) !important;
#   background: var(--surface) !important;
#   color: var(--text) !important;
#   font-family: var(--sans) !important;
#   font-weight: 500 !important;
#   font-size: 13.5px !important;
#   transition: border-color 0.15s ease, background 0.15s ease;
# }
# .stButton > button:hover { border-color: var(--accent) !important; background: var(--surface-hover) !important; }

# .stButton > button[kind="primaryFormSubmit"],
# div[data-testid="stFormSubmitButton"] button {
#   background: var(--accent) !important;
#   border-color: var(--accent) !important;
#   color: #17140b !important;
#   font-weight: 600 !important;
# }
# div[data-testid="stFormSubmitButton"] button:hover { opacity: 0.92; }

# input, textarea { border-radius: var(--r-sm) !important; font-family: var(--sans) !important; }
# div[data-baseweb="input"] { background: var(--surface) !important; border-color: var(--border) !important; }

# [data-testid="stExpander"] { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); }

# hr { border-color: var(--border) !important; }

# code, .stCode, [data-testid="stCodeBlock"] { font-family: var(--mono) !important; }

# @media (max-width: 900px) {
#   .stat-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
#   .stat:nth-child(2) { border-right: none; }
# }
# </style>
# """, unsafe_allow_html=True)


# # ============================================================
# # SESSION STATE
# # ============================================================

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


# # ============================================================
# # API FUNCTIONS
# # ============================================================

# def login_user(email: str, password: str) -> bool:
#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/auth/login",
#             json={"email": email, "password": password},
#             timeout=10,
#         )
#         if response.status_code == 200:
#             result = response.json()
#             st.session_state.access_token = result["access_token"]
#             st.session_state.user = result["user"]
#             return True
#         if response.status_code == 401:
#             st.error("Invalid email or password.")
#         else:
#             try:
#                 detail = response.json().get("detail", "Login failed.")
#             except ValueError:
#                 detail = "Login failed."
#             st.error(detail)
#         return False
#     except requests.exceptions.RequestException as exc:
#         st.error(f"Unable to reach the backend: {exc}")
#         return False


# def check_backend() -> bool:
#     try:
#         response = requests.get(FASTAPI_URL, timeout=5)
#         return response.status_code == 200
#     except requests.exceptions.RequestException:
#         return False


# def send_message(query: str) -> dict:
#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/chat",
#             headers={"Authorization": f"Bearer {st.session_state.access_token}"},
#             json={"query": query, "thread_id": st.session_state.thread_id},
#             timeout=180,
#         )
#         if response.status_code == 401:
#             st.session_state.access_token = None
#             st.session_state.user = None
#             st.session_state.messages = []
#             st.session_state.pending_approval = None
#             st.session_state.workflow = None
#             st.rerun()
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as exc:
#         return {"success": False, "blocked": False, "error": str(exc)}


# def send_email_decision(thread_id: str, decision: str) -> dict:
#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/email/approval",
#             json={"thread_id": thread_id, "decision": decision},
#             timeout=180,
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as exc:
#         return {"success": False, "blocked": False, "error": str(exc)}


# # ============================================================
# # DATA HELPERS
# # ============================================================

# def extract_workflow(result: dict) -> dict:
#     data = result.get("data", {})
#     return {
#         "tasks": result.get("tasks", data.get("tasks", [])),
#         "completed_tasks": result.get("completed_tasks", data.get("completed_tasks", [])),
#         "task_count": result.get("task_count", data.get("task_count", 0)),
#         "current_task": result.get("current_task", data.get("current_task")),
#         "workflow_results": result.get("workflow_results", data.get("workflow_results", [])),
#     }


# def get_task_value(task, key, default=None):
#     if isinstance(task, dict):
#         return task.get(key, default)
#     return getattr(task, key, default)


# def esc(value) -> str:
#     """Minimal HTML escaping for values interpolated into markup."""
#     return (
#         str(value)
#         .replace("&", "&amp;")
#         .replace("<", "&lt;")
#         .replace(">", "&gt;")
#     )


# # ============================================================
# # UI COMPONENTS
# # ============================================================

# def render_brand():
#     st.markdown("""
# <div class="brand">
# <div class="brand-mark">AF</div>
# <div>
# <div class="brand-name">AgentFlow</div>
# <div class="brand-sub">orchestration console</div>
# </div>
# </div>
# """, unsafe_allow_html=True)


# def render_stepper():
#     steps = [
#         ("1", "Planner", True),
#         ("2", "Executor", True),
#         ("3", "Tasks", True),
#         ("4", "Approval", False),
#         ("5", "Delivery", False),
#     ]
#     parts = ['<div class="stepper">']
#     for i, (index, label, active) in enumerate(steps):
#         cls = "step is-active" if active else "step"
#         parts.append(f'<div class="{cls}"><span class="step-index">{index}</span><span class="step-label">{label}</span></div>')
#         if i < len(steps) - 1:
#             parts.append('<div class="step-connector"></div>')
#     parts.append("</div>")
#     st.markdown("".join(parts), unsafe_allow_html=True)


# def render_empty_state():
#     st.markdown("""
# <div class="empty">
# <div class="empty-title">No workflow running yet</div>
# <div class="empty-desc">Describe what you want done in plain language. The planner breaks it into tasks, the executor runs them in dependency order, and anything leaving the system — like an email — waits for your sign-off below.</div>
# </div>
# """, unsafe_allow_html=True)


# STATUS_TAG = {
#     "pending": ("tag-pending", "Queued"),
#     "running": ("tag-running", "Running"),
#     "completed": ("tag-completed", "Completed"),
#     "rejected": ("tag-rejected", "Rejected"),
#     "failed": ("tag-failed", "Failed"),
# }


# def render_task_row(task):
#     task_id = esc(get_task_value(task, "id", "unknown"))
#     task_type = esc(get_task_value(task, "type", "unknown")).lower()
#     description = esc(get_task_value(task, "description", ""))
#     depends_on = get_task_value(task, "depends_on", [])
#     use_blog = get_task_value(task, "use_blog", False)
#     status = str(get_task_value(task, "status", "unknown")).lower()

#     tag_class, tag_text = STATUS_TAG.get(status, ("tag-pending", status.title() or "Unknown"))
#     dependency_text = esc(", ".join(depends_on)) if depends_on else "none"
#     blog_text = "uses generated blog" if use_blog else "independent input"

#     st.markdown(f"""
# <div class="task-row status-{status}">
# <div class="task-row-top">
# <div><span class="task-id">{task_id}</span><span class="task-type">{task_type}</span></div>
# <span class="tag {tag_class}">{tag_text}</span>
# </div>
# <p class="task-desc">{description}</p>
# <div class="task-meta"><span>depends on {dependency_text}</span><span>{blog_text}</span></div>
# </div>
# """, unsafe_allow_html=True)


# def render_workflow_results(workflow_results):
#     if not workflow_results:
#         return

#     st.markdown('<div class="panel-heading">Output</div>', unsafe_allow_html=True)

#     for item in workflow_results:
#         task_id = esc(get_task_value(item, "task_id", "unknown"))
#         task_type = get_task_value(item, "task_type", "unknown")
#         status = get_task_value(item, "status", "unknown")
#         result_data = get_task_value(item, "result", None)

#         if task_type == "blog" and isinstance(result_data, dict):
#             title = result_data.get("title", "Blog generated")
#             meta = "content generated"
#         elif task_type == "email" and isinstance(result_data, dict):
#             recipient = result_data.get("to", "")
#             subject = result_data.get("subject", "")
#             title = subject if subject else "Email prepared"
#             meta = f"to {recipient}" if recipient else "prepared"
#         else:
#             title = f"{str(task_type).lower()} result"
#             meta = f"status: {status}"

#         st.markdown(f"""
# <div class="result-row">
# <div class="result-title"><span>✓</span>{esc(title)}<span style="color:var(--muted); margin-left:8px;">{esc(task_id)}</span></div>
# <div class="result-meta">{esc(meta)}</div>
# </div>
# """, unsafe_allow_html=True)


# def display_workflow(workflow):
#     if not workflow:
#         return

#     tasks = workflow.get("tasks", [])
#     if not tasks:
#         return

#     completed_tasks = workflow.get("completed_tasks", [])
#     task_count = workflow.get("task_count", len(tasks))
#     current_task = workflow.get("current_task")
#     workflow_results = workflow.get("workflow_results", [])
#     completed_count = len(completed_tasks)

#     if completed_count >= task_count and task_count:
#         workflow_status = ("ok", "Complete")
#     elif current_task:
#         workflow_status = ("", "In progress")
#     else:
#         workflow_status = ("", "Ready")

#     progress_pct = round(completed_count / task_count * 100) if task_count else 0

#     top_left, top_right = st.columns([4, 1])
#     with top_left:
#         st.markdown('<div class="panel-heading">Execution</div>', unsafe_allow_html=True)
#     with top_right:
#         status_class, status_text = workflow_status
#         st.markdown(
#             f'<div class="status-line {status_class}" style="justify-content:center;">'
#             f'<span class="status-dot"></span>{status_text}</div>',
#             unsafe_allow_html=True,
#         )

#     st.markdown(f"""
# <div class="stat-strip">
# <div class="stat"><div class="stat-label">Tasks</div><div class="stat-value">{task_count}</div></div>
# <div class="stat"><div class="stat-label">Completed</div><div class="stat-value">{completed_count}</div></div>
# <div class="stat"><div class="stat-label">Current</div><div class="stat-value accent" style="font-size:14px;">{esc(current_task) if current_task else "—"}</div></div>
# <div class="stat"><div class="stat-label">Progress</div><div class="stat-value">{progress_pct}%</div></div>
# </div>
# """, unsafe_allow_html=True)

#     for task in tasks:
#         render_task_row(task)

#     render_workflow_results(workflow_results)


# def render_approval():
#     if not st.session_state.pending_approval:
#         return

#     approval_data = st.session_state.pending_approval
#     approval = approval_data.get("approval", {})
#     email = approval.get("email", {})
#     thread_id = approval_data.get("thread_id", st.session_state.thread_id)

#     st.markdown(f"""
# <div class="approval-panel">
# <div class="approval-title">Authorization needed</div>
# <div class="approval-desc">AgentFlow drafted an email that will leave the system. Review it below — nothing sends until you approve it.</div>
# <div class="approval-field-label">To</div>
# <div class="approval-field-value">{esc(email.get("to", "—"))}</div>
# <div class="approval-field-label">Subject</div>
# <div class="approval-field-value">{esc(email.get("subject", "—"))}</div>
# </div>
# """, unsafe_allow_html=True)

#     st.markdown("")

#     st.text_area(
#         "Generated email",
#         value=email.get("body", ""),
#         height=220,
#         disabled=True,
#         label_visibility="collapsed",
#     )

#     approve_col, reject_col = st.columns(2)
#     with approve_col:
#         approve_clicked = st.button("Approve and send", key=f"approve_{thread_id}", use_container_width=True)
#     with reject_col:
#         reject_clicked = st.button("Reject", key=f"reject_{thread_id}", use_container_width=True)

#     if approve_clicked:
#         with st.spinner("Sending approved email..."):
#             decision_result = send_email_decision(thread_id, "approve")
#         if decision_result.get("success"):
#             st.session_state.pending_approval = None
#             st.session_state.workflow = extract_workflow(decision_result)
#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": "Email approved and sent.",
#             })
#             st.rerun()
#         else:
#             st.error(decision_result.get("error", decision_result.get("message", "Failed to approve the email.")))

#     if reject_clicked:
#         with st.spinner("Rejecting email..."):
#             decision_result = send_email_decision(thread_id, "reject")
#         if decision_result.get("success"):
#             st.session_state.pending_approval = None
#             st.session_state.workflow = extract_workflow(decision_result)
#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": "Email rejected. Nothing was sent.",
#             })
#             st.rerun()
#         else:
#             st.error(decision_result.get("error", decision_result.get("message", "Failed to reject the email.")))


# def render_sidebar():
#     with st.sidebar:
#         render_brand()

#         backend_up = check_backend()
#         if backend_up:
#             st.markdown(
#                 '<div class="status-line ok"><span class="status-dot"></span>Backend connected</div>',
#                 unsafe_allow_html=True,
#             )
#         else:
#             st.markdown(
#                 '<div class="status-line err"><span class="status-dot"></span>Backend unreachable</div>',
#                 unsafe_allow_html=True,
#             )

#         st.markdown("")

#         if st.button("New workflow", use_container_width=True):
#             st.session_state.messages = []
#             st.session_state.pending_approval = None
#             st.session_state.workflow = None
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.rerun()

#         st.markdown('<div class="rail-heading">Capabilities</div>', unsafe_allow_html=True)
#         st.markdown("""
# <div class="capability"><div class="capability-name">Blog generation</div><div class="capability-desc">Drafts short structured posts from a topic.</div></div>
# <div class="capability"><div class="capability-name">Email automation</div><div class="capability-desc">Writes outbound messages for your review.</div></div>
# <div class="capability"><div class="capability-name">Dependency graphs</div><div class="capability-desc">Chains tasks that rely on each other's output.</div></div>
# <div class="capability"><div class="capability-name">Human approval</div><div class="capability-desc">Pauses before anything leaves the system.</div></div>
# """, unsafe_allow_html=True)

#         st.markdown('<div class="rail-heading" style="margin-top:20px;">Pipeline</div>', unsafe_allow_html=True)
#         st.markdown("""
# <div class="flow-line">request</div>
# <div class="flow-line">input guardrail</div>
# <div class="flow-line">planner</div>
# <div class="flow-line">dependency graph</div>
# <div class="flow-line">executor</div>
# <div class="flow-line">task workers</div>
# <div class="flow-line">human approval</div>
# <div class="flow-line terminal">gmail</div>
# """, unsafe_allow_html=True)

#         st.markdown('<div class="rail-heading" style="margin-top:20px;">Session</div>', unsafe_allow_html=True)
#         st.code(st.session_state.thread_id, language=None)

#         user_email = (
#             st.session_state.user.get("email", "Authenticated")
#             if st.session_state.user
#             else "Authenticated"
#         )
#         st.caption(user_email)

#         if st.button("Log out", use_container_width=True):
#             st.session_state.access_token = None
#             st.session_state.user = None
#             st.session_state.messages = []
#             st.session_state.pending_approval = None
#             st.session_state.workflow = None
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.rerun()


# # ============================================================
# # LOGIN SCREEN
# # ============================================================

# if not st.session_state.access_token:

#     st.markdown("""
# <div style="max-width:420px; margin:64px auto 0 auto;">
# <div style="display:flex; align-items:center; gap:11px; margin-bottom:30px;">
# <div class="brand-mark" style="width:38px; height:38px; font-size:14px;">AF</div>
# <div>
# <div style="font-weight:600; font-size:17px; color:var(--text);">AgentFlow</div>
# <div style="font-family:var(--mono); font-size:11.5px; color:var(--muted); margin-top:1px;">orchestration console</div>
# </div>
# </div>
# <div style="color:var(--text-dim); font-size:13.5px; line-height:1.6; margin-bottom:28px;">Sign in to plan, execute and approve automated workflows.</div>
# </div>
# """, unsafe_allow_html=True)

#     _, login_center, _ = st.columns([1, 1.3, 1])

#     with login_center:
#         with st.form("login_form"):
#             email = st.text_input("Email", placeholder="you@example.com")
#             password = st.text_input("Password", type="password", placeholder="Enter your password")
#             login_clicked = st.form_submit_button("Sign in", use_container_width=True)

#         if login_clicked:
#             if not email or not password:
#                 st.error("Enter your email and password.")
#             else:
#                 with st.spinner("Authenticating..."):
#                     if login_user(email, password):
#                         st.rerun()

#     st.stop()


# # ============================================================
# # SIDEBAR
# # ============================================================

# render_sidebar()


# # ============================================================
# # HEADER
# # ============================================================

# header_left, header_right = st.columns([4, 1])

# with header_left:
#     st.markdown("""
# <div class="console-header" style="border-bottom:none; margin-bottom:6px; padding-bottom:0;">
# <div>
# <h1 class="console-title">Command your workflow</h1>
# <div class="console-desc">Describe a task in plain language. AgentFlow plans it, executes it, and stops for your approval before anything leaves the system.</div>
# </div>
# </div>
# """, unsafe_allow_html=True)

# with header_right:
#     st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
#     if check_backend():
#         st.markdown(
#             '<div class="status-line ok"><span class="status-dot"></span>Operational</div>',
#             unsafe_allow_html=True,
#         )
#     else:
#         st.markdown(
#             '<div class="status-line err"><span class="status-dot"></span>Offline</div>',
#             unsafe_allow_html=True,
#         )

# st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

# render_stepper()


# # ============================================================
# # CHAT / EMPTY STATE
# # ============================================================

# if not st.session_state.messages:
#     render_empty_state()

#     st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

#     prompt_col1, prompt_col2, prompt_col3 = st.columns(3)

#     with prompt_col1:
#         if st.button("Generate a blog", use_container_width=True):
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": "Generate a brief blog about AI agents.",
#             })
#             st.rerun()

#     with prompt_col2:
#         if st.button("Draft an email", use_container_width=True):
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": "Create an email about AI agents.",
#             })
#             st.rerun()

#     with prompt_col3:
#         if st.button("Blog, then email", use_container_width=True):
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": "Generate a brief blog about AI agents and email the generated blog.",
#             })
#             st.rerun()

#     st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# # ============================================================
# # MESSAGE HISTORY
# # ============================================================

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])


# # ============================================================
# # WORKFLOW + APPROVAL
# # ============================================================

# display_workflow(st.session_state.workflow)
# render_approval()


# # ============================================================
# # CHAT INPUT
# # ============================================================

# query = st.chat_input("Ask AgentFlow to research, create or automate...")


# # ============================================================
# # QUERY EXECUTION
# # ============================================================

# if query:

#     if st.session_state.pending_approval:
#         st.warning("Approve or reject the pending email first.")
#         st.stop()

#     st.session_state.messages.append({"role": "user", "content": query})

#     with st.chat_message("user"):
#         st.markdown(query)

#     with st.chat_message("assistant"):
#         start_time = time.time()

#         with st.spinner("Planning and executing..."):
#             result = send_message(query)

#         elapsed_time = time.time() - start_time
#         workflow = extract_workflow(result)
#         st.session_state.workflow = workflow

#         if result.get("error"):
#             answer = f"**Couldn't reach the workflow backend.**\n\n`{result['error']}`"
#             st.error(answer)

#         elif result.get("blocked"):
#             stage = result.get("stage", "security")
#             reason = result.get("reason", "Request blocked by a security guardrail.")

#             if stage == "input":
#                 answer = "**Request blocked.** The input guardrail stopped this request before it ran."
#             elif stage == "output":
#                 answer = "**Response blocked.** The output guardrail stopped the generated response."
#             else:
#                 answer = f"**Request blocked.**\n\n{reason}"

#             st.warning(answer)
#             st.caption(f"stage: {stage} · {elapsed_time:.2f}s")

#         elif result.get("success") and result.get("status") == "approval_required":
#             st.session_state.pending_approval = result
#             approval = result.get("approval", {})
#             email = approval.get("email", {})

#             answer = "**Paused for approval.** AgentFlow prepared the email and is waiting on your decision before it sends."
#             st.warning(answer)

#             if email:
#                 st.caption(f"prepared for {email.get('to', '')} · {elapsed_time:.2f}s")

#         elif result.get("success"):
#             data = result.get("data", {})
#             answer = data.get("response", "Workflow completed.")

#             completed_tasks = workflow.get("completed_tasks", [])
#             task_count = workflow.get("task_count", 0)

#             st.markdown(answer)
#             st.caption(f"{len(completed_tasks)} / {task_count} tasks completed · {elapsed_time:.2f}s")

#         else:
#             answer = "**Unexpected response from AgentFlow.**"
#             st.warning(answer)

#     st.session_state.messages.append({"role": "assistant", "content": answer})

#     if result.get("status") == "approval_required":
#         st.rerun()

##############################################################################################
#######################################################################################33####

# import time
# import uuid

# import requests
# import streamlit as st
# import streamlit.components.v1 as components


# # ============================================================
# # CONFIGURATION
# # ============================================================

# FASTAPI_URL = "http://localhost:8000"

# st.set_page_config(
#     page_title="AgentFlow — Orchestration Console",
#     page_icon="◆",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# # ============================================================
# # DESIGN SYSTEM
# # ------------------------------------------------------------
# # Subject: a console for operators who dispatch and supervise
# # AI agent workflows — closer to a build/deploy log or a
# # mission-control panel than a marketing site. The palette and
# # type system below are built around that: monospace for
# # anything that is data (ids, counts, status), a plain humanist
# # sans for anything that is prose. Status color is the only
# # color language in the UI — amber means "needs you", blue
# # means "in progress", green means "done", red means "stopped".
# #
# # NOTE ON MARKUP: every HTML string below is left-flush (no
# # leading indentation on content lines). Streamlit's markdown
# # renderer treats 4+ leading spaces as a code fence, which is
# # what caused raw tags to print on screen previously — this is
# # the actual fix, not just a restyle.
# # ============================================================

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

# :root {
#   --bg: #15140f;
#   --bg-raised: #1b1a14;
#   --surface: #201f18;
#   --surface-hover: #262419;
#   --border: #34322a;
#   --border-strong: #4a4738;

#   --text: #ece8db;
#   --text-dim: #a6a290;
#   --muted: #726f60;

#   --accent: #e8a33d;
#   --accent-soft: rgba(232, 163, 61, 0.13);
#   --success: #6fa287;
#   --success-soft: rgba(111, 162, 135, 0.13);
#   --info: #6c93a8;
#   --info-soft: rgba(108, 147, 168, 0.13);
#   --danger: #c2695a;
#   --danger-soft: rgba(194, 105, 90, 0.13);

#   --sans: 'IBM Plex Sans', -apple-system, sans-serif;
#   --mono: 'IBM Plex Mono', 'SFMono-Regular', monospace;

#   --r-sm: 4px;
#   --r-md: 8px;
# }

# #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
# header { background: transparent !important; }

# html, body, .stApp { background: var(--bg); color: var(--text); font-family: var(--sans); }
# .stApp { background-image: none; }

# .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 6rem; }

# h1, h2, h3, h4, h5, h6 { font-family: var(--sans); color: var(--text); }
# p, span, div, label { font-family: var(--sans); }

# ::selection { background: var(--accent-soft); color: var(--text); }

# /* ---------------- sidebar ---------------- */

# [data-testid="stSidebar"] {
#   background: var(--bg-raised);
#   border-right: 1px solid var(--border);
# }
# [data-testid="stSidebar"] .block-container { padding-top: 1.75rem; }

# .brand {
#   display: flex;
#   align-items: center;
#   gap: 11px;
#   margin-bottom: 26px;
#   padding-bottom: 18px;
#   border-bottom: 1px solid var(--border);
# }
# .brand-mark {
#   width: 34px;
#   height: 34px;
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   border: 1px solid var(--border-strong);
#   border-radius: var(--r-sm);
#   font-family: var(--mono);
#   font-weight: 600;
#   font-size: 13px;
#   color: var(--accent);
#   background: var(--surface);
# }
# .brand-name { font-weight: 600; font-size: 15px; color: var(--text); line-height: 1.2; }
# .brand-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 1px; }

# .rail-heading {
#   font-family: var(--mono);
#   font-size: 11px;
#   color: var(--muted);
#   margin: 4px 0 10px 0;
# }

# .status-line {
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   font-family: var(--mono);
#   font-size: 12px;
#   color: var(--text-dim);
#   padding: 9px 11px;
#   border: 1px solid var(--border);
#   border-radius: var(--r-sm);
#   background: var(--surface);
# }
# .status-line.ok { color: var(--success); border-color: rgba(111,162,135,0.3); }
# .status-line.err { color: var(--danger); border-color: rgba(194,105,90,0.3); }
# .status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

# .capability { padding: 9px 0; border-bottom: 1px solid var(--border); }
# .capability:last-child { border-bottom: none; }
# .capability-name { font-size: 13px; font-weight: 600; color: var(--text); }
# .capability-desc { font-size: 12px; color: var(--muted); margin-top: 2px; line-height: 1.5; }

# .flow-line {
#   font-family: var(--mono);
#   font-size: 12px;
#   color: var(--text-dim);
#   padding: 5px 0 5px 14px;
#   border-left: 1px solid var(--border);
#   margin-left: 3px;
# }
# .flow-line.terminal { color: var(--muted); }

# /* ---------------- header / hero ---------------- */

# .console-header {
#   display: flex;
#   align-items: flex-start;
#   justify-content: space-between;
#   gap: 20px;
#   padding-bottom: 22px;
#   margin-bottom: 22px;
#   border-bottom: 1px solid var(--border);
# }
# .console-title {
#   font-size: 27px;
#   font-weight: 600;
#   letter-spacing: -0.3px;
#   color: var(--text);
#   margin: 0;
# }
# .console-desc {
#   max-width: 560px;
#   margin-top: 9px;
#   color: var(--text-dim);
#   font-size: 14px;
#   line-height: 1.6;
# }

# /* ---------------- stepper ---------------- */

# .stepper {
#   display: flex;
#   align-items: center;
#   margin-bottom: 26px;
#   overflow-x: auto;
# }
# .step {
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   padding: 6px 2px;
#   white-space: nowrap;
# }
# .step-index {
#   width: 20px;
#   height: 20px;
#   border-radius: 50%;
#   border: 1px solid var(--border-strong);
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   font-family: var(--mono);
#   font-size: 10px;
#   color: var(--muted);
#   flex-shrink: 0;
# }
# .step.is-active .step-index { border-color: var(--accent); color: var(--accent); }
# .step-label { font-size: 12.5px; color: var(--muted); }
# .step.is-active .step-label { color: var(--text); font-weight: 500; }
# .step-connector { width: 28px; height: 1px; background: var(--border); margin: 0 4px; flex-shrink: 0; }

# /* ---------------- stat strip ---------------- */

# .stat-strip {
#   display: grid;
#   grid-template-columns: repeat(4, minmax(0, 1fr));
#   border: 1px solid var(--border);
#   border-radius: var(--r-md);
#   overflow: hidden;
#   margin-bottom: 22px;
# }
# .stat {
#   padding: 14px 16px;
#   border-right: 1px solid var(--border);
#   background: var(--surface);
# }
# .stat:last-child { border-right: none; }
# .stat-label { font-size: 11px; color: var(--muted); }
# .stat-value {
#   font-family: var(--mono);
#   font-size: 21px;
#   font-weight: 600;
#   color: var(--text);
#   margin-top: 3px;
#   font-variant-numeric: tabular-nums;
# }
# .stat-value.accent { color: var(--accent); }

# .panel-heading {
#   font-size: 13px;
#   font-weight: 600;
#   color: var(--text-dim);
#   margin: 4px 0 10px 0;
# }

# /* ---------------- task rows ---------------- */

# .task-row {
#   border: 1px solid var(--border);
#   border-left: 3px solid var(--border-strong);
#   border-radius: var(--r-sm);
#   padding: 13px 15px;
#   margin-bottom: 8px;
#   background: var(--surface);
# }
# .task-row.status-running { border-left-color: var(--info); }
# .task-row.status-completed { border-left-color: var(--success); }
# .task-row.status-pending { border-left-color: var(--accent); }
# .task-row.status-failed, .task-row.status-rejected { border-left-color: var(--danger); }

# .task-row-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
# .task-id { font-family: var(--mono); font-size: 13px; font-weight: 600; color: var(--text); }
# .task-type { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-left: 9px; }
# .task-desc { font-size: 13px; color: var(--text-dim); line-height: 1.55; margin: 8px 0 0 0; }
# .task-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 9px; }
# .task-meta span:not(:last-child)::after { content: '  /  '; color: var(--border-strong); }

# .tag {
#   display: inline-block;
#   font-family: var(--mono);
#   font-size: 10.5px;
#   font-weight: 500;
#   padding: 3px 8px;
#   border-radius: var(--r-sm);
#   border: 1px solid transparent;
# }
# .tag-completed { color: var(--success); background: var(--success-soft); border-color: rgba(111,162,135,0.25); }
# .tag-running { color: var(--info); background: var(--info-soft); border-color: rgba(108,147,168,0.25); }
# .tag-pending { color: var(--accent); background: var(--accent-soft); border-color: rgba(232,163,61,0.25); }
# .tag-failed, .tag-rejected { color: var(--danger); background: var(--danger-soft); border-color: rgba(194,105,90,0.25); }

# /* ---------------- results ---------------- */

# .result-row {
#   display: flex;
#   align-items: baseline;
#   justify-content: space-between;
#   gap: 14px;
#   padding: 11px 14px;
#   border: 1px solid var(--border);
#   border-radius: var(--r-sm);
#   margin-top: 7px;
#   background: var(--bg-raised);
# }
# .result-title { font-size: 13px; color: var(--text); }
# .result-title span { color: var(--success); font-family: var(--mono); margin-right: 6px; }
# .result-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); flex-shrink: 0; }

# /* ---------------- approval ---------------- */

# .approval-panel {
#   border: 1px solid rgba(232, 163, 61, 0.35);
#   border-radius: var(--r-md);
#   padding: 20px;
#   background: var(--accent-soft);
# }
# .approval-title { font-size: 15px; font-weight: 600; color: var(--text); }
# .approval-desc { font-size: 13px; color: var(--text-dim); margin-top: 5px; line-height: 1.6; max-width: 640px; }
# .approval-field-label { font-family: var(--mono); font-size: 10.5px; color: var(--muted); margin-top: 15px; }
# .approval-field-value { font-size: 13.5px; color: var(--text); margin-top: 2px; }

# /* ---------------- empty state ---------------- */

# .empty {
#   padding: 52px 10px 28px 10px;
#   border: 1px dashed var(--border);
#   border-radius: var(--r-md);
#   text-align: left;
# }
# .empty-title { font-size: 18px; font-weight: 600; color: var(--text); }
# .empty-desc { max-width: 520px; margin-top: 8px; color: var(--text-dim); font-size: 13.5px; line-height: 1.65; }

# /* ---------------- chat ---------------- */

# [data-testid="stChatMessage"] {
#   background: var(--surface);
#   border: 1px solid var(--border);
#   border-radius: var(--r-md);
#   padding: 13px 15px;
# }
# [data-testid="stChatMessage"] p { line-height: 1.65; font-size: 14px; }

# [data-testid="stChatInput"] > div {
#   background: var(--surface) !important;
#   border: 1px solid var(--border-strong) !important;
#   border-radius: var(--r-md) !important;
# }
# [data-testid="stChatInput"] > div:focus-within { border-color: var(--accent) !important; }
# [data-testid="stChatInput"] textarea { color: var(--text) !important; font-family: var(--sans) !important; }

# /* ---------------- buttons / inputs ---------------- */

# .stButton > button {
#   width: 100%;
#   min-height: 40px;
#   border-radius: var(--r-sm) !important;
#   border: 1px solid var(--border-strong) !important;
#   background: var(--surface) !important;
#   color: var(--text) !important;
#   font-family: var(--sans) !important;
#   font-weight: 500 !important;
#   font-size: 13.5px !important;
#   transition: border-color 0.15s ease, background 0.15s ease;
# }
# .stButton > button:hover { border-color: var(--accent) !important; background: var(--surface-hover) !important; }

# .stButton > button[kind="primaryFormSubmit"],
# div[data-testid="stFormSubmitButton"] button {
#   background: var(--accent) !important;
#   border-color: var(--accent) !important;
#   color: #17140b !important;
#   font-weight: 600 !important;
# }
# div[data-testid="stFormSubmitButton"] button:hover { opacity: 0.92; }

# input, textarea { border-radius: var(--r-sm) !important; font-family: var(--sans) !important; }
# div[data-baseweb="input"] { background: var(--surface) !important; border-color: var(--border) !important; }

# [data-testid="stExpander"] { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); }

# hr { border-color: var(--border) !important; }

# code, .stCode, [data-testid="stCodeBlock"] { font-family: var(--mono) !important; }

# @media (max-width: 900px) {
#   .stat-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
#   .stat:nth-child(2) { border-right: none; }
# }

# /* ============================================================
#    MOTION LAYER — premium interaction system
#    ============================================================ */

# :root {
#   --glow-amber: rgba(232, 163, 61, .32);
#   --glow-blue: rgba(108, 147, 168, .22);
#   --glass: rgba(27, 26, 20, .72);
# }

# /* Smooth page entrance */
# .main .block-container {
#   animation: af-page-in .7s cubic-bezier(.22,1,.36,1) both;
# }
# @keyframes af-page-in {
#   from { opacity: 0; transform: translateY(8px); }
#   to { opacity: 1; transform: translateY(0); }
# }

# /* Header typography gets a subtle scramble/glitch feel. */
# .console-title {
#   position: relative;
#   text-shadow: 0 0 28px rgba(232,163,61,.08);
# }
# .console-title::after {
#   content: "COMMAND YOUR WORKFLOW";
#   position: absolute;
#   inset: 0;
#   color: var(--accent);
#   opacity: 0;
#   pointer-events: none;
#   animation: af-title-flicker 5s ease-in-out infinite;
# }
# @keyframes af-title-flicker {
#   0%, 86%, 100% { opacity: 0; transform: translateX(0); clip-path: inset(0 100% 0 0); }
#   88% { opacity: .18; transform: translateX(1px); clip-path: inset(15% 0 55% 0); }
#   90% { opacity: 0; transform: translateX(-1px); clip-path: inset(70% 0 8% 0); }
#   92% { opacity: .10; transform: translateX(0); clip-path: inset(0 0 0 0); }
# }

# /* Glassier cards while retaining the original restrained console style. */
# .stat-strip,
# .task-row,
# .result-row,
# .approval-panel,
# .empty {
#   box-shadow: 0 18px 60px rgba(0,0,0,.13);
#   backdrop-filter: blur(12px);
# }
# .task-row {
#   transition: transform .25s cubic-bezier(.22,1,.36,1),
#               border-color .25s ease,
#               background .25s ease,
#               box-shadow .25s ease;
# }
# .task-row:hover {
#   transform: translateX(4px);
#   background: var(--surface-hover);
#   box-shadow: -8px 0 28px rgba(232,163,61,.045);
# }
# .result-row {
#   transition: transform .25s cubic-bezier(.22,1,.36,1), border-color .25s ease;
# }
# .result-row:hover {
#   transform: translateX(3px);
#   border-color: var(--border-strong);
# }

# /* Premium Streamlit buttons inspired by the liquid-carve interaction. */
# .stButton > button {
#   position: relative;
#   overflow: hidden;
#   isolation: isolate;
#   box-shadow: inset 0 0 0 1px rgba(255,255,255,.015),
#               0 8px 24px rgba(0,0,0,.10);
# }
# .stButton > button::before {
#   content: "";
#   position: absolute;
#   width: 110px;
#   height: 110px;
#   left: var(--mx, 50%);
#   top: var(--my, 50%);
#   border-radius: 50%;
#   transform: translate(-50%,-50%) scale(0);
#   background: radial-gradient(circle, rgba(232,163,61,.22), rgba(232,163,61,0) 68%);
#   transition: transform .45s cubic-bezier(.22,1,.36,1);
#   pointer-events: none;
#   z-index: -1;
# }
# .stButton > button:hover::before {
#   transform: translate(-50%,-50%) scale(1.8);
# }
# .stButton > button:active {
#   transform: scale(.985);
# }
# .stButton > button[kind="primaryFormSubmit"],
# div[data-testid="stFormSubmitButton"] button {
#   box-shadow: 0 8px 30px rgba(232,163,61,.13);
# }

# /* Animated status dot. */
# .status-line .status-dot {
#   animation: af-status-pulse 2.2s ease-in-out infinite;
# }
# @keyframes af-status-pulse {
#   0%,100% { box-shadow: 0 0 0 0 currentColor; opacity: .8; }
#   50% { box-shadow: 0 0 0 5px transparent; opacity: 1; }
# }

# /* Input focus glow */
# [data-testid="stChatInput"] > div {
#   transition: border-color .25s ease, box-shadow .25s ease, transform .25s ease;
# }
# [data-testid="stChatInput"] > div:focus-within {
#   box-shadow: 0 0 0 1px rgba(232,163,61,.08), 0 12px 40px rgba(0,0,0,.18);
#   transform: translateY(-1px);
# }

# /* ============================================================
#    DOUBLE-STAIRS PRELOADER
#    ============================================================ */
# .af-preloader {
#   position: fixed;
#   inset: 0;
#   z-index: 999999;
#   background: #15140f;
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   overflow: hidden;
# }
# .af-preloader::after {
#   content: "";
#   position: absolute;
#   inset: 0;
#   background: radial-gradient(circle at 50% 45%, rgba(232,163,61,.07), transparent 42%);
# }
# .af-preloader-copy {
#   position: absolute;
#   z-index: 4;
#   text-align: center;
#   color: #ece8db;
#   font-family: 'IBM Plex Mono', monospace;
#   letter-spacing: .18em;
#   font-size: 10px;
#   text-transform: uppercase;
#   opacity: .65;
# }
# .af-stairs {
#   position: absolute;
#   inset: 0;
#   display: flex;
#   pointer-events: none;
# }
# .af-stair {
#   flex: 1;
#   background: #201f18;
#   transform: scaleY(1);
#   transform-origin: top;
# }
# .af-stairs.left .af-stair:nth-child(1) { transition-delay: .00s; }
# .af-stairs.left .af-stair:nth-child(2) { transition-delay: .04s; }
# .af-stairs.left .af-stair:nth-child(3) { transition-delay: .08s; }
# .af-stairs.left .af-stair:nth-child(4) { transition-delay: .12s; }
# .af-stairs.left .af-stair:nth-child(5) { transition-delay: .16s; }
# .af-stairs.right .af-stair {
#   transform-origin: bottom;
# }
# .af-stairs.right .af-stair:nth-child(1) { transition-delay: .16s; }
# .af-stairs.right .af-stair:nth-child(2) { transition-delay: .12s; }
# .af-stairs.right .af-stair:nth-child(3) { transition-delay: .08s; }
# .af-stairs.right .af-stair:nth-child(4) { transition-delay: .04s; }
# .af-stairs.right .af-stair:nth-child(5) { transition-delay: .00s; }
# .af-preloader.is-out .af-stair {
#   transform: scaleY(0);
#   transition: transform .68s cubic-bezier(.77,0,.175,1);
# }
# .af-preloader.is-out .af-preloader-copy {
#   opacity: 0;
#   transform: translateY(-8px);
#   transition: opacity .25s ease, transform .25s ease;
# }

# /* ============================================================
#    TUNNEL / THREE.JS HERO
#    ============================================================ */
# .af-tunnel-shell {
#   position: relative;
#   width: 100%;
#   height: 285px;
#   overflow: hidden;
#   border: 1px solid var(--border);
#   border-radius: 12px;
#   background: #090a0a;
#   margin: 0 0 25px;
#   box-shadow: inset 0 0 90px rgba(0,0,0,.55), 0 20px 70px rgba(0,0,0,.18);
# }
# .af-tunnel-shell iframe {
#   width: 100%;
#   height: 100%;
#   border: 0;
# }
# .af-tunnel-overlay {
#   position: absolute;
#   inset: 0;
#   pointer-events: none;
#   background:
#     linear-gradient(90deg, rgba(21,20,15,.62), transparent 35%, transparent 65%, rgba(21,20,15,.48)),
#     linear-gradient(0deg, rgba(21,20,15,.48), transparent 35%);
# }
# .af-tunnel-caption {
#   position: absolute;
#   left: 22px;
#   bottom: 18px;
#   z-index: 2;
#   font-family: var(--mono);
#   font-size: 10px;
#   letter-spacing: .13em;
#   text-transform: uppercase;
#   color: rgba(236,232,219,.58);
# }
# .af-tunnel-caption b {
#   color: var(--accent);
#   font-weight: 500;
# }

# /* ============================================================
#    CYLINDER CAROUSEL
#    ============================================================ */
# .af-cylinder {
#   position: relative;
#   height: 205px;
#   margin: 0 0 22px;
#   overflow: hidden;
#   border: 1px solid var(--border);
#   border-radius: 10px;
#   background:
#     radial-gradient(ellipse at center, rgba(232,163,61,.055), transparent 52%),
#     var(--bg-raised);
#   perspective: 850px;
#   cursor: grab;
# }
# .af-cylinder:active { cursor: grabbing; }
# .af-cylinder::before {
#   content: "";
#   position: absolute;
#   left: 50%;
#   top: 50%;
#   width: 44%;
#   height: 1px;
#   transform: translate(-50%,-50%);
#   background: linear-gradient(90deg, transparent, rgba(232,163,61,.28), transparent);
# }
# .af-cylinder-track {
#   position: absolute;
#   inset: 0;
#   transform-style: preserve-3d;
# }
# .af-cylinder-card {
#   position: absolute;
#   left: 50%;
#   top: 50%;
#   width: 190px;
#   height: 112px;
#   padding: 15px;
#   box-sizing: border-box;
#   border: 1px solid var(--border);
#   border-radius: 9px;
#   background: rgba(32,31,24,.91);
#   backdrop-filter: blur(8px);
#   transform-style: preserve-3d;
#   transition: transform .08s linear, opacity .08s linear, border-color .25s ease;
#   box-shadow: 0 20px 45px rgba(0,0,0,.18);
# }
# .af-cylinder-card strong {
#   display: block;
#   font-size: 12px;
#   color: var(--text);
#   margin-bottom: 7px;
# }
# .af-cylinder-card small {
#   display: block;
#   color: var(--muted);
#   font-family: var(--mono);
#   font-size: 9.5px;
#   line-height: 1.55;
# }
# .af-cylinder-card .af-card-index {
#   color: var(--accent);
#   font-family: var(--mono);
#   font-size: 9px;
#   margin-bottom: 9px;
# }
# .af-cylinder-hint {
#   position: absolute;
#   right: 15px;
#   bottom: 13px;
#   z-index: 3;
#   font-family: var(--mono);
#   font-size: 9px;
#   color: var(--muted);
# }

# /* Responsive polish */
# @media (max-width: 900px) {
#   .af-tunnel-shell { height: 235px; }
#   .af-cylinder { height: 185px; }
# }
# @media (prefers-reduced-motion: reduce) {
#   .main .block-container,
#   .status-line .status-dot,
#   .console-title::after {
#     animation: none !important;
#   }
#   .task-row, .result-row, .stButton > button {
#     transition: none !important;
#   }
# }

# </style>
# """, unsafe_allow_html=True)


# # ============================================================
# # SESSION STATE
# # ============================================================

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


# # ============================================================
# # API FUNCTIONS
# # ============================================================

# def login_user(email: str, password: str) -> bool:
#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/auth/login",
#             json={"email": email, "password": password},
#             timeout=10,
#         )
#         if response.status_code == 200:
#             result = response.json()
#             st.session_state.access_token = result["access_token"]
#             st.session_state.user = result["user"]
#             return True
#         if response.status_code == 401:
#             st.error("Invalid email or password.")
#         else:
#             try:
#                 detail = response.json().get("detail", "Login failed.")
#             except ValueError:
#                 detail = "Login failed."
#             st.error(detail)
#         return False
#     except requests.exceptions.RequestException as exc:
#         st.error(f"Unable to reach the backend: {exc}")
#         return False


# def check_backend() -> bool:
#     try:
#         response = requests.get(FASTAPI_URL, timeout=5)
#         return response.status_code == 200
#     except requests.exceptions.RequestException:
#         return False


# def send_message(query: str) -> dict:
#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/chat",
#             headers={"Authorization": f"Bearer {st.session_state.access_token}"},
#             json={"query": query, "thread_id": st.session_state.thread_id},
#             timeout=180,
#         )
#         if response.status_code == 401:
#             st.session_state.access_token = None
#             st.session_state.user = None
#             st.session_state.messages = []
#             st.session_state.pending_approval = None
#             st.session_state.workflow = None
#             st.rerun()
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as exc:
#         return {"success": False, "blocked": False, "error": str(exc)}


# def send_email_decision(thread_id: str, decision: str) -> dict:
#     try:
#         response = requests.post(
#             f"{FASTAPI_URL}/email/approval",
#             json={"thread_id": thread_id, "decision": decision},
#             timeout=180,
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as exc:
#         return {"success": False, "blocked": False, "error": str(exc)}


# # ============================================================
# # DATA HELPERS
# # ============================================================

# def extract_workflow(result: dict) -> dict:
#     data = result.get("data", {})
#     return {
#         "tasks": result.get("tasks", data.get("tasks", [])),
#         "completed_tasks": result.get("completed_tasks", data.get("completed_tasks", [])),
#         "task_count": result.get("task_count", data.get("task_count", 0)),
#         "current_task": result.get("current_task", data.get("current_task")),
#         "workflow_results": result.get("workflow_results", data.get("workflow_results", [])),
#     }


# def get_task_value(task, key, default=None):
#     if isinstance(task, dict):
#         return task.get(key, default)
#     return getattr(task, key, default)


# def esc(value) -> str:
#     """Minimal HTML escaping for values interpolated into markup."""
#     return (
#         str(value)
#         .replace("&", "&amp;")
#         .replace("<", "&lt;")
#         .replace(">", "&gt;")
#     )



# # ============================================================
# # MOTION COMPONENTS
# # ============================================================

# def render_double_stairs_preloader():
#     """One-shot Skiper-inspired double-stairs page preloader."""
#     if st.session_state.get("preloader_seen"):
#         return

#     components.html(
#         """
#         <style>
#           html, body { margin:0; padding:0; background:transparent; overflow:hidden; }
#           .p { position:fixed; inset:0; z-index:999999; background:#15140f; overflow:hidden; }
#           .stairs { position:absolute; inset:0; display:flex; }
#           .side { flex:1; display:flex; }
#           .side.r { flex-direction:row-reverse; }
#           .s { flex:1; background:#201f18; transform:scaleY(1); }
#           .l .s { transform-origin:top; }
#           .r .s { transform-origin:bottom; }
#           .l .s:nth-child(1){transition-delay:0s}.l .s:nth-child(2){transition-delay:.04s}
#           .l .s:nth-child(3){transition-delay:.08s}.l .s:nth-child(4){transition-delay:.12s}
#           .l .s:nth-child(5){transition-delay:.16s}
#           .r .s:nth-child(1){transition-delay:.16s}.r .s:nth-child(2){transition-delay:.12s}
#           .r .s:nth-child(3){transition-delay:.08s}.r .s:nth-child(4){transition-delay:.04s}
#           .r .s:nth-child(5){transition-delay:0s}
#           .p.out .s { transform:scaleY(0); transition:transform .72s cubic-bezier(.77,0,.175,1); }
#           .copy {
#             position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
#             color:#ece8db; font:500 10px/1.4 "Courier New",monospace;
#             letter-spacing:.22em; text-transform:uppercase; text-align:center;
#             transition:opacity .25s ease, transform .25s ease;
#           }
#           .copy b { display:block; color:#e8a33d; font-size:18px; letter-spacing:.08em; margin-bottom:8px; }
#           .p.out .copy { opacity:0; transform:translate(-50%,-58%); }
#         </style>
#         <div class="p" id="p">
#           <div class="stairs l"><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i></div>
#           <div class="stairs r"><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i></div>
#           <div class="copy"><b>AF</b>initializing orchestration</div>
#         </div>
#         <script>
#           const p=document.getElementById("p");
#           setTimeout(()=>p.classList.add("out"),1150);
#           setTimeout(()=>{ p.style.display="none"; document.body.style.overflow="auto"; },2050);
#         </script>
#         """,
#         height=0,
#         width=0,
#     )
#     st.session_state.preloader_seen = True


# # The function must be defined before it is called.
# render_double_stairs_preloader()


# def render_tunnel_hero():
#     """Three.js gallery tunnel inspired by the supplied Gallery Tunnel component."""
#     components.html(
#         """
#         <style>
#           html,body{margin:0;padding:0;background:transparent;overflow:hidden}
#           #wrap{position:relative;width:100%;height:285px;background:#090a0a;border-radius:12px;overflow:hidden}
#           canvas{display:block;width:100%;height:100%}
#           .v{position:absolute;inset:0;pointer-events:none;
#              background:linear-gradient(90deg,rgba(21,20,15,.64),transparent 36%,transparent 64%,rgba(21,20,15,.48)),
#                         linear-gradient(0deg,rgba(21,20,15,.52),transparent 38%)}
#           .caption{position:absolute;left:22px;bottom:18px;color:rgba(236,232,219,.58);
#                    font:10px/1 "Courier New",monospace;letter-spacing:.13em;text-transform:uppercase}
#           .caption b{color:#e8a33d;font-weight:500}
#           .reticle{position:absolute;left:50%;top:50%;width:12px;height:12px;transform:translate(-50%,-50%);
#                    border:1px solid rgba(232,163,61,.45);border-radius:50%;box-shadow:0 0 22px rgba(232,163,61,.18)}
#         </style>
#         <div id="wrap">
#           <canvas id="c"></canvas><div class="v"></div><div class="reticle"></div>
#           <div class="caption"><b>LIVE /</b> execution tunnel · pointer accelerates traversal</div>
#         </div>
#         <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
#         <script>
#         (() => {
#           const root=document.getElementById("wrap"), canvas=document.getElementById("c");
#           if(!window.THREE) return;
#           const T=THREE, scene=new T.Scene();
#           scene.background=new T.Color(0x090a0a);
#           scene.fog=new T.Fog(0x090a0a,7,22);
#           const camera=new T.PerspectiveCamera(48,1,.1,100);
#           camera.position.set(0,0,0);

#           const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:"high-performance"});
#           renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));

#           const group=new T.Group(); scene.add(group);
#           const mats=[
#             new T.MeshBasicMaterial({color:0xe8a33d,transparent:true,opacity:.16}),
#             new T.MeshBasicMaterial({color:0x6c93a8,transparent:true,opacity:.12}),
#             new T.MeshBasicMaterial({color:0x6fa287,transparent:true,opacity:.11})
#           ];
#           const lineMat=new T.LineBasicMaterial({color:0x777363,transparent:true,opacity:.32});
#           const slabGeo=new T.PlaneGeometry(1.15,.72);
#           const segments=[];
#           const depth=1.25, count=17, width=5.2, height=3.4;

#           function makeSegment(z){
#             const g=new T.Group(); g.position.z=z;
#             const pts=[];
#             for(let x=-width/2;x<=width/2+.001;x+=width/4){
#               pts.push(new T.Vector3(x,-height/2,0),new T.Vector3(x,height/2,0));
#             }
#             for(let y=-height/2;y<=height/2+.001;y+=height/4){
#               pts.push(new T.Vector3(-width/2,y,0),new T.Vector3(width/2,y,0));
#             }
#             const geo=new T.BufferGeometry().setFromPoints(pts);
#             g.add(new T.LineSegments(geo,lineMat));
#             for(let i=0;i<5;i++){
#               const slab=new T.Mesh(slabGeo,mats[(i+Math.floor(-z/depth))%mats.length]);
#               slab.position.set((Math.random()-.5)*4.1,(Math.random()-.5)*2.55,-.01);
#               slab.rotation.z=(Math.random()-.5)*.22;
#               slab.scale.setScalar(.55+Math.random()*.55);
#               g.add(slab);
#             }
#             return g;
#           }
#           for(let i=0;i<count;i++){const g=makeSegment(-i*depth);scene.add(g);segments.push(g);}

#           const mouse={x:0,y:0,tx:0,ty:0};
#           let down=false, speed=.055, last=performance.now();

#           root.addEventListener("pointermove",e=>{
#             const r=root.getBoundingClientRect();
#             mouse.tx=(e.clientX-r.left)/r.width*2-1;
#             mouse.ty=-((e.clientY-r.top)/r.height*2-1);
#             if(down) speed=.105;
#           });
#           root.addEventListener("pointerenter",()=>speed=.075);
#           root.addEventListener("pointerleave",()=>{mouse.tx=0;mouse.ty=0;down=false;speed=.055});
#           root.addEventListener("pointerdown",()=>{down=true;speed=.12});
#           window.addEventListener("pointerup",()=>{down=false});

#           function resize(){
#             const w=Math.max(1,root.clientWidth),h=Math.max(1,root.clientHeight);
#             camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);
#           }
#           new ResizeObserver(resize).observe(root); resize();

#           function tick(now){
#             requestAnimationFrame(tick);
#             const dt=Math.min(.04,(now-last)/1000);last=now;
#             mouse.x+=(mouse.tx-mouse.x)*Math.min(1,dt*5);
#             mouse.y+=(mouse.ty-mouse.y)*Math.min(1,dt*5);
#             camera.position.x=mouse.x*.32;
#             camera.position.y=mouse.y*.20;
#             camera.rotation.z=-mouse.x*.012;
#             camera.rotation.y=mouse.x*.035;
#             camera.rotation.x=-mouse.y*.025;

#             const dz=speed*dt*60;
#             for(const seg of segments){
#               seg.position.z+=dz;
#               if(seg.position.z>1.3) seg.position.z-=count*depth;
#               seg.children.forEach((m,j)=>{
#                 if(m.isMesh) m.rotation.z += dt*(.04+(j%3)*.018);
#               });
#             }
#             renderer.render(scene,camera);
#           }
#           requestAnimationFrame(tick);
#         })();
#         </script>
#         """,
#         height=285,
#         width=None,
#     )


# def render_cylinder_carousel():
#     """Interactive CSS 3D cylinder carousel for the empty-state prompt deck."""
#     cards = [
#         ("01", "Planner", "decomposes natural-language requests into executable tasks"),
#         ("02", "Executor", "runs dependency-aware workers in the correct order"),
#         ("03", "Guardrails", "checks requests and generated output before delivery"),
#         ("04", "Approval", "pauses external actions until you explicitly approve"),
#         ("05", "Delivery", "hands completed work to the connected destination"),
#         ("06", "Observability", "keeps task status, timing and results visible"),
#     ]
#     cards_json = str([{"i":a,"t":b,"d":c} for a,b,c in cards]).replace("'", '"')
#     components.html(
#         f"""
#         <style>
#           html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
#           #stage{{position:relative;width:100%;height:205px;overflow:hidden;border:1px solid #34322a;border-radius:10px;
#             background:radial-gradient(ellipse at center,rgba(232,163,61,.055),transparent 52%),#1b1a14;
#             perspective:850px;cursor:grab;user-select:none}}
#           #stage:active{{cursor:grabbing}}
#           #track{{position:absolute;inset:0;transform-style:preserve-3d}}
#           .card{{position:absolute;left:50%;top:50%;width:190px;height:112px;padding:15px;box-sizing:border-box;
#             border:1px solid #34322a;border-radius:9px;background:rgba(32,31,24,.92);backdrop-filter:blur(8px);
#             box-shadow:0 20px 45px rgba(0,0,0,.18);transform-style:preserve-3d;}}
#           .ix{{color:#e8a33d;font:9px "Courier New",monospace;margin-bottom:9px}}
#           .tt{{color:#ece8db;font:600 12px system-ui;margin-bottom:7px}}
#           .dd{{color:#726f60;font:9.5px/1.55 "Courier New",monospace}}
#           .hint{{position:absolute;right:15px;bottom:13px;color:#726f60;font:9px "Courier New",monospace}}
#           .line{{position:absolute;left:50%;top:50%;width:44%;height:1px;transform:translate(-50%,-50%);
#             background:linear-gradient(90deg,transparent,rgba(232,163,61,.28),transparent)}}
#         </style>
#         <div id="stage"><div class="line"></div><div id="track"></div><div class="hint">DRAG / SCROLL TO EXPLORE</div></div>
#         <script>
#         (()=>{{
#           const data={cards_json},stage=document.getElementById("stage"),track=document.getElementById("track");
#           const els=data.map((d)=>{{
#             const e=document.createElement("div");e.className="card";
#             e.innerHTML=`<div class="ix">${{d.i}}</div><div class="tt">${{d.t}}</div><div class="dd">${{d.d}}</div>`;
#             track.appendChild(e);return e;
#           }});
#           let offset=0,target=0,down=false,lastX=0;
#           function render(){{
#             const n=els.length, step=58, radius=250;
#             els.forEach((e,i)=>{{
#               let rel=i-offset;
#               rel=((rel+n/2)%n+n)%n-n/2;
#               const a=rel*step*Math.PI/180;
#               const x=Math.sin(a)*radius;
#               const z=(Math.cos(a)-1)*radius;
#               const scale=.58+.42*Math.max(0,Math.cos(a));
#               const op=.28+.72*Math.max(0,Math.cos(a));
#               e.style.transform=`translate(-50%,-50%) translate3d(${{x}}px,0,${{z}}px) scale(${{scale}})`;
#               e.style.opacity=op;
#               e.style.zIndex=String(Math.round(100+Math.cos(a)*100));
#             }});
#             offset+=(target-offset)*.075;
#             requestAnimationFrame(render);
#           }}
#           stage.addEventListener("pointerdown",e=>{{down=true;lastX=e.clientX;stage.setPointerCapture?.(e.pointerId)}});
#           stage.addEventListener("pointermove",e=>{{if(!down)return;target-=(e.clientX-lastX)/42;lastX=e.clientX}});
#           stage.addEventListener("pointerup",()=>down=false);
#           stage.addEventListener("pointercancel",()=>down=false);
#           stage.addEventListener("wheel",e=>{{e.preventDefault();target+=e.deltaY*.008}},{{passive:false}});
#           render();
#         }})();
#         </script>
#         """,
#         height=205,
#         width=None,
#     )


# # ============================================================
# # UI COMPONENTS
# # ============================================================

# def render_brand():
#     st.markdown("""
# <div class="brand">
# <div class="brand-mark">AF</div>
# <div>
# <div class="brand-name">AgentFlow</div>
# <div class="brand-sub">orchestration console</div>
# </div>
# </div>
# """, unsafe_allow_html=True)


# def render_stepper():
#     steps = [
#         ("1", "Planner", True),
#         ("2", "Executor", True),
#         ("3", "Tasks", True),
#         ("4", "Approval", False),
#         ("5", "Delivery", False),
#     ]
#     parts = ['<div class="stepper">']
#     for i, (index, label, active) in enumerate(steps):
#         cls = "step is-active" if active else "step"
#         parts.append(f'<div class="{cls}"><span class="step-index">{index}</span><span class="step-label">{label}</span></div>')
#         if i < len(steps) - 1:
#             parts.append('<div class="step-connector"></div>')
#     parts.append("</div>")
#     st.markdown("".join(parts), unsafe_allow_html=True)


# def render_empty_state():
#     st.markdown("""
# <div class="empty">
# <div class="empty-title">No workflow running yet</div>
# <div class="empty-desc">Describe what you want done in plain language. The planner breaks it into tasks, the executor runs them in dependency order, and anything leaving the system — like an email — waits for your sign-off below.</div>
# </div>
# """, unsafe_allow_html=True)


# STATUS_TAG = {
#     "pending": ("tag-pending", "Queued"),
#     "running": ("tag-running", "Running"),
#     "completed": ("tag-completed", "Completed"),
#     "rejected": ("tag-rejected", "Rejected"),
#     "failed": ("tag-failed", "Failed"),
# }


# def render_task_row(task):
#     task_id = esc(get_task_value(task, "id", "unknown"))
#     task_type = esc(get_task_value(task, "type", "unknown")).lower()
#     description = esc(get_task_value(task, "description", ""))
#     depends_on = get_task_value(task, "depends_on", [])
#     use_blog = get_task_value(task, "use_blog", False)
#     status = str(get_task_value(task, "status", "unknown")).lower()

#     tag_class, tag_text = STATUS_TAG.get(status, ("tag-pending", status.title() or "Unknown"))
#     dependency_text = esc(", ".join(depends_on)) if depends_on else "none"
#     blog_text = "uses generated blog" if use_blog else "independent input"

#     st.markdown(f"""
# <div class="task-row status-{status}">
# <div class="task-row-top">
# <div><span class="task-id">{task_id}</span><span class="task-type">{task_type}</span></div>
# <span class="tag {tag_class}">{tag_text}</span>
# </div>
# <p class="task-desc">{description}</p>
# <div class="task-meta"><span>depends on {dependency_text}</span><span>{blog_text}</span></div>
# </div>
# """, unsafe_allow_html=True)


# def render_workflow_results(workflow_results):
#     if not workflow_results:
#         return

#     st.markdown('<div class="panel-heading">Output</div>', unsafe_allow_html=True)

#     for item in workflow_results:
#         task_id = esc(get_task_value(item, "task_id", "unknown"))
#         task_type = get_task_value(item, "task_type", "unknown")
#         status = get_task_value(item, "status", "unknown")
#         result_data = get_task_value(item, "result", None)

#         if task_type == "blog" and isinstance(result_data, dict):
#             title = result_data.get("title", "Blog generated")
#             meta = "content generated"
#         elif task_type == "email" and isinstance(result_data, dict):
#             recipient = result_data.get("to", "")
#             subject = result_data.get("subject", "")
#             title = subject if subject else "Email prepared"
#             meta = f"to {recipient}" if recipient else "prepared"
#         else:
#             title = f"{str(task_type).lower()} result"
#             meta = f"status: {status}"

#         st.markdown(f"""
# <div class="result-row">
# <div class="result-title"><span>✓</span>{esc(title)}<span style="color:var(--muted); margin-left:8px;">{esc(task_id)}</span></div>
# <div class="result-meta">{esc(meta)}</div>
# </div>
# """, unsafe_allow_html=True)


# def display_workflow(workflow):
#     if not workflow:
#         return

#     tasks = workflow.get("tasks", [])
#     if not tasks:
#         return

#     completed_tasks = workflow.get("completed_tasks", [])
#     task_count = workflow.get("task_count", len(tasks))
#     current_task = workflow.get("current_task")
#     workflow_results = workflow.get("workflow_results", [])
#     completed_count = len(completed_tasks)

#     if completed_count >= task_count and task_count:
#         workflow_status = ("ok", "Complete")
#     elif current_task:
#         workflow_status = ("", "In progress")
#     else:
#         workflow_status = ("", "Ready")

#     progress_pct = round(completed_count / task_count * 100) if task_count else 0

#     top_left, top_right = st.columns([4, 1])
#     with top_left:
#         st.markdown('<div class="panel-heading">Execution</div>', unsafe_allow_html=True)
#     with top_right:
#         status_class, status_text = workflow_status
#         st.markdown(
#             f'<div class="status-line {status_class}" style="justify-content:center;">'
#             f'<span class="status-dot"></span>{status_text}</div>',
#             unsafe_allow_html=True,
#         )

#     st.markdown(f"""
# <div class="stat-strip">
# <div class="stat"><div class="stat-label">Tasks</div><div class="stat-value">{task_count}</div></div>
# <div class="stat"><div class="stat-label">Completed</div><div class="stat-value">{completed_count}</div></div>
# <div class="stat"><div class="stat-label">Current</div><div class="stat-value accent" style="font-size:14px;">{esc(current_task) if current_task else "—"}</div></div>
# <div class="stat"><div class="stat-label">Progress</div><div class="stat-value">{progress_pct}%</div></div>
# </div>
# """, unsafe_allow_html=True)

#     for task in tasks:
#         render_task_row(task)

#     render_workflow_results(workflow_results)


# def render_approval():
#     if not st.session_state.pending_approval:
#         return

#     approval_data = st.session_state.pending_approval
#     approval = approval_data.get("approval", {})
#     email = approval.get("email", {})
#     thread_id = approval_data.get("thread_id", st.session_state.thread_id)

#     st.markdown(f"""
# <div class="approval-panel">
# <div class="approval-title">Authorization needed</div>
# <div class="approval-desc">AgentFlow drafted an email that will leave the system. Review it below — nothing sends until you approve it.</div>
# <div class="approval-field-label">To</div>
# <div class="approval-field-value">{esc(email.get("to", "—"))}</div>
# <div class="approval-field-label">Subject</div>
# <div class="approval-field-value">{esc(email.get("subject", "—"))}</div>
# </div>
# """, unsafe_allow_html=True)

#     st.markdown("")

#     st.text_area(
#         "Generated email",
#         value=email.get("body", ""),
#         height=220,
#         disabled=True,
#         label_visibility="collapsed",
#     )

#     approve_col, reject_col = st.columns(2)
#     with approve_col:
#         approve_clicked = st.button("Approve and send", key=f"approve_{thread_id}", use_container_width=True)
#     with reject_col:
#         reject_clicked = st.button("Reject", key=f"reject_{thread_id}", use_container_width=True)

#     if approve_clicked:
#         with st.spinner("Sending approved email..."):
#             decision_result = send_email_decision(thread_id, "approve")
#         if decision_result.get("success"):
#             st.session_state.pending_approval = None
#             st.session_state.workflow = extract_workflow(decision_result)
#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": "Email approved and sent.",
#             })
#             st.rerun()
#         else:
#             st.error(decision_result.get("error", decision_result.get("message", "Failed to approve the email.")))

#     if reject_clicked:
#         with st.spinner("Rejecting email..."):
#             decision_result = send_email_decision(thread_id, "reject")
#         if decision_result.get("success"):
#             st.session_state.pending_approval = None
#             st.session_state.workflow = extract_workflow(decision_result)
#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": "Email rejected. Nothing was sent.",
#             })
#             st.rerun()
#         else:
#             st.error(decision_result.get("error", decision_result.get("message", "Failed to reject the email.")))


# def render_sidebar():
#     with st.sidebar:
#         render_brand()

#         backend_up = check_backend()
#         if backend_up:
#             st.markdown(
#                 '<div class="status-line ok"><span class="status-dot"></span>Backend connected</div>',
#                 unsafe_allow_html=True,
#             )
#         else:
#             st.markdown(
#                 '<div class="status-line err"><span class="status-dot"></span>Backend unreachable</div>',
#                 unsafe_allow_html=True,
#             )

#         st.markdown("")

#         if st.button("New workflow", use_container_width=True):
#             st.session_state.messages = []
#             st.session_state.pending_approval = None
#             st.session_state.workflow = None
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.rerun()

#         st.markdown('<div class="rail-heading">Capabilities</div>', unsafe_allow_html=True)
#         st.markdown("""
# <div class="capability"><div class="capability-name">Blog generation</div><div class="capability-desc">Drafts short structured posts from a topic.</div></div>
# <div class="capability"><div class="capability-name">Email automation</div><div class="capability-desc">Writes outbound messages for your review.</div></div>
# <div class="capability"><div class="capability-name">Dependency graphs</div><div class="capability-desc">Chains tasks that rely on each other's output.</div></div>
# <div class="capability"><div class="capability-name">Human approval</div><div class="capability-desc">Pauses before anything leaves the system.</div></div>
# """, unsafe_allow_html=True)

#         st.markdown('<div class="rail-heading" style="margin-top:20px;">Pipeline</div>', unsafe_allow_html=True)
#         st.markdown("""
# <div class="flow-line">request</div>
# <div class="flow-line">input guardrail</div>
# <div class="flow-line">planner</div>
# <div class="flow-line">dependency graph</div>
# <div class="flow-line">executor</div>
# <div class="flow-line">task workers</div>
# <div class="flow-line">human approval</div>
# <div class="flow-line terminal">gmail</div>
# """, unsafe_allow_html=True)

#         st.markdown('<div class="rail-heading" style="margin-top:20px;">Session</div>', unsafe_allow_html=True)
#         st.code(st.session_state.thread_id, language=None)

#         user_email = (
#             st.session_state.user.get("email", "Authenticated")
#             if st.session_state.user
#             else "Authenticated"
#         )
#         st.caption(user_email)

#         if st.button("Log out", use_container_width=True):
#             st.session_state.access_token = None
#             st.session_state.user = None
#             st.session_state.messages = []
#             st.session_state.pending_approval = None
#             st.session_state.workflow = None
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.rerun()


# # ============================================================
# # LOGIN SCREEN
# # ============================================================

# if not st.session_state.access_token:

#     st.markdown("""
# <div style="max-width:420px; margin:64px auto 0 auto;">
# <div style="display:flex; align-items:center; gap:11px; margin-bottom:30px;">
# <div class="brand-mark" style="width:38px; height:38px; font-size:14px;">AF</div>
# <div>
# <div style="font-weight:600; font-size:17px; color:var(--text);">AgentFlow</div>
# <div style="font-family:var(--mono); font-size:11.5px; color:var(--muted); margin-top:1px;">orchestration console</div>
# </div>
# </div>
# <div style="color:var(--text-dim); font-size:13.5px; line-height:1.6; margin-bottom:28px;">Sign in to plan, execute and approve automated workflows.</div>
# </div>
# """, unsafe_allow_html=True)

#     _, login_center, _ = st.columns([1, 1.3, 1])

#     with login_center:
#         with st.form("login_form"):
#             email = st.text_input("Email", placeholder="you@example.com")
#             password = st.text_input("Password", type="password", placeholder="Enter your password")
#             login_clicked = st.form_submit_button("Sign in", use_container_width=True)

#         if login_clicked:
#             if not email or not password:
#                 st.error("Enter your email and password.")
#             else:
#                 with st.spinner("Authenticating..."):
#                     if login_user(email, password):
#                         st.rerun()

#     st.stop()


# # ============================================================
# # SIDEBAR
# # ============================================================

# render_sidebar()


# # ============================================================
# # HEADER
# # ============================================================

# header_left, header_right = st.columns([4, 1])

# with header_left:
#     st.markdown("""
# <div class="console-header" style="border-bottom:none; margin-bottom:6px; padding-bottom:0;">
# <div>
# <h1 class="console-title">Command your workflow</h1>
# <div class="console-desc">Describe a task in plain language. AgentFlow plans it, executes it, and stops for your approval before anything leaves the system.</div>
# </div>
# </div>
# """, unsafe_allow_html=True)

# with header_right:
#     st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
#     if check_backend():
#         st.markdown(
#             '<div class="status-line ok"><span class="status-dot"></span>Operational</div>',
#             unsafe_allow_html=True,
#         )
#     else:
#         st.markdown(
#             '<div class="status-line err"><span class="status-dot"></span>Offline</div>',
#             unsafe_allow_html=True,
#         )

# st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

# render_stepper()

# render_tunnel_hero()


# # ============================================================
# # CHAT / EMPTY STATE
# # ============================================================

# if not st.session_state.messages:
#     render_cylinder_carousel()
#     st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
#     render_empty_state()

#     st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

#     prompt_col1, prompt_col2, prompt_col3 = st.columns(3)

#     with prompt_col1:
#         if st.button("Generate a blog", use_container_width=True):
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": "Generate a brief blog about AI agents.",
#             })
#             st.rerun()

#     with prompt_col2:
#         if st.button("Draft an email", use_container_width=True):
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": "Create an email about AI agents.",
#             })
#             st.rerun()

#     with prompt_col3:
#         if st.button("Blog, then email", use_container_width=True):
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": "Generate a brief blog about AI agents and email the generated blog.",
#             })
#             st.rerun()

#     st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# # ============================================================
# # MESSAGE HISTORY
# # ============================================================

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])


# # ============================================================
# # WORKFLOW + APPROVAL
# # ============================================================

# display_workflow(st.session_state.workflow)
# render_approval()


# # ============================================================
# # CHAT INPUT
# # ============================================================

# query = st.chat_input("Ask AgentFlow to research, create or automate...")


# # ============================================================
# # QUERY EXECUTION
# # ============================================================

# if query:

#     if st.session_state.pending_approval:
#         st.warning("Approve or reject the pending email first.")
#         st.stop()

#     st.session_state.messages.append({"role": "user", "content": query})

#     with st.chat_message("user"):
#         st.markdown(query)

#     with st.chat_message("assistant"):
#         start_time = time.time()

#         with st.spinner("Planning and executing..."):
#             result = send_message(query)

#         elapsed_time = time.time() - start_time
#         workflow = extract_workflow(result)
#         st.session_state.workflow = workflow

#         if result.get("error"):
#             answer = f"**Couldn't reach the workflow backend.**\n\n`{result['error']}`"
#             st.error(answer)

#         elif result.get("blocked"):
#             stage = result.get("stage", "security")
#             reason = result.get("reason", "Request blocked by a security guardrail.")

#             if stage == "input":
#                 answer = "**Request blocked.** The input guardrail stopped this request before it ran."
#             elif stage == "output":
#                 answer = "**Response blocked.** The output guardrail stopped the generated response."
#             else:
#                 answer = f"**Request blocked.**\n\n{reason}"

#             st.warning(answer)
#             st.caption(f"stage: {stage} · {elapsed_time:.2f}s")

#         elif result.get("success") and result.get("status") == "approval_required":
#             st.session_state.pending_approval = result
#             approval = result.get("approval", {})
#             email = approval.get("email", {})

#             answer = "**Paused for approval.** AgentFlow prepared the email and is waiting on your decision before it sends."
#             st.warning(answer)

#             if email:
#                 st.caption(f"prepared for {email.get('to', '')} · {elapsed_time:.2f}s")

#         elif result.get("success"):
#             data = result.get("data", {})
#             answer = data.get("response", "Workflow completed.")

#             completed_tasks = workflow.get("completed_tasks", [])
#             task_count = workflow.get("task_count", 0)

#             st.markdown(answer)
#             st.caption(f"{len(completed_tasks)} / {task_count} tasks completed · {elapsed_time:.2f}s")

#         else:
#             answer = "**Unexpected response from AgentFlow.**"
#             st.warning(answer)

#     st.session_state.messages.append({"role": "assistant", "content": answer})

#     if result.get("status") == "approval_required":
#         st.rerun()

# # ============================================================
# # BUTTON POINTER POLISH
# # ============================================================
# # Streamlit renders native buttons outside our custom components.
# # This tiny client-side enhancement gives them the same pointer-aware
# # "liquid carve" feel without changing their click/state semantics.
# components.html(
#     """
#     <script>
#     (() => {
#       const parent = window.parent;
#       const install = () => {
#         parent.document.querySelectorAll('.stButton > button').forEach(btn => {
#           if (btn.dataset.afMotion) return;
#           btn.dataset.afMotion = '1';
#           btn.addEventListener('pointermove', e => {
#             const r = btn.getBoundingClientRect();
#             btn.style.setProperty('--mx', `${e.clientX-r.left}px`);
#             btn.style.setProperty('--my', `${e.clientY-r.top}px`);
#           }, {passive:true});
#         });
#       };
#       install();
#       new MutationObserver(install).observe(parent.document.body, {subtree:true, childList:true});
#     })();
#     </script>
#     """,
#     height=0,
#     width=0,
# )


import time
import uuid

import requests
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# CONFIGURATION
# ============================================================

FASTAPI_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AgentFlow — Orchestration Console",
    page_icon="✦",
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

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: var(--sans);
}
.stApp { background-image: none !important; }
[data-testid="stMainBlockContainer"] { background: transparent !important; }
iframe { background: var(--bg) !important; }

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
  width: 48px;
  height: 48px;
  min-width: 48px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(232,163,61,.72);
  border-radius: 11px;
  color: var(--accent);
  background:
    radial-gradient(circle at 50% 42%, rgba(232,163,61,.12), transparent 58%),
    rgba(32,31,24,.78);
  box-shadow:
    0 0 24px rgba(232,163,61,.10),
    inset 0 0 18px rgba(232,163,61,.045),
    inset 0 1px 0 rgba(255,255,255,.08);
  position: relative;
  overflow: hidden;
}
.brand-mark::after {
  content: "";
  position: absolute;
  inset: -30%;
  background: linear-gradient(125deg, transparent 42%, rgba(255,202,117,.18) 49%, transparent 56%);
  transform: translateX(-55%);
  animation: brand-logo-sweep 4.8s ease-in-out infinite;
  pointer-events: none;
}
.brand-mark svg {
  width: 34px;
  height: 34px;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 0 7px rgba(255,190,80,.58));
}
@keyframes brand-logo-sweep {
  0%, 55% { transform: translateX(-55%); }
  78%, 100% { transform: translateX(55%); }
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

/* ---------------- cinematic bottom chat dock ---------------- */
[data-testid="stBottom"] {
  background: transparent !important;
  border-top: 0 !important;
  box-shadow: none !important;
  z-index: 1000 !important;
}

[data-testid="stBottom"] > div {
  background: transparent !important;
}

[data-testid="stBottom"]::before {
  content: "";
  position: absolute;
  left: -10vw;
  right: -10vw;
  bottom: 0;
  height: 132px;
  pointer-events: none;
  background:
    radial-gradient(ellipse at 18% 115%, rgba(232,163,61,.22), transparent 34%),
    radial-gradient(ellipse at 82% 115%, rgba(232,163,61,.16), transparent 34%),
    linear-gradient(180deg, rgba(3,5,6,0), rgba(3,5,6,.92) 70%, #030506 100%);
}

[data-testid="stBottom"]::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 76px;
  pointer-events: none;
  opacity: .9;
  background:
    radial-gradient(ellipse at 8% 100%, transparent 0 27%, rgba(232,163,61,.24) 27.3%, transparent 28.2%),
    radial-gradient(ellipse at 92% 100%, transparent 0 27%, rgba(232,163,61,.20) 27.3%, transparent 28.2%),
    linear-gradient(90deg, transparent 5%, rgba(232,163,61,.14) 24%, transparent 44%, transparent 56%, rgba(232,163,61,.14) 76%, transparent 95%);
  filter: blur(.15px);
}

[data-testid="stChatInput"] {
  position: relative !important;
  z-index: 1002 !important;
  max-width: 1180px !important;
  margin: 0 auto !important;
  padding: 10px 0 32px !important;
  background: transparent !important;
}

[data-testid="stChatInput"]::before {
  content: "";
  position: absolute;
  left: 7%;
  right: 7%;
  bottom: 12px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(232,163,61,.42), transparent);
  box-shadow: 0 0 18px rgba(232,163,61,.18);
  pointer-events: none;
}

[data-testid="stChatInput"]::after {
  content: "S T R A T E G I Z E   ·   B U I L D   ·   E X E C U T E   ·   I M P A C T";
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  color: rgba(238,215,172,.55);
  font: 500 8px var(--mono);
  letter-spacing: .26em;
  white-space: nowrap;
  pointer-events: none;
}

[data-testid="stChatInput"] > div {
  position: relative !important;
  z-index: 3 !important;
  min-height: 66px !important;
  background: linear-gradient(145deg, rgba(23,27,29,.96), rgba(7,10,12,.94)) !important;
  border: 1px solid rgba(255,210,125,.38) !important;
  border-radius: 17px !important;
  box-shadow:
    0 18px 55px rgba(0,0,0,.48),
    0 0 0 1px rgba(255,255,255,.025) inset,
    0 0 34px rgba(232,163,61,.08) !important;
  backdrop-filter: blur(18px) saturate(125%) !important;
  -webkit-backdrop-filter: blur(18px) saturate(125%) !important;
  transition: border-color .25s ease, box-shadow .25s ease, transform .25s ease !important;
}

[data-testid="stChatInput"] > div::before {
  content: "";
  position: absolute;
  left: 22px;
  right: 22px;
  top: -1px;
  height: 2px;
  border-radius: 99px;
  background: linear-gradient(90deg, transparent 0%, rgba(232,163,61,.18) 16%, #ffd27d 50%, rgba(232,163,61,.18) 84%, transparent 100%);
  box-shadow: 0 0 18px rgba(232,163,61,.32);
  animation: af-chat-scan 4.5s ease-in-out infinite;
  pointer-events: none;
}

[data-testid="stChatInput"] > div::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: 16px;
  background: linear-gradient(115deg, transparent 0 38%, rgba(255,210,125,.055) 46%, transparent 54%);
  transform: translateX(-115%);
  animation: af-chat-sweep 6s ease-in-out infinite;
  pointer-events: none;
}

[data-testid="stChatInput"] > div:focus-within {
  border-color: rgba(255,210,125,.72) !important;
  box-shadow:
    0 20px 65px rgba(0,0,0,.55),
    0 0 0 1px rgba(232,163,61,.16) inset,
    0 0 42px rgba(232,163,61,.16) !important;
  transform: translateY(-1px);
}

[data-testid="stChatInput"] textarea {
  color: #f2eee5 !important;
  font-family: var(--sans) !important;
  font-size: 14px !important;
  background: transparent !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: #777b7d !important;
}

[data-testid="stChatInput"] button {
  border-radius: 11px !important;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease !important;
}

[data-testid="stChatInput"] button:hover {
  transform: translateY(-1px) scale(1.025) !important;
  box-shadow: 0 0 24px rgba(232,163,61,.18) !important;
}

@keyframes af-chat-scan {
  0%, 100% { transform: scaleX(.18); opacity: .35; }
  50% { transform: scaleX(1); opacity: 1; }
}

@keyframes af-chat-sweep {
  0%, 55% { transform: translateX(-115%); }
  76%, 100% { transform: translateX(115%); }
}

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

/* ============================================================
   MOTION LAYER — premium interaction system
   ============================================================ */

:root {
  --glow-amber: rgba(232, 163, 61, .32);
  --glow-blue: rgba(108, 147, 168, .22);
  --glass: rgba(27, 26, 20, .72);
}

/* Smooth page entrance */
.main .block-container {
  animation: af-page-in .7s cubic-bezier(.22,1,.36,1) both;
}
@keyframes af-page-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Header typography gets a subtle scramble/glitch feel. */
.console-title {
  position: relative;
  text-shadow: 0 0 28px rgba(232,163,61,.08);
}
.console-title::after {
  content: "COMMAND YOUR WORKFLOW";
  position: absolute;
  inset: 0;
  color: var(--accent);
  opacity: 0;
  pointer-events: none;
  animation: af-title-flicker 5s ease-in-out infinite;
}
@keyframes af-title-flicker {
  0%, 86%, 100% { opacity: 0; transform: translateX(0); clip-path: inset(0 100% 0 0); }
  88% { opacity: .18; transform: translateX(1px); clip-path: inset(15% 0 55% 0); }
  90% { opacity: 0; transform: translateX(-1px); clip-path: inset(70% 0 8% 0); }
  92% { opacity: .10; transform: translateX(0); clip-path: inset(0 0 0 0); }
}

/* Glassier cards while retaining the original restrained console style. */
.stat-strip,
.task-row,
.result-row,
.approval-panel,
.empty {
  box-shadow: 0 18px 60px rgba(0,0,0,.13);
  backdrop-filter: blur(12px);
}
.task-row {
  transition: transform .25s cubic-bezier(.22,1,.36,1),
              border-color .25s ease,
              background .25s ease,
              box-shadow .25s ease;
}
.task-row:hover {
  transform: translateX(4px);
  background: var(--surface-hover);
  box-shadow: -8px 0 28px rgba(232,163,61,.045);
}
.result-row {
  transition: transform .25s cubic-bezier(.22,1,.36,1), border-color .25s ease;
}
.result-row:hover {
  transform: translateX(3px);
  border-color: var(--border-strong);
}

/* Premium Streamlit buttons inspired by the liquid-carve interaction. */
.stButton > button {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.015),
              0 8px 24px rgba(0,0,0,.10);
}
.stButton > button::before {
  content: "";
  position: absolute;
  width: 110px;
  height: 110px;
  left: var(--mx, 50%);
  top: var(--my, 50%);
  border-radius: 50%;
  transform: translate(-50%,-50%) scale(0);
  background: radial-gradient(circle, rgba(232,163,61,.22), rgba(232,163,61,0) 68%);
  transition: transform .45s cubic-bezier(.22,1,.36,1);
  pointer-events: none;
  z-index: -1;
}
.stButton > button:hover::before {
  transform: translate(-50%,-50%) scale(1.8);
}
.stButton > button:active {
  transform: scale(.985);
}
.stButton > button[kind="primaryFormSubmit"],
div[data-testid="stFormSubmitButton"] button {
  box-shadow: 0 8px 30px rgba(232,163,61,.13);
}

/* Animated status dot. */
.status-line .status-dot {
  animation: af-status-pulse 2.2s ease-in-out infinite;
}
@keyframes af-status-pulse {
  0%,100% { box-shadow: 0 0 0 0 currentColor; opacity: .8; }
  50% { box-shadow: 0 0 0 5px transparent; opacity: 1; }
}

/* Input focus glow */
[data-testid="stChatInput"] > div {
  transition: border-color .25s ease, box-shadow .25s ease, transform .25s ease;
}
[data-testid="stChatInput"] > div:focus-within {
  box-shadow: 0 0 0 1px rgba(232,163,61,.08), 0 12px 40px rgba(0,0,0,.18);
  transform: translateY(-1px);
}

/* ============================================================
   DOUBLE-STAIRS PRELOADER
   ============================================================ */
.af-preloader {
  position: fixed;
  inset: 0;
  z-index: 999999;
  background: #15140f;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.af-preloader::after {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 45%, rgba(232,163,61,.07), transparent 42%);
}
.af-preloader-copy {
  position: absolute;
  z-index: 4;
  text-align: center;
  color: #ece8db;
  font-family: 'IBM Plex Mono', monospace;
  letter-spacing: .18em;
  font-size: 10px;
  text-transform: uppercase;
  opacity: .65;
}
.af-stairs {
  position: absolute;
  inset: 0;
  display: flex;
  pointer-events: none;
}
.af-stair {
  flex: 1;
  background: #201f18;
  transform: scaleY(1);
  transform-origin: top;
}
.af-stairs.left .af-stair:nth-child(1) { transition-delay: .00s; }
.af-stairs.left .af-stair:nth-child(2) { transition-delay: .04s; }
.af-stairs.left .af-stair:nth-child(3) { transition-delay: .08s; }
.af-stairs.left .af-stair:nth-child(4) { transition-delay: .12s; }
.af-stairs.left .af-stair:nth-child(5) { transition-delay: .16s; }
.af-stairs.right .af-stair {
  transform-origin: bottom;
}
.af-stairs.right .af-stair:nth-child(1) { transition-delay: .16s; }
.af-stairs.right .af-stair:nth-child(2) { transition-delay: .12s; }
.af-stairs.right .af-stair:nth-child(3) { transition-delay: .08s; }
.af-stairs.right .af-stair:nth-child(4) { transition-delay: .04s; }
.af-stairs.right .af-stair:nth-child(5) { transition-delay: .00s; }
.af-preloader.is-out .af-stair {
  transform: scaleY(0);
  transition: transform .68s cubic-bezier(.77,0,.175,1);
}
.af-preloader.is-out .af-preloader-copy {
  opacity: 0;
  transform: translateY(-8px);
  transition: opacity .25s ease, transform .25s ease;
}

/* ============================================================
   TUNNEL / THREE.JS HERO
   ============================================================ */
.af-tunnel-shell {
  position: relative;
  width: 100%;
  height: 285px;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #090a0a;
  margin: 0 0 25px;
  box-shadow: inset 0 0 90px rgba(0,0,0,.55), 0 20px 70px rgba(0,0,0,.18);
}
.af-tunnel-shell iframe {
  width: 100%;
  height: 100%;
  border: 0;
}
.af-tunnel-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(21,20,15,.62), transparent 35%, transparent 65%, rgba(21,20,15,.48)),
    linear-gradient(0deg, rgba(21,20,15,.48), transparent 35%);
}
.af-tunnel-caption {
  position: absolute;
  left: 22px;
  bottom: 18px;
  z-index: 2;
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: .13em;
  text-transform: uppercase;
  color: rgba(236,232,219,.58);
}
.af-tunnel-caption b {
  color: var(--accent);
  font-weight: 500;
}

/* ============================================================
   CYLINDER CAROUSEL
   ============================================================ */
.af-cylinder {
  position: relative;
  height: 205px;
  margin: 0 0 22px;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 10px;
  background:
    radial-gradient(ellipse at center, rgba(232,163,61,.055), transparent 52%),
    var(--bg-raised);
  perspective: 850px;
  cursor: grab;
}
.af-cylinder:active { cursor: grabbing; }
.af-cylinder::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  width: 44%;
  height: 1px;
  transform: translate(-50%,-50%);
  background: linear-gradient(90deg, transparent, rgba(232,163,61,.28), transparent);
}
.af-cylinder-track {
  position: absolute;
  inset: 0;
  transform-style: preserve-3d;
}
.af-cylinder-card {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 190px;
  height: 112px;
  padding: 15px;
  box-sizing: border-box;
  border: 1px solid var(--border);
  border-radius: 9px;
  background: rgba(32,31,24,.91);
  backdrop-filter: blur(8px);
  transform-style: preserve-3d;
  transition: transform .08s linear, opacity .08s linear, border-color .25s ease;
  box-shadow: 0 20px 45px rgba(0,0,0,.18);
}
.af-cylinder-card strong {
  display: block;
  font-size: 12px;
  color: var(--text);
  margin-bottom: 7px;
}
.af-cylinder-card small {
  display: block;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 9.5px;
  line-height: 1.55;
}
.af-cylinder-card .af-card-index {
  color: var(--accent);
  font-family: var(--mono);
  font-size: 9px;
  margin-bottom: 9px;
}
.af-cylinder-hint {
  position: absolute;
  right: 15px;
  bottom: 13px;
  z-index: 3;
  font-family: var(--mono);
  font-size: 9px;
  color: var(--muted);
}

/* Responsive polish */
@media (max-width: 900px) {
  .af-tunnel-shell { height: 235px; }
  .af-cylinder { height: 185px; }

  [data-testid="stChatInput"] {
    width: calc(100% - 24px) !important;
    padding-bottom: 28px !important;
  }

  [data-testid="stChatInput"]::after {
    font-size: 7px;
    letter-spacing: .18em;
  }
}
@media (prefers-reduced-motion: reduce) {
  .main .block-container,
  .status-line .status-dot,
  .console-title::after,
  [data-testid="stChatInput"] > div::before,
  [data-testid="stChatInput"] > div::after {
    animation: none !important;
  }
  .task-row, .result-row, .stButton > button {
    transition: none !important;
  }
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
# MOTION COMPONENTS
# ============================================================

def render_double_stairs_preloader():
    """One-shot Skiper-inspired double-stairs page preloader."""
    if st.session_state.get("preloader_seen"):
        return

    components.html(
        """
        <style>
          html, body { margin:0; padding:0; background:transparent; overflow:hidden; }
          .p { position:fixed; inset:0; z-index:999999; background:#15140f; overflow:hidden; }
          .stairs { position:absolute; inset:0; display:flex; }
          .side { flex:1; display:flex; }
          .side.r { flex-direction:row-reverse; }
          .s { flex:1; background:#201f18; transform:scaleY(1); }
          .l .s { transform-origin:top; }
          .r .s { transform-origin:bottom; }
          .l .s:nth-child(1){transition-delay:0s}.l .s:nth-child(2){transition-delay:.04s}
          .l .s:nth-child(3){transition-delay:.08s}.l .s:nth-child(4){transition-delay:.12s}
          .l .s:nth-child(5){transition-delay:.16s}
          .r .s:nth-child(1){transition-delay:.16s}.r .s:nth-child(2){transition-delay:.12s}
          .r .s:nth-child(3){transition-delay:.08s}.r .s:nth-child(4){transition-delay:.04s}
          .r .s:nth-child(5){transition-delay:0s}
          .p.out .s { transform:scaleY(0); transition:transform .72s cubic-bezier(.77,0,.175,1); }
          .copy {
            position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
            color:#ece8db; font:500 10px/1.4 "Courier New",monospace;
            letter-spacing:.22em; text-transform:uppercase; text-align:center;
            transition:opacity .25s ease, transform .25s ease;
          }
          .copy b { display:block; color:#e8a33d; font-size:18px; letter-spacing:.08em; margin-bottom:8px; }
          .p.out .copy { opacity:0; transform:translate(-50%,-58%); }
        </style>
        <div class="p" id="p">
          <div class="stairs l"><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i></div>
          <div class="stairs r"><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i><i class="s"></i></div>
          <div class="copy"><b>AF</b>initializing orchestration</div>
        </div>
        <script>
          const p=document.getElementById("p");
          setTimeout(()=>p.classList.add("out"),1150);
          setTimeout(()=>{ p.style.display="none"; document.body.style.overflow="auto"; },2050);
        </script>
        """,
        height=0,
        width=0,
    )
    st.session_state.preloader_seen = True


# The function must be defined before it is called.
render_double_stairs_preloader()


def render_tunnel_hero():
    """Three.js gallery tunnel inspired by the supplied Gallery Tunnel component."""
    components.html(
        """
        <style>
          html,body{margin:0;padding:0;background:#15140f !important;overflow:hidden}
          #wrap{position:relative;width:100%;height:285px;background:#090a0a;border-radius:12px;overflow:hidden}
          canvas{display:block;width:100%;height:100%}
          .v{position:absolute;inset:0;pointer-events:none;
             background:linear-gradient(90deg,rgba(21,20,15,.64),transparent 36%,transparent 64%,rgba(21,20,15,.48)),
                        linear-gradient(0deg,rgba(21,20,15,.52),transparent 38%)}
          .caption{position:absolute;left:22px;bottom:18px;color:rgba(236,232,219,.58);
                   font:10px/1 "Courier New",monospace;letter-spacing:.13em;text-transform:uppercase}
          .caption b{color:#e8a33d;font-weight:500}
          .reticle{position:absolute;left:50%;top:50%;width:12px;height:12px;transform:translate(-50%,-50%);
                   border:1px solid rgba(232,163,61,.45);border-radius:50%;box-shadow:0 0 22px rgba(232,163,61,.18)}
        </style>
        <div id="wrap">
          <canvas id="c"></canvas><div class="v"></div><div class="reticle"></div>
          <div class="caption"><b>LIVE /</b> execution tunnel · pointer accelerates traversal</div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
        <script>
        (() => {
          const root=document.getElementById("wrap"), canvas=document.getElementById("c");
          if(!window.THREE) return;
          const T=THREE, scene=new T.Scene();
          scene.background=new T.Color(0x090a0a);
          scene.fog=new T.Fog(0x090a0a,7,22);
          const camera=new T.PerspectiveCamera(48,1,.1,100);
          camera.position.set(0,0,0);

          const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:"high-performance"});
          renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));

          const group=new T.Group(); scene.add(group);
          const mats=[
            new T.MeshBasicMaterial({color:0xe8a33d,transparent:true,opacity:.16}),
            new T.MeshBasicMaterial({color:0x6c93a8,transparent:true,opacity:.12}),
            new T.MeshBasicMaterial({color:0x6fa287,transparent:true,opacity:.11})
          ];
          const lineMat=new T.LineBasicMaterial({color:0x777363,transparent:true,opacity:.32});
          const slabGeo=new T.PlaneGeometry(1.15,.72);
          const segments=[];
          const depth=1.25, count=17, width=5.2, height=3.4;

          function makeSegment(z){
            const g=new T.Group(); g.position.z=z;
            const pts=[];
            for(let x=-width/2;x<=width/2+.001;x+=width/4){
              pts.push(new T.Vector3(x,-height/2,0),new T.Vector3(x,height/2,0));
            }
            for(let y=-height/2;y<=height/2+.001;y+=height/4){
              pts.push(new T.Vector3(-width/2,y,0),new T.Vector3(width/2,y,0));
            }
            const geo=new T.BufferGeometry().setFromPoints(pts);
            g.add(new T.LineSegments(geo,lineMat));
            for(let i=0;i<5;i++){
              const slab=new T.Mesh(slabGeo,mats[(i+Math.floor(-z/depth))%mats.length]);
              slab.position.set((Math.random()-.5)*4.1,(Math.random()-.5)*2.55,-.01);
              slab.rotation.z=(Math.random()-.5)*.22;
              slab.scale.setScalar(.55+Math.random()*.55);
              g.add(slab);
            }
            return g;
          }
          for(let i=0;i<count;i++){const g=makeSegment(-i*depth);scene.add(g);segments.push(g);}

          const mouse={x:0,y:0,tx:0,ty:0};
          let down=false, speed=.055, last=performance.now();

          root.addEventListener("pointermove",e=>{
            const r=root.getBoundingClientRect();
            mouse.tx=(e.clientX-r.left)/r.width*2-1;
            mouse.ty=-((e.clientY-r.top)/r.height*2-1);
            if(down) speed=.105;
          });
          root.addEventListener("pointerenter",()=>speed=.075);
          root.addEventListener("pointerleave",()=>{mouse.tx=0;mouse.ty=0;down=false;speed=.055});
          root.addEventListener("pointerdown",()=>{down=true;speed=.12});
          window.addEventListener("pointerup",()=>{down=false});

          function resize(){
            const w=Math.max(1,root.clientWidth),h=Math.max(1,root.clientHeight);
            camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);
          }
          new ResizeObserver(resize).observe(root); resize();

          function tick(now){
            requestAnimationFrame(tick);
            const dt=Math.min(.04,(now-last)/1000);last=now;
            mouse.x+=(mouse.tx-mouse.x)*Math.min(1,dt*5);
            mouse.y+=(mouse.ty-mouse.y)*Math.min(1,dt*5);
            camera.position.x=mouse.x*.32;
            camera.position.y=mouse.y*.20;
            camera.rotation.z=-mouse.x*.012;
            camera.rotation.y=mouse.x*.035;
            camera.rotation.x=-mouse.y*.025;

            const dz=speed*dt*60;
            for(const seg of segments){
              seg.position.z+=dz;
              if(seg.position.z>1.3) seg.position.z-=count*depth;
              seg.children.forEach((m,j)=>{
                if(m.isMesh) m.rotation.z += dt*(.04+(j%3)*.018);
              });
            }
            renderer.render(scene,camera);
          }
          requestAnimationFrame(tick);
        })();
        </script>
        """,
        height=285,
        width=None,
    )


def render_cylinder_carousel():
    """Interactive CSS 3D cylinder carousel for the empty-state prompt deck."""
    cards = [
        ("01", "Planner", "decomposes natural-language requests into executable tasks"),
        ("02", "Executor", "runs dependency-aware workers in the correct order"),
        ("03", "Guardrails", "checks requests and generated output before delivery"),
        ("04", "Approval", "pauses external actions until you explicitly approve"),
        ("05", "Delivery", "hands completed work to the connected destination"),
        ("06", "Observability", "keeps task status, timing and results visible"),
    ]
    cards_json = str([{"i":a,"t":b,"d":c} for a,b,c in cards]).replace("'", '"')
    components.html(
        f"""
        <style>
          html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
          #stage{{position:absolute;inset:0;width:auto;height:auto;overflow:hidden;border:1px solid #34322a;border-radius:10px;
            background:radial-gradient(ellipse at center,rgba(232,163,61,.055),transparent 52%),#1b1a14;
            perspective:850px;cursor:grab;user-select:none}}
          #stage:active{{cursor:grabbing}}
          #track{{position:absolute;inset:0;transform-style:preserve-3d}}
          .card{{position:absolute;left:50%;top:50%;width:190px;height:112px;padding:15px;box-sizing:border-box;
            border:1px solid #34322a;border-radius:9px;background:rgba(32,31,24,.92);backdrop-filter:blur(8px);
            box-shadow:0 20px 45px rgba(0,0,0,.18);transform-style:preserve-3d;}}
          .ix{{color:#e8a33d;font:9px "Courier New",monospace;margin-bottom:9px}}
          .tt{{color:#ece8db;font:600 12px system-ui;margin-bottom:7px}}
          .dd{{color:#726f60;font:9.5px/1.55 "Courier New",monospace}}
          .hint{{position:absolute;right:15px;bottom:13px;color:#726f60;font:9px "Courier New",monospace}}
          .line{{position:absolute;left:50%;top:50%;width:44%;height:1px;transform:translate(-50%,-50%);
            background:linear-gradient(90deg,transparent,rgba(232,163,61,.28),transparent)}}
        </style>
        <div id="stage"><div class="line"></div><div id="track"></div><div class="hint">DRAG / SCROLL TO EXPLORE</div></div>
        <script>
        (()=>{{
          const data={cards_json},stage=document.getElementById("stage"),track=document.getElementById("track");
          const els=data.map((d)=>{{
            const e=document.createElement("div");e.className="card";
            e.innerHTML=`<div class="ix">${{d.i}}</div><div class="tt">${{d.t}}</div><div class="dd">${{d.d}}</div>`;
            track.appendChild(e);return e;
          }});
          let offset=0,target=0,down=false,lastX=0;
          function render(){{
            const n=els.length, step=58, radius=250;
            els.forEach((e,i)=>{{
              let rel=i-offset;
              rel=((rel+n/2)%n+n)%n-n/2;
              const a=rel*step*Math.PI/180;
              const x=Math.sin(a)*radius;
              const z=(Math.cos(a)-1)*radius;
              const scale=.58+.42*Math.max(0,Math.cos(a));
              const op=.28+.72*Math.max(0,Math.cos(a));
              e.style.transform=`translate(-50%,-50%) translate3d(${{x}}px,0,${{z}}px) scale(${{scale}})`;
              e.style.opacity=op;
              e.style.zIndex=String(Math.round(100+Math.cos(a)*100));
            }});
            offset+=(target-offset)*.075;
            requestAnimationFrame(render);
          }}
          stage.addEventListener("pointerdown",e=>{{down=true;lastX=e.clientX;stage.setPointerCapture?.(e.pointerId)}});
          stage.addEventListener("pointermove",e=>{{if(!down)return;target-=(e.clientX-lastX)/42;lastX=e.clientX}});
          stage.addEventListener("pointerup",()=>down=false);
          stage.addEventListener("pointercancel",()=>down=false);
          stage.addEventListener("wheel",e=>{{e.preventDefault();target+=e.deltaY*.008}},{{passive:false}});
          render();
        }})();
        </script>
        """,
        height=205,
        width=None,
    )


# ============================================================
# UI COMPONENTS
# ============================================================

def render_brand():
    st.markdown("""
<div class="brand">
<div class="brand-mark" aria-label="AgentFlow logo">
<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<path d="M20 57 L50 30 L63 44 L36 68" stroke="#FFD27D" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M63 44 L80 20" stroke="#FFD27D" stroke-width="9" stroke-linecap="round"/>
<path d="M63 44 L80 68" stroke="#FFD27D" stroke-width="9" stroke-linecap="round"/>
</svg>
</div>
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
# LOGIN SCREEN — CINEMATIC AGENTFLOW
# ============================================================

if not st.session_state.access_token:
    # Hide the application chrome while the cinematic login is active.
    st.markdown("""
<style>
/* ============================================================
   FULL-SCREEN CINEMATIC LOGIN
   Inspired by the supplied AgentFlow reference + the motion
   components: gallery tunnel, text-scramble/glitch, liquid glow,
   double-stairs reveal and cinematic parallax.
   ============================================================ */

[data-testid="stSidebar"] { display:none !important; }
.block-container {
  max-width:none !important;
  padding:0 !important;
  margin:0 !important;
}
[data-testid="stMainBlockContainer"] { padding:0 !important; }
body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  overflow:hidden !important;
  background:#030506 !important;
}

.af-login-world {
  position:fixed; inset:0; z-index:0; overflow:hidden;
  background:
    radial-gradient(circle at 50% 43%, rgba(255,171,57,.18), transparent 15%),
    radial-gradient(circle at 50% 55%, rgba(21,71,103,.13), transparent 38%),
    linear-gradient(180deg,#020405 0%,#05080b 55%,#020304 100%);
  perspective:1000px;
}
.af-login-world::before {
  content:""; position:absolute; inset:-25%;
  background:
    linear-gradient(rgba(246,174,68,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(246,174,68,.035) 1px,transparent 1px);
  background-size:52px 52px;
  transform:perspective(800px) rotateX(61deg) translateY(23%) scale(1.35);
  transform-origin:center bottom;
  animation:af-floor 8s linear infinite;
  opacity:.9;
}
.af-login-world::after {
  content:""; position:absolute; left:50%; top:43%;
  width:min(58vw,760px); aspect-ratio:1;
  transform:translate(-50%,-50%);
  border-radius:50%;
  background:radial-gradient(circle,rgba(255,181,69,.12),rgba(255,181,69,.025) 32%,transparent 68%);
  filter:blur(10px);
  animation:af-core 4s ease-in-out infinite;
}
@keyframes af-floor { from{background-position:0 0,0 0} to{background-position:0 52px,52px 0} }
@keyframes af-core { 0%,100%{transform:translate(-50%,-50%) scale(.92);opacity:.65} 50%{transform:translate(-50%,-50%) scale(1.08);opacity:1} }

/* 3D gallery-tunnel walls */
.af-tunnel {
  position:absolute; inset:0; transform-style:preserve-3d;
  animation:af-breathe 6s ease-in-out infinite;
}
@keyframes af-breathe { 0%,100%{transform:scale(1)} 50%{transform:scale(1.015)} }
.af-wall { position:absolute; top:0; bottom:0; width:50%; overflow:hidden; opacity:.9; }
.af-wall.left { left:0; background:linear-gradient(90deg,#020304 0%,rgba(4,10,15,.5) 62%,transparent); }
.af-wall.right { right:0; background:linear-gradient(270deg,#020304 0%,rgba(4,10,15,.5) 62%,transparent); }

.af-panel {
  position:absolute; width:150px; height:205px;
  border:1px solid rgba(115,160,191,.35);
  background:linear-gradient(145deg,rgba(19,49,68,.48),rgba(5,13,19,.72));
  box-shadow:0 0 35px rgba(34,104,147,.09), inset 0 0 25px rgba(255,255,255,.025);
  overflow:hidden;
  animation:af-panel-float 5s ease-in-out infinite;
}
.af-panel::before {
  content:""; position:absolute; inset:0;
  background:linear-gradient(125deg,transparent 0 42%,rgba(255,190,91,.16) 47%,transparent 53%),
             linear-gradient(0deg,transparent,rgba(255,255,255,.04));
  animation:af-panel-scan 3.8s linear infinite;
}
.af-panel::after {
  content:""; position:absolute; left:10%; right:10%; top:16%; bottom:16%;
  border:1px solid rgba(232,163,61,.16);
  background:repeating-linear-gradient(180deg,rgba(255,255,255,.07) 0 1px,transparent 1px 8px);
  opacity:.45;
}
@keyframes af-panel-float { 0%,100%{transform:translateY(0) rotateY(-7deg)} 50%{transform:translateY(-12px) rotateY(-3deg)} }
@keyframes af-panel-scan { from{transform:translateX(-110%)} to{transform:translateX(110%)} }

.af-left .p1{left:5%;top:16%;transform:rotateY(28deg) rotateZ(-2deg);animation-delay:-1s}
.af-left .p2{left:20%;top:34%;transform:scale(.78) rotateY(25deg);animation-delay:-3s}
.af-left .p3{left:8%;top:58%;transform:scale(.66) rotateY(25deg);animation-delay:-2s}
.af-left .p4{left:30%;top:13%;transform:scale(.56) rotateY(23deg);animation-delay:-4s}
.af-right .p1{right:5%;top:18%;transform:rotateY(-28deg) rotateZ(2deg);animation-delay:-2s}
.af-right .p2{right:21%;top:39%;transform:scale(.78) rotateY(-25deg);animation-delay:-4s}
.af-right .p3{right:7%;top:61%;transform:scale(.66) rotateY(-25deg);animation-delay:-1s}
.af-right .p4{right:31%;top:12%;transform:scale(.56) rotateY(-23deg);animation-delay:-3s}

/* Decorative panel content */
.af-panel-art { position:absolute; inset:0; display:grid; place-items:center; color:rgba(220,239,249,.68); font:10px var(--mono); letter-spacing:.16em; text-align:center; }
.af-planet { width:70px;height:70px;border-radius:50%;border:1px solid rgba(111,184,220,.55); box-shadow:inset -13px -5px 25px rgba(17,84,121,.8),0 0 25px rgba(51,143,193,.22); position:relative; }
.af-planet::after { content:"";position:absolute;inset:8px;border-radius:50%;border:1px dashed rgba(232,163,61,.35);animation:af-spin 5s linear infinite; }
.af-orbit-art { width:72px;height:72px;border:1px solid rgba(102,183,224,.5);border-radius:50%;box-shadow:0 0 25px rgba(65,157,210,.22);position:relative; }
.af-orbit-art::before,.af-orbit-art::after { content:"";position:absolute;inset:12px;border:1px solid rgba(232,163,61,.4);border-radius:50%;transform:rotate(55deg); }
.af-orbit-art::after { inset:24px; }
@keyframes af-spin { to{transform:rotate(360deg)} }

/* Perspective tunnel rails */
.af-rail { position:absolute; left:50%; top:0; width:1px; height:100%; background:linear-gradient(transparent,rgba(232,163,61,.42),transparent); transform-origin:center; opacity:.38; }
.af-rail.r1{transform:translateX(-360px) rotateY(67deg)}
.af-rail.r2{transform:translateX(360px) rotateY(-67deg)}
.af-rail.r3{transform:translateX(-190px) rotateY(78deg);opacity:.22}
.af-rail.r4{transform:translateX(190px) rotateY(-78deg);opacity:.22}

/* Fast-moving light streaks */
.af-streak { position:absolute; width:3px; height:65px; border-radius:99px; background:linear-gradient(180deg,transparent,#ffc56d,transparent); box-shadow:0 0 18px rgba(255,180,66,.9); opacity:.7; animation:af-streak 2.5s linear infinite; }
@keyframes af-streak { from{transform:translate3d(0,-30vh,0) rotate(18deg);opacity:0} 12%{opacity:.8} to{transform:translate3d(0,125vh,0) rotate(18deg);opacity:0} }
.af-s1{left:12%;animation-delay:-.3s}.af-s2{left:24%;animation-delay:-1.7s}.af-s3{left:39%;animation-delay:-2.2s}.af-s4{left:61%;animation-delay:-.9s}.af-s5{left:77%;animation-delay:-2.7s}.af-s6{left:89%;animation-delay:-1.2s}

/* Fine particles */
.af-dot { position:absolute;width:2px;height:2px;border-radius:50%;background:#ffd184;box-shadow:0 0 12px #e8a33d;animation:af-dot 5s ease-in-out infinite;opacity:.5; }
@keyframes af-dot { 0%,100%{transform:translate3d(0,0,0);opacity:.15}50%{transform:translate3d(18px,-28px,0) scale(2);opacity:.9} }
.af-d1{left:16%;top:30%;animation-delay:-1s}.af-d2{left:83%;top:29%;animation-delay:-3s}.af-d3{left:27%;top:77%;animation-delay:-2s}.af-d4{left:72%;top:70%;animation-delay:-4s}.af-d5{left:51%;top:18%;animation-delay:-2.5s}.af-d6{left:45%;top:84%;animation-delay:-.5s}

/* Login content */
.af-login-content {
  position:relative;
  z-index:20;
  width:min(530px,92vw);
  margin:0 auto;
  padding-top:19vh;
  box-sizing:border-box;
  text-align:center;
  animation:af-enter 1.15s cubic-bezier(.22,1,.36,1) both;
}
@keyframes af-enter { from{opacity:0;transform:translateY(28px) scale(.98);filter:blur(12px)} to{opacity:1;transform:none;filter:none} }
.af-brand-logo {
  width:72px;height:72px;margin-bottom:15px;position:relative;display:grid;place-items:center;
  animation:af-logo 3.2s ease-in-out infinite;
}
.af-brand-logo::before { content:"";position:absolute;inset:0;border:1px solid rgba(255,194,102,.55);border-radius:16px;box-shadow:0 0 45px rgba(232,163,61,.18),inset 0 0 25px rgba(232,163,61,.06); }
.af-brand-logo svg { width:48px;height:48px;filter:drop-shadow(0 0 12px rgba(255,190,80,.65)); }
@keyframes af-logo { 0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-5px) rotate(2deg)} }
.af-login-title { margin:0; font-size:clamp(34px,5vw,52px);line-height:1;letter-spacing:-1.8px;font-weight:600;color:#f4f0e7;text-shadow:0 0 35px rgba(255,177,67,.13); }
.af-login-title .gold { color:#ffc66e; }
.af-login-kicker { margin:13px 0 8px;color:#d1c9b8;font:500 10px var(--mono);letter-spacing:.25em;text-transform:uppercase; }
.af-login-desc { margin:0;color:#9c9a94;font-size:13px;text-align:center; line-height:1.5; }
.af-login-card {
  position:relative;width:min(450px,100%);padding:30px 30px 22px;box-sizing:border-box;
  border:1px solid rgba(159,177,187,.42);border-radius:18px;
  background:linear-gradient(145deg,rgba(14,20,23,.72),rgba(7,10,12,.62));
  backdrop-filter:blur(20px) saturate(120%);-webkit-backdrop-filter:blur(20px) saturate(120%);
  box-shadow:0 30px 100px rgba(0,0,0,.62),0 0 65px rgba(232,163,61,.10),inset 0 1px 0 rgba(255,255,255,.12);
  overflow:hidden;
}
.af-login-card::before { content:"";position:absolute;left:8%;right:8%;top:0;height:2px;background:linear-gradient(90deg,transparent,#ffc66e,transparent);filter:blur(.2px);animation:af-scan 3.6s ease-in-out infinite; }
.af-login-card::after { content:"";position:absolute;inset:0;background:linear-gradient(115deg,transparent 0 35%,rgba(255,255,255,.045) 43%,transparent 51%);transform:translateX(-120%);animation:af-glass-sweep 5.5s ease-in-out infinite;pointer-events:none; }
@keyframes af-scan {0%,100%{transform:scaleX(.2);opacity:.3}50%{transform:scaleX(1);opacity:1}}
@keyframes af-glass-sweep { 0%,55%{transform:translateX(-120%)}75%,100%{transform:translateX(120%)} }

/* Streamlit form becomes the glass card */
div[data-testid="stForm"] {
  position:relative !important;
  z-index:50 !important;
  width:min(450px,92vw) !important;
  margin:22px auto 0 !important;
  padding:30px 30px 22px !important;
  box-sizing:border-box !important;
  border:1px solid rgba(159,177,187,.42) !important;
  border-radius:18px !important;
  background:linear-gradient(145deg,rgba(14,20,23,.88),rgba(7,10,12,.82)) !important;
  backdrop-filter:blur(20px) saturate(120%) !important;
  -webkit-backdrop-filter:blur(20px) saturate(120%) !important;
  box-shadow:0 30px 100px rgba(0,0,0,.62),0 0 65px rgba(232,163,61,.10),inset 0 1px 0 rgba(255,255,255,.12) !important;
  animation:af-card 1s .25s cubic-bezier(.22,1,.36,1) both;
}
@keyframes af-card {from{opacity:0;transform:translateY(22px) scale(.97)}to{opacity:1;transform:none}}
div[data-testid="stForm"] label { color:#ddd6c8 !important;font-size:12px !important;font-weight:500 !important;letter-spacing:.01em !important; }
div[data-testid="stForm"] input {
  color:#f4f0e7 !important;background:rgba(3,6,8,.58) !important;
  border:1px solid rgba(124,142,153,.38) !important;border-radius:10px !important;
  min-height:48px !important;transition:all .25s ease !important;
}
div[data-testid="stForm"] input:hover {border-color:rgba(255,194,102,.45) !important;box-shadow:0 0 20px rgba(232,163,61,.05) !important;}
div[data-testid="stForm"] input:focus {border-color:#e8a33d !important;box-shadow:0 0 0 1px rgba(232,163,61,.18),0 0 30px rgba(232,163,61,.12) !important;transform:translateY(-1px);}
div[data-testid="stForm"] input::placeholder {color:#666c70 !important;}
div[data-testid="stFormSubmitButton"] button {
  min-height:50px !important;border-radius:10px !important;border:1px solid rgba(255,221,160,.75) !important;
  background:linear-gradient(110deg,#e7a33d,#ffd27d,#e7a33d) !important;background-size:220% 100% !important;
  color:#161109 !important;font-weight:700 !important;font-size:14px !important;
  box-shadow:0 12px 45px rgba(232,163,61,.22),inset 0 1px 0 rgba(255,255,255,.45) !important;
  animation:af-button 3s ease-in-out infinite !important;transition:transform .2s ease,box-shadow .2s ease !important;
}
div[data-testid="stFormSubmitButton"] button:hover {transform:translateY(-2px) !important;box-shadow:0 18px 55px rgba(232,163,61,.36),inset 0 1px 0 rgba(255,255,255,.55) !important;}
div[data-testid="stFormSubmitButton"] button:active {transform:scale(.985) !important;}
@keyframes af-button {0%,100%{background-position:0 50%}50%{background-position:100% 50%}}
.af-secure { display:flex;align-items:center;justify-content:center;gap:9px;margin-top:18px;color:#77766f;font:9px var(--mono);letter-spacing:.15em;text-transform:uppercase; }
.af-secure::before,.af-secure::after {content:"";height:1px;width:74px;background:linear-gradient(90deg,transparent,rgba(150,150,150,.25));}.af-secure::after{transform:rotate(180deg)}
.af-side-label {position:fixed;z-index:8;color:rgba(227,220,204,.38);font:10px var(--mono);letter-spacing:.27em;text-transform:uppercase;line-height:3.2;}
.af-side-label.left{left:4vw;top:38%}.af-side-label.right{right:4vw;top:40%;text-align:right}
.af-corner {position:fixed;z-index:8;color:rgba(227,220,204,.34);font:9px var(--mono);letter-spacing:.18em;text-transform:uppercase;}
.af-corner.tl{left:3vw;top:4vh}.af-corner.tr{right:3vw;top:4vh}.af-corner.bl{left:3vw;bottom:4vh}.af-corner.br{right:3vw;bottom:4vh;text-align:right}

@media(max-width:800px){
  .af-panel{opacity:.48;transform:scale(.62) !important}
  .af-side-label{display:none}
  .af-corner{font-size:7px}
  .af-login-content{width:92vw;padding-top:12vh}
  .af-login-title{font-size:37px}
  div[data-testid="stForm"]{width:92vw !important;padding:24px 20px 18px !important}
}
@media(prefers-reduced-motion:reduce){
  .af-login-world::before,.af-login-world::after,.af-tunnel,.af-panel,.af-panel::before,.af-planet::after,.af-login-content,.af-brand-logo,div[data-testid="stForm"],div[data-testid="stFormSubmitButton"] button,.af-streak,.af-dot{animation:none !important}
}
</style>

<div class="af-login-world">
  <div class="af-tunnel">
    <div class="af-wall left af-left">
      <div class="af-panel p1"><div class="af-panel-art"><div class="af-planet"></div></div></div>
      <div class="af-panel p2"><div class="af-panel-art">AI<br>AGENTS</div></div>
      <div class="af-panel p3"><div class="af-panel-art">IDEAS<br>TO IMPACT</div></div>
      <div class="af-panel p4"><div class="af-panel-art">CODE<br>• • • •</div></div>
    </div>
    <div class="af-wall right af-right">
      <div class="af-panel p1"><div class="af-panel-art"><div class="af-orbit-art"></div></div></div>
      <div class="af-panel p2"><div class="af-panel-art">REAL<br>IMPACT</div></div>
      <div class="af-panel p3"><div class="af-panel-art">FASTER<br>WORKFLOWS</div></div>
      <div class="af-panel p4"><div class="af-panel-art">VALIDATE<br>DELIVER</div></div>
    </div>
    <div class="af-rail r1"></div><div class="af-rail r2"></div><div class="af-rail r3"></div><div class="af-rail r4"></div>
  </div>
  <div class="af-streak af-s1"></div><div class="af-streak af-s2"></div><div class="af-streak af-s3"></div><div class="af-streak af-s4"></div><div class="af-streak af-s5"></div><div class="af-streak af-s6"></div>
  <div class="af-dot af-d1"></div><div class="af-dot af-d2"></div><div class="af-dot af-d3"></div><div class="af-dot af-d4"></div><div class="af-dot af-d5"></div><div class="af-dot af-d6"></div>
</div>

<div class="af-side-label left">PLAN<br>EXECUTE<br>VALIDATE<br>DELIVER</div>
<div class="af-side-label right">AI AGENTS<br>REAL IMPACT<br>FASTER WORKFLOWS</div>
<div class="af-corner tl">[ AGENTFLOW ] / SECURE ACCESS</div>
<div class="af-corner tr">BUILT FOR<br>WHAT'S NEXT&nbsp;&nbsp;✦</div>
<div class="af-corner bl">“Human insight<br>AI execution<br>Real impact.”</div>
<div class="af-corner br">[ AGENTFLOW ]<br>AUTOMATE BEYOND LIMITS</div>

<div class="af-login-content">
  <div class="af-brand-logo" aria-label="AgentFlow logo">
    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M20 57 L50 30 L63 44 L36 68" stroke="#FFD27D" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M63 44 L80 20" stroke="#FFD27D" stroke-width="9" stroke-linecap="round"/>
      <path d="M63 44 L80 68" stroke="#FFD27D" stroke-width="9" stroke-linecap="round"/>
    </svg>
  </div>
  <h1 class="af-login-title">Agent<span class="gold">Flow</span></h1>
  <div class="af-login-kicker">ORCHESTRATION CONSOLE · SECURE ACCESS</div>
  <p class="af-login-desc">Sign in to plan, execute and approve automated workflows.</p>
</div>
""", unsafe_allow_html=True)

    # Keep the real Streamlit form so authentication remains exactly the same.
    _, login_center, _ = st.columns([1, 1.3, 1])
    with login_center:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_clicked = st.form_submit_button("Sign in  →", use_container_width=True)

        st.markdown('<div class="af-secure">◈ Secure Access ◈</div>', unsafe_allow_html=True)

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

render_tunnel_hero()


# ============================================================
# CHAT / EMPTY STATE
# ============================================================

if not st.session_state.messages:
    render_cylinder_carousel()
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
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

# ============================================================
# BUTTON POINTER POLISH
# ============================================================
# Streamlit renders native buttons outside our custom components.
# This tiny client-side enhancement gives them the same pointer-aware
# "liquid carve" feel without changing their click/state semantics.
components.html(
    """
    <script>
    (() => {
      const parent = window.parent;
      const install = () => {
        parent.document.querySelectorAll('.stButton > button').forEach(btn => {
          if (btn.dataset.afMotion) return;
          btn.dataset.afMotion = '1';
          btn.addEventListener('pointermove', e => {
            const r = btn.getBoundingClientRect();
            btn.style.setProperty('--mx', `${e.clientX-r.left}px`);
            btn.style.setProperty('--my', `${e.clientY-r.top}px`);
          }, {passive:true});
        });
      };
      install();
      new MutationObserver(install).observe(parent.document.body, {subtree:true, childList:true});
    })();
    </script>
    """,
    height=0,
    width=0,
)
