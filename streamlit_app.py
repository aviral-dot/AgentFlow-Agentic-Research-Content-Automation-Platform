import time
import uuid

import requests
import streamlit as st




FASTAPI_URL = "http://localhost:8000"




st.set_page_config(
    page_title="AgentFlow AI",
    page_icon="🤖",
    layout="centered",
)




st.markdown(
    """
    <style>

    .stButton > button {
        width: 100%;
        font-weight: bold;
    }

    .workflow-card {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)




if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "workflow" not in st.session_state:
    st.session_state.workflow = None




def check_backend() -> bool:

    try:

        response = requests.get(
            FASTAPI_URL,
            timeout=5,
        )

        return response.status_code == 200

    except requests.exceptions.RequestException:

        return False




def send_message(
    query: str,
) -> dict:

    try:

        response = requests.post(
            f"{FASTAPI_URL}/chat",
            json={
                "query": query,
                "thread_id": st.session_state.thread_id,
            },
            timeout=180,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as exc:

        return {
            "success": False,
            "blocked": False,
            "error": str(exc),
        }




def send_email_decision(
    thread_id: str,
    decision: str,
) -> dict:

    try:

        response = requests.post(
            f"{FASTAPI_URL}/email/approval",
            json={
                "thread_id": thread_id,
                "decision": decision,
            },
            timeout=180,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as exc:

        return {
            "success": False,
            "blocked": False,
            "error": str(exc),
        }




def extract_workflow(
    result: dict,
) -> dict:

    data = result.get(
        "data",
        {},
    )

    return {
        "tasks": result.get(
            "tasks",
            data.get(
                "tasks",
                [],
            ),
        ),
        "completed_tasks": result.get(
            "completed_tasks",
            data.get(
                "completed_tasks",
                [],
            ),
        ),
        "task_count": result.get(
            "task_count",
            data.get(
                "task_count",
                0,
            ),
        ),
        "current_task": result.get(
            "current_task",
            data.get(
                "current_task",
            ),
        ),
        "workflow_results": result.get(
            "workflow_results",
            data.get(
                "workflow_results",
                [],
            ),
        ),
    }




def display_workflow(
    workflow: dict | None,
):

    if not workflow:
        return

    tasks = workflow.get(
        "tasks",
        [],
    )

    completed_tasks = workflow.get(
        "completed_tasks",
        [],
    )

    task_count = workflow.get(
        "task_count",
        len(tasks),
    )

    current_task = workflow.get(
        "current_task",
    )

    workflow_results = workflow.get(
        "workflow_results",
        [],
    )

    if not tasks:
        return

    with st.expander(
        "🔎 Planner → Executor Workflow",
        expanded=False,
    ):

       

        st.markdown(
            "### 📋 Workflow Summary"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Tasks",
                task_count,
            )

        with col2:

            st.metric(
                "Completed",
                len(completed_tasks),
            )

        with col3:

            if current_task:
                current_display = current_task
            else:
                current_display = "None"

            st.metric(
                "Current",
                current_display,
            )

        st.divider()

       

        st.markdown(
            "### 🧠 Planned Tasks"
        )

        for task in tasks:

            if isinstance(
                task,
                dict,
            ):

                task_id = task.get(
                    "id",
                    "unknown",
                )

                task_type = task.get(
                    "type",
                    "unknown",
                )

                description = task.get(
                    "description",
                    "",
                )

                depends_on = task.get(
                    "depends_on",
                    [],
                )

                use_blog = task.get(
                    "use_blog",
                    False,
                )

                status = task.get(
                    "status",
                    "unknown",
                )

            else:

                task_id = getattr(
                    task,
                    "id",
                    "unknown",
                )

                task_type = getattr(
                    task,
                    "type",
                    "unknown",
                )

                description = getattr(
                    task,
                    "description",
                    "",
                )

                depends_on = getattr(
                    task,
                    "depends_on",
                    [],
                )

                use_blog = getattr(
                    task,
                    "use_blog",
                    False,
                )

                status = getattr(
                    task,
                    "status",
                    "unknown",
                )

            status_icons = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "rejected": "🚫",
                "failed": "❌",
            }

            icon = status_icons.get(
                status,
                "❔",
            )

            st.markdown(
                f"**{icon} {task_id} — "
                f"{task_type.upper()}**"
            )

            if description:

                st.caption(
                    description
                )

            if depends_on:

                st.caption(
                    "🔗 Depends on: "
                    + ", ".join(depends_on)
                )

            else:

                st.caption(
                    "🔗 Depends on: None"
                )

            if task_type == "email":

                if use_blog:

                    st.caption(
                        "📨 Uses generated blog: Yes"
                    )

                else:

                    st.caption(
                        "📨 Uses generated blog: No"
                    )

            st.caption(
                f"Status: `{status}`"
            )

            st.divider()

        

        if workflow_results:

            st.markdown(
                "### 📦 Task Results"
            )

            for item in workflow_results:

                if isinstance(
                    item,
                    dict,
                ):

                    task_id = item.get(
                        "task_id",
                        "unknown",
                    )

                    task_type = item.get(
                        "task_type",
                        "unknown",
                    )

                    status = item.get(
                        "status",
                        "unknown",
                    )

                    result_data = item.get(
                        "result",
                    )

                else:

                    task_id = getattr(
                        item,
                        "task_id",
                        "unknown",
                    )

                    task_type = getattr(
                        item,
                        "task_type",
                        "unknown",
                    )

                    status = getattr(
                        item,
                        "status",
                        "unknown",
                    )

                    result_data = getattr(
                        item,
                        "result",
                        None,
                    )

                st.markdown(
                    f"**{task_id} — "
                    f"{task_type.upper()} — "
                    f"`{status}`**"
                )

                if task_type == "blog" and isinstance(
                    result_data,
                    dict,
                ):

                    title = result_data.get(
                        "title",
                        "",
                    )

                    content = result_data.get(
                        "content",
                        "",
                    )

                    if title:

                        st.caption(
                            f"Title: {title}"
                        )

                    if content:

                        st.caption(
                            "Blog generated successfully."

                        )

                elif task_type == "email" and isinstance(
                    result_data,
                    dict,
                ):

                    recipient = result_data.get(
                        "to",
                        "",
                    )

                    subject = result_data.get(
                        "subject",
                        "",
                    )

                    if recipient:

                        st.caption(
                            f"To: {recipient}"
                        )

                    if subject:

                        st.caption(
                            f"Subject: {subject}"
                        )

                st.divider()




with st.sidebar:

    st.title(
        "⚙️ AgentFlow"
    )

   

    if check_backend():

        st.success(
            "🟢 FastAPI Connected"
        )

    else:

        st.error(
            "🔴 FastAPI Offline"
        )

   

    st.markdown("---")

    st.markdown(
        "### Architecture"
    )

    st.markdown(
        """
        **User Request**
        ↓

        **FastAPI**
        ↓

        **Input Guardrail**
        ↓

        **Workflow Planner**
        ↓

        **Dependency Graph**
        ↓

        **Workflow Executor**
        ↓

        **Blog / Email Worker**
        ↓

        **Task Result**
        ↓

        **Next Ready Task**
        ↓

        **Human Approval**
        ↓

        **Gmail**
        """
    )

    

    st.markdown("---")

    st.markdown(
        "### Supported Workflows"
    )

    st.markdown(
        """
        **📝 Blog only**

        Generate a brief blog about a topic.

        **📧 Email only**

        Generate and send an email.

        **📝 + 📧 Independent**

        Generate a blog and send an unrelated email.

        **📝 → 📧 Dependent**

        Generate a blog and email the generated blog.
        """
    )

   

    st.markdown("---")

    st.caption(
        "Conversation ID"
    )

    st.code(
        st.session_state.thread_id,
        language=None,
    )

   

    st.markdown("---")

    if st.button(
        "🗑️ New Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.session_state.pending_approval = None

        st.session_state.workflow = None

        st.session_state.thread_id = str(
            uuid.uuid4()
        )

        st.rerun()




st.title(
    "🤖 AgentFlow AI"
)

st.markdown(
    "Planner–Executor automation for "
    "**brief blog generation and email communication.**"
)

st.markdown("---")



for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )




display_workflow(
    st.session_state.workflow
)




if st.session_state.pending_approval:

    approval_data = (
        st.session_state.pending_approval
    )

    approval = approval_data.get(
        "approval",
        {},
    )

    email = approval.get(
        "email",
        {},
    )

    thread_id = approval_data.get(
        "thread_id",
        st.session_state.thread_id,
    )

    st.markdown("---")

    st.warning(
        "⚠️ Human approval required before sending this email."
    )

    st.markdown(
        "### 📧 Email Preview"
    )

    st.markdown(
        f"**To:** `{email.get('to', '')}`"
    )

    st.markdown(
        f"**Subject:** {email.get('subject', '')}"
    )

    st.markdown(
        "**Body:**"
    )

    st.text_area(
        "Email Body",
        value=email.get(
            "body",
            "",
        ),
        height=250,
        disabled=True,
        label_visibility="collapsed",
    )

    st.caption(
        "Review the email carefully before approving."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    

    with col1:

        approve_clicked = st.button(
            "✅ Approve & Send",
            key=f"approve_{thread_id}",
            use_container_width=True,
        )

    
    with col2:

        reject_clicked = st.button(
            "❌ Reject",
            key=f"reject_{thread_id}",
            use_container_width=True,
        )

   

    if approve_clicked:

        with st.spinner(
            "Sending approved email..."
        ):

            decision_result = (
                send_email_decision(
                    thread_id,
                    "approve",
                )
            )

        if decision_result.get(
            "success"
        ):

            st.session_state.pending_approval = None

            st.session_state.workflow = extract_workflow(
                decision_result
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "✅ **Email approved and "
                        "sent successfully.**"
                    ),
                }
            )

            st.success(
                "Email approved and sent successfully."
            )

            st.rerun()

        else:

            error_message = decision_result.get(
                "error",
                decision_result.get(
                    "message",
                    "Failed to approve the email.",
                ),
            )

            st.error(
                f"❌ {error_message}"
            )

   
    if reject_clicked:

        with st.spinner(
            "Rejecting email..."
        ):

            decision_result = (
                send_email_decision(
                    thread_id,
                    "reject",
                )
            )

        if decision_result.get(
            "success"
        ):

            st.session_state.pending_approval = None

            st.session_state.workflow = extract_workflow(
                decision_result
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "❌ **Email rejected. "
                        "Nothing was sent.**"
                    ),
                }
            )

            st.info(
                "Email rejected. Nothing was sent."
            )

            st.rerun()

        else:

            error_message = decision_result.get(
                "error",
                decision_result.get(
                    "message",
                    "Failed to reject the email.",
                ),
            )

            st.error(
                f"❌ {error_message}"
            )




query = st.chat_input(
    "e.g. Generate a brief blog about AI agents..."
)




if query:

    

    if st.session_state.pending_approval:

        st.warning(
            "⚠️ Please approve or reject the pending email first."
        )

        st.stop()

    

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    

    with st.chat_message(
        "user"
    ):

        st.markdown(
            query
        )

   

    with st.chat_message(
        "assistant"
    ):

        start_time = time.time()

        with st.spinner(
            "🤔 Planning and executing..."
        ):

            result = send_message(
                query
            )

        elapsed_time = (
            time.time() - start_time
        )

        

        workflow = extract_workflow(
            result
        )

        st.session_state.workflow = workflow

       
        if result.get(
            "error"
        ):

            answer = (
                "❌ **Unable to connect "
                "to the backend.**\n\n"
                f"`{result['error']}`"
            )

            st.error(
                answer
            )

        

        elif result.get(
            "blocked"
        ):

            stage = result.get(
                "stage",
                "security",
            )

            reason = result.get(
                "reason",
                "Request blocked by security guardrail.",
            )

            if stage == "input":

                answer = (
                    "🛡️ **Request blocked**\n\n"
                    "Your request was blocked by "
                    "the **input security guardrail**."
                )

            elif stage == "output":

                answer = (
                    "🛡️ **Response blocked**\n\n"
                    "The generated response was blocked "
                    "by the **output security guardrail**."
                )

            else:

                answer = (
                    "🛡️ **Request blocked**\n\n"
                    f"{reason}"
                )

            st.warning(
                answer
            )

            st.caption(
                f"Security stage: `{stage}` • "
                f"Response time: "
                f"`{elapsed_time:.2f}s`"
            )

       

        elif (
            result.get("success")
            and result.get("status")
            == "approval_required"
        ):

            st.session_state.pending_approval = result

            approval = result.get(
                "approval",
                {},
            )

            email = approval.get(
                "email",
                {},
            )

            answer = (
                "⚠️ **Email generated successfully. "
                "Human approval is required "
                "before sending.**"
            )

            st.warning(
                answer
            )

            if email:

                st.info(
                    f"📧 Email prepared for "
                    f"`{email.get('to', '')}`"
                )

            st.caption(
                "👤 Human approval required • "
                f"⏱️ Response time: "
                f"`{elapsed_time:.2f}s`"
            )

       

        elif result.get(
            "success"
        ):

            data = result.get(
                "data",
                {},
            )

            answer = data.get(
                "response",
                "Request completed successfully.",
            )

            completed_tasks = workflow.get(
                "completed_tasks",
                [],
            )

            task_count = workflow.get(
                "task_count",
                0,
            )

            st.markdown(
                answer
            )

            st.caption(
                f"✅ Completed "
                f"{len(completed_tasks)} "
                f"of {task_count} tasks"
            )

            st.caption(
                "🤖 Planner → Executor • "
                f"⏱️ Response time: "
                f"`{elapsed_time:.2f}s`"
            )

        
        else:

            answer = (
                "⚠️ **Unexpected response "
                "from backend.**"
            )

            st.warning(
                answer
            )

    

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    

    if (
        result.get("status")
        == "approval_required"
    ):

        st.rerun()