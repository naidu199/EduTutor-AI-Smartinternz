import streamlit as st
import json
from datetime import datetime
from utils.session_manager import SessionManager
from page_modules import login, dashboard, quiz, analytics

# Configure page
st.set_page_config(
    page_title="EduTutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session manager
session_manager = SessionManager()

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = {}
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    # Main app logic
    if not st.session_state.authenticated:
        login.show_login_page()
    else:
        show_authenticated_app()

def show_authenticated_app():
    # Set default page to Dashboard after authentication
    if st.session_state.current_page == 'login':
        st.session_state.current_page = 'Dashboard'

    # Check for page navigation requests
    if 'requested_page' in st.session_state:
        current_page = st.session_state.requested_page
        del st.session_state.requested_page
    else:
        current_page = st.session_state.get('current_page', 'Dashboard')

    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       background-clip: text; margin: 0;">
                EduTutor AI
            </h2>
            <p style="color: #94a3b8; margin: 0.5rem 0;">Welcome back, {}</p>
        </div>
        """.format(st.session_state.current_user), unsafe_allow_html=True)

        st.markdown("---")

        # Enhanced navigation with icons
        nav_options = [
            {"name": "Dashboard", "icon": "📊", "desc": "Overview & Progress"},
            {"name": "Take Quiz", "icon": "🎯", "desc": "AI-Powered Quizzes"},
            {"name": "Analytics", "icon": "📈", "desc": "Learning Insights"},
            {"name": "Profile", "icon": "👤", "desc": "Account Settings"}
        ]

        # Navigation buttons
        selected_page = None
        for option in nav_options:
            is_current = option["name"] == current_page

            if st.button(
                f"{option['icon']} {option['name']}\n{option['desc']}",
                key=f"nav_{option['name']}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                selected_page = option["name"]

        # Only update page if a button was clicked, otherwise keep current page
        if selected_page:
            page = selected_page
        else:
            page = current_page

        st.markdown("---")

        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            session_manager.logout()
            st.rerun()

    # Store current page
    st.session_state.current_page = page

    # Main content area - ensure we always show a valid page
    if page == "Dashboard":
        dashboard.show_dashboard()
    elif page == "Take Quiz":
        quiz.show_quiz_page()
    elif page == "Analytics":
        analytics.show_analytics()
    elif page == "Profile":
        show_profile_page()
    else:
        # Fallback to Dashboard if page is not recognized
        st.session_state.current_page = "Dashboard"
        dashboard.show_dashboard()

def show_profile_page():
    st.header("👤 User Profile")

    user_data = st.session_state.users.get(st.session_state.current_user, {})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Profile Information")
        st.write(f"**Username:** {st.session_state.current_user}")
        st.write(f"**Email:** {user_data.get('email', 'Not provided')}")
        st.write(f"**Member since:** {user_data.get('created_at', 'Unknown')}")

    with col2:
        st.subheader("Quick Stats")
        user_history = st.session_state.quiz_history.get(st.session_state.current_user, [])

        if user_history:
            total_quizzes = len(user_history)
            avg_score = sum(quiz['score'] for quiz in user_history) / total_quizzes
            st.metric("Total Quizzes", total_quizzes)
            st.metric("Average Score", f"{avg_score:.1f}%")
        else:
            st.info("No quiz history available yet. Take your first quiz!")

if __name__ == "__main__":
    main()
