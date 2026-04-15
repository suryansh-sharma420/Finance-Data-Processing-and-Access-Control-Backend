import os
from datetime import date, datetime
from typing import Any, Dict, Optional

import pandas as pd
import requests
import streamlit as st


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
RECORD_CATEGORIES = ["Salary", "Other Income", "Housing", "Food", "Transportation", "Misc"]
ROLES = ["Viewer", "Analyst", "Admin"]


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def _headers() -> Dict[str, str]:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _safe_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"detail": response.text or "No response body"}


def api_request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    form_payload: Optional[Dict[str, Any]] = None,
) -> tuple[bool, Any, int]:
    url = f"{get_api_base_url()}{path}"
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=_headers(),
            params=params,
            json=json_payload,
            data=form_payload,
            timeout=20,
        )
    except requests.RequestException as exc:
        return False, {"detail": f"Request error: {exc}"}, 0

    if 200 <= response.status_code < 300:
        if response.status_code == 204:
            return True, {"detail": "Success (no content)"}, response.status_code
        return True, _safe_json(response), response.status_code
    return False, _safe_json(response), response.status_code


def ensure_session_defaults() -> None:
    defaults = {
        "access_token": None,
        "token_type": None,
        "current_user": None,
        "records_cache": [],
        "users_cache": [],
        "dashboard_summary": None,
        "dashboard_trends": [],
        "dashboard_breakdown": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def refresh_current_user() -> None:
    if not st.session_state.get("access_token"):
        st.session_state.current_user = None
        return
    ok, data, _ = api_request("GET", "/auth/me")
    st.session_state.current_user = data if ok else None


def load_dashboard_data(months: int = 12) -> None:
    ok_summary, summary, _ = api_request("GET", "/dashboard/summary")
    ok_trends, trends, _ = api_request("GET", "/dashboard/trends", params={"months": months})
    ok_breakdown, breakdown, _ = api_request("GET", "/dashboard/category-breakdown")
    st.session_state.dashboard_summary = summary if ok_summary else None
    st.session_state.dashboard_trends = trends if ok_trends else []
    st.session_state.dashboard_breakdown = breakdown if ok_breakdown else []


def load_records(skip: int = 0, limit: int = 100, tx_type: str = "", category: str = "") -> None:
    params = {
        "skip": skip,
        "limit": limit,
        "type": tx_type or None,
        "category": category or None,
    }
    clean_params = {k: v for k, v in params.items() if v is not None}
    ok, data, _ = api_request("GET", "/records/", params=clean_params)
    st.session_state.records_cache = data if ok else []


def load_users() -> bool:
    ok, data, _ = api_request("GET", "/users/")
    st.session_state.users_cache = data if ok else []
    return ok


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(120deg, #f8fbff 0%, #f4f0ff 45%, #fff5f5 100%);
        }
        .hero-card {
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            color: #121212;
            background: linear-gradient(135deg, #7c3aed 0%, #2563eb 55%, #06b6d4 100%);
            color: white;
            box-shadow: 0 14px 32px rgba(37, 99, 235, 0.18);
            margin-bottom: 0.8rem;
        }
        .hero-title {
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }
        .muted {
            opacity: 0.9;
            font-size: 0.95rem;
        }
        .pill {
            display: inline-block;
            padding: 0.28rem 0.62rem;
            border-radius: 999px;
            font-size: 0.8rem;
            margin-right: 0.35rem;
            margin-top: 0.35rem;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.45);
        }
        .panel {
            background: white;
            border-radius: 14px;
            border: 1px solid #e7e9f1;
            padding: 0.85rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 8px 20px rgba(18, 18, 18, 0.04);
        }
        .kpi {
            background: white;
            border: 1px solid #e6e8f2;
            border-radius: 14px;
            padding: 0.8rem;
            box-shadow: 0 8px 18px rgba(18, 18, 18, 0.03);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_auth_panel() -> None:
    st.subheader("Sign In")
    st.caption("Use seeded credentials from the README.")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="admin@zorvyn.com")
        password = st.text_input("Password", type="password", placeholder="password123")
        login_clicked = st.form_submit_button("Log In", use_container_width=True)

    if login_clicked:
        ok, data, code = api_request(
            "POST",
            "/auth/login",
            form_payload={"username": email, "password": password},
        )
        if ok:
            st.session_state.access_token = data.get("access_token")
            st.session_state.token_type = data.get("token_type")
            refresh_current_user()
            st.success("Login successful.")
            st.rerun()
        else:
            st.error(f"Login failed ({code}): {data.get('detail', data)}")

    if st.session_state.get("access_token"):
        if st.button("Refresh Profile", use_container_width=True):
            refresh_current_user()
        if st.button("Log Out", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.token_type = None
            st.session_state.current_user = None
            st.session_state.records_cache = []
            st.session_state.users_cache = []
            st.session_state.dashboard_summary = None
            st.session_state.dashboard_trends = []
            st.session_state.dashboard_breakdown = []
            st.rerun()
    else:
        st.info("Not logged in.")


def render_profile_panel() -> None:
    st.subheader("Profile")
    if not st.session_state.get("access_token"):
        st.warning("Log in to view profile details.")
        return

    if st.session_state.current_user is None:
        refresh_current_user()

    if st.session_state.current_user:
        user = st.session_state.current_user
        col1, col2, col3 = st.columns(3)
        col1.metric("Email", user.get("email", "-"))
        col2.metric("Role", user.get("role", "-"))
        col3.metric("Status", "Active" if user.get("is_active") else "Inactive")
        with st.expander("Raw User JSON"):
            st.json(user)
    else:
        st.error("Could not load user profile. Try refreshing after login.")


def _user_update_payload(
    email: str,
    username: str,
    role: str,
    include_is_active: bool,
    is_active: bool,
    password: str,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if email:
        payload["email"] = email
    if username:
        payload["username"] = username
    if role:
        payload["role"] = role
    if include_is_active:
        payload["is_active"] = is_active
    if password:
        payload["password"] = password
    return payload


def render_users_panel() -> None:
    st.subheader("Team & Access")
    st.caption("Manage users, roles, and account states.")
    is_admin = bool(st.session_state.current_user and st.session_state.current_user.get("is_superuser"))
    if not is_admin:
        st.warning("Only admins can list/create users. You can still fetch your own profile in the Profile tab.")

    with st.expander("Create New User", expanded=False):
        with st.form("create_user_form"):
            email = st.text_input("Email", key="create_user_email")
            username = st.text_input("Username", key="create_user_username")
            password = st.text_input("Password", type="password", key="create_user_password")
            role = st.selectbox("Role", options=ROLES, key="create_user_role")
            is_active = st.checkbox("Is Active", value=True, key="create_user_active")
            submit = st.form_submit_button("Create User", use_container_width=True, disabled=not is_admin)
        if submit:
            ok, data, code = api_request(
                "POST",
                "/users/",
                json_payload={
                    "email": email,
                    "username": username,
                    "password": password,
                    "role": role,
                    "is_active": is_active,
                },
            )
            if ok:
                st.success("User created.")
                st.json(data)
            else:
                st.error(f"Create failed ({code}): {data.get('detail', data)}")

    with st.expander("Directory", expanded=True):
        col_left, col_right = st.columns([1, 2])
        with col_left:
            if st.button("Refresh User Directory", use_container_width=True, disabled=not is_admin):
                ok = load_users()
                if not ok:
                    st.error("Failed to fetch users. Admin access is required.")
        with col_right:
            role_filter = st.selectbox("Filter by Role", options=["All"] + ROLES, key="users_role_filter")
        users = st.session_state.users_cache or []
        if users:
            frame = pd.DataFrame(users)
            if role_filter != "All":
                frame = frame[frame["role"] == role_filter]
            st.dataframe(frame, use_container_width=True)
        else:
            st.info("User directory is empty or not loaded yet.")

    with st.expander("Get User By ID"):
        user_id = st.number_input("User ID", min_value=1, step=1, key="read_user_id")
        if st.button("Fetch User", use_container_width=True):
            ok, data, code = api_request("GET", f"/users/{int(user_id)}")
            if ok:
                st.json(data)
            else:
                st.error(f"Fetch failed ({code}): {data.get('detail', data)}")

    with st.expander("Update User"):
        with st.form("update_user_form"):
            user_id = st.number_input("User ID", min_value=1, step=1, key="update_user_id")
            email = st.text_input("Email (optional)", key="update_user_email")
            username = st.text_input("Username (optional)", key="update_user_username")
            role = st.selectbox("Role (optional)", options=[""] + ROLES, key="update_user_role")
            include_is_active = st.checkbox("Set is_active", value=False, key="update_user_include_active")
            is_active = st.checkbox("Is Active", value=True, key="update_user_active")
            password = st.text_input("New Password (optional)", type="password", key="update_user_password")
            submit = st.form_submit_button("Update User", use_container_width=True)
        if submit:
            payload = _user_update_payload(email, username, role, include_is_active, is_active, password)
            if not payload:
                st.warning("Provide at least one field to update.")
                return
            ok, data, code = api_request("PATCH", f"/users/{int(user_id)}", json_payload=payload)
            if ok:
                st.success("User updated.")
                st.json(data)
            else:
                st.error(f"Update failed ({code}): {data.get('detail', data)}")

    with st.expander("Delete User"):
        user_id = st.number_input("User ID", min_value=1, step=1, key="delete_user_id")
        if st.button("Delete User", type="primary", use_container_width=True):
            ok, data, code = api_request("DELETE", f"/users/{int(user_id)}")
            if ok:
                st.success("User deleted.")
            else:
                st.error(f"Delete failed ({code}): {data.get('detail', data)}")


def _record_payload(
    amount: float,
    tx_type: str,
    category: str,
    description: str,
    tx_date: date,
) -> Dict[str, Any]:
    dt = datetime.combine(tx_date, datetime.min.time()).isoformat()
    return {
        "amount": amount,
        "type": tx_type,
        "category": category,
        "description": description,
        "date": dt,
    }


def render_records_panel() -> None:
    st.subheader("Transactions")
    st.caption("Track and manage income and expenses with live filtering.")

    with st.expander("Add Transaction", expanded=True):
        with st.form("create_record_form"):
            amount = st.number_input("Amount", min_value=0.01, value=100.0, step=0.01)
            tx_type = st.selectbox("Type", options=["Income", "Expense"])
            category = st.selectbox("Category", options=RECORD_CATEGORIES)
            description = st.text_input("Description", value="Sample transaction")
            tx_date = st.date_input("Date", value=date.today())
            submit = st.form_submit_button("Add Transaction", use_container_width=True)
        if submit:
            ok, data, code = api_request(
                "POST",
                "/records/",
                json_payload=_record_payload(amount, tx_type, category, description, tx_date),
            )
            if ok:
                st.success("Record created.")
                st.json(data)
            else:
                st.error(f"Create failed ({code}): {data.get('detail', data)}")

    with st.expander("Explore Transactions", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            skip = st.number_input("Skip", min_value=0, step=1, value=0)
        with col2:
            limit = st.number_input("Limit", min_value=1, step=1, value=100)
        with col3:
            record_type = st.selectbox("Type filter", options=["", "Income", "Expense"])
        with col4:
            category_filter = st.selectbox("Category filter", options=[""] + RECORD_CATEGORIES)

        if st.button("Refresh Transactions", use_container_width=True):
            load_records(skip=int(skip), limit=int(limit), tx_type=record_type, category=category_filter)

        records = st.session_state.records_cache or []
        if records:
            frame = pd.DataFrame(records)
            st.dataframe(frame, use_container_width=True)
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            summary_col1.metric("Rows", len(frame))
            summary_col2.metric("Income", f"{frame.loc[frame['type'] == 'Income', 'amount'].sum():,.2f}")
            summary_col3.metric("Expense", f"{frame.loc[frame['type'] == 'Expense', 'amount'].sum():,.2f}")
        else:
            st.info("No records loaded yet. Click Refresh Transactions.")

    with st.expander("Get Record By ID"):
        record_id = st.number_input("Record ID", min_value=1, step=1, key="read_record_id")
        if st.button("Fetch Record"):
            ok, data, code = api_request("GET", f"/records/{int(record_id)}")
            if ok:
                st.json(data)
            else:
                st.error(f"Fetch failed ({code}): {data.get('detail', data)}")

    with st.expander("Update Record (Admin)"):
        with st.form("update_record_form"):
            record_id = st.number_input("Record ID", min_value=1, step=1, key="update_record_id")
            amount = st.number_input("Amount", min_value=0.01, value=100.0, step=0.01, key="update_record_amount")
            tx_type = st.selectbox("Type", options=["Income", "Expense"], key="update_record_type")
            category = st.selectbox("Category", options=RECORD_CATEGORIES, key="update_record_category")
            description = st.text_input("Description", key="update_record_description")
            tx_date = st.date_input("Date", value=date.today(), key="update_record_date")
            submit = st.form_submit_button("Update Transaction", use_container_width=True)
        if submit:
            ok, data, code = api_request(
                "PATCH",
                f"/records/{int(record_id)}",
                json_payload=_record_payload(amount, tx_type, category, description, tx_date),
            )
            if ok:
                st.success("Record updated.")
                st.json(data)
            else:
                st.error(f"Update failed ({code}): {data.get('detail', data)}")

    with st.expander("Delete Record (Admin)"):
        record_id = st.number_input("Record ID", min_value=1, step=1, key="delete_record_id")
        if st.button("Delete Transaction", type="primary", use_container_width=True):
            ok, data, code = api_request("DELETE", f"/records/{int(record_id)}")
            if ok:
                st.success("Record deleted.")
            else:
                st.error(f"Delete failed ({code}): {data.get('detail', data)}")


def render_dashboard_panel() -> None:
    st.subheader("Insights")
    st.caption("Colorful analytics view with quick visual checks.")

    ctrl1, ctrl2 = st.columns([2, 1])
    with ctrl1:
        months = st.slider("Trend Window (Months)", min_value=1, max_value=36, value=12)
    with ctrl2:
        if st.button("Refresh Insights", use_container_width=True):
            load_dashboard_data(months=months)

    summary = st.session_state.dashboard_summary
    trends = st.session_state.dashboard_trends or []
    breakdown = st.session_state.dashboard_breakdown or []

    if summary:
        c1, c2, c3 = st.columns(3)
        c1.markdown('<div class="kpi">', unsafe_allow_html=True)
        c1.metric("Total Income", f"{summary.get('total_income', 0):,.2f}")
        c1.markdown("</div>", unsafe_allow_html=True)
        c2.markdown('<div class="kpi">', unsafe_allow_html=True)
        c2.metric("Total Expenses", f"{summary.get('total_expenses', 0):,.2f}")
        c2.markdown("</div>", unsafe_allow_html=True)
        c3.markdown('<div class="kpi">', unsafe_allow_html=True)
        c3.metric("Net Balance", f"{summary.get('net_balance', 0):,.2f}")
        c3.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No summary data yet. Click Refresh Insights.")

    with st.expander("Summary Filters"):
        col1, col2 = st.columns(2)
        with col1:
            use_start = st.checkbox("Use Start Date", value=False, key="summary_use_start")
            start_date = st.date_input("Start Date", value=date.today(), key="summary_start")
        with col2:
            use_end = st.checkbox("Use End Date", value=False, key="summary_use_end")
            end_date = st.date_input("End Date", value=date.today(), key="summary_end")
        if st.button("Fetch Filtered Summary", use_container_width=True):
            params = {}
            if use_start:
                params["start_date"] = start_date.isoformat()
            if use_end:
                params["end_date"] = end_date.isoformat()
            ok, data, code = api_request("GET", "/dashboard/summary", params=params or None)
            if ok:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Income", f"{data.get('total_income', 0):,.2f}")
                c2.metric("Total Expenses", f"{data.get('total_expenses', 0):,.2f}")
                c3.metric("Net Balance", f"{data.get('net_balance', 0):,.2f}")
                st.session_state.dashboard_summary = data
            else:
                st.error(f"Summary failed ({code}): {data.get('detail', data)}")

    left, right = st.columns([2, 1])
    with left:
        st.markdown("#### Monthly Trends")
        if trends:
            trend_frame = pd.DataFrame(trends)
            st.line_chart(trend_frame.set_index("month")[["income", "expenses", "net_balance"]], use_container_width=True)
            with st.expander("Trend Data Table"):
                st.dataframe(trend_frame, use_container_width=True)
        else:
            st.info("No trend data available.")

    with right:
        st.markdown("#### Category Mix")
        if breakdown:
            breakdown_frame = pd.DataFrame(breakdown)
            st.bar_chart(breakdown_frame.set_index("category")["amount"], use_container_width=True)
            with st.expander("Breakdown Data Table"):
                st.dataframe(breakdown_frame, use_container_width=True)
        else:
            st.info("No category data available.")


def render_overview_panel() -> None:
    st.subheader("Overview")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            """
            <div class="panel">
            <h4 style="margin-top:0;">How to use this UI</h4>
            <p style="margin-bottom:0.35rem;">
            Start with <b>Insights</b> to view health metrics, then use <b>Transactions</b> for day-to-day financial updates.
            User and access operations stay in <b>Team & Access</b>.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Quick Refresh All", use_container_width=True):
            load_dashboard_data()
            load_records()
            if st.session_state.current_user and st.session_state.current_user.get("is_superuser"):
                load_users()

    d1, d2, d3 = st.columns(3)
    summary = st.session_state.dashboard_summary or {}
    d1.metric("Income", f"{summary.get('total_income', 0):,.2f}")
    d2.metric("Expenses", f"{summary.get('total_expenses', 0):,.2f}")
    d3.metric("Balance", f"{summary.get('net_balance', 0):,.2f}")


def main() -> None:
    st.set_page_config(page_title="Zorvyn Frontend", page_icon="💹", layout="wide")
    ensure_session_defaults()
    inject_styles()

    role = "-"
    if st.session_state.current_user:
        role = st.session_state.current_user.get("role", "-")
    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-title">Zorvyn Finance Studio</div>
          <div class="muted">A modern control center for records, analytics, and access management.</div>
          <span class="pill">Role: {role}</span>
          <span class="pill">API: {get_api_base_url()}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Workspace")
        if st.session_state.current_user:
            st.success(
                f"Logged in as: {st.session_state.current_user.get('email')} "
                f"({st.session_state.current_user.get('role')})"
            )
        else:
            st.warning("Not authenticated")
        st.divider()
        render_auth_panel()
        st.divider()
        if st.button("Refresh Dashboard Cache", use_container_width=True):
            load_dashboard_data()
            st.success("Dashboard data refreshed.")

    tabs = st.tabs(["Overview", "Insights", "Transactions", "Team & Access", "Profile"])

    with tabs[0]:
        render_overview_panel()
    with tabs[1]:
        render_dashboard_panel()
    with tabs[2]:
        render_records_panel()
    with tabs[3]:
        render_users_panel()
    with tabs[4]:
        render_profile_panel()


if __name__ == "__main__":
    main()
