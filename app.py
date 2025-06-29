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
    # Check for page navigation requests
    if 'requested_page' in st.session_state:
        current_page = st.session_state.requested_page
        del st.session_state.requested_page
    else:
        current_page = st.session_state.get('current_page', 'Dashboard')
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎓 EduTutor AI")
        st.write(f"Welcome, {st.session_state.current_user}!")
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "Take Quiz", "Analytics", "Profile"],
            index=["Dashboard", "Take Quiz", "Analytics", "Profile"].index(current_page) if current_page in ["Dashboard", "Take Quiz", "Analytics", "Profile"] else 0,
            key="nav_selector"
        )
        
        if st.button("Logout", type="secondary"):
            session_manager.logout()
            st.rerun()
    
    # Store current page
    st.session_state.current_page = page
    
    # Main content area
    if page == "Dashboard":
        dashboard.show_dashboard()
    elif page == "Take Quiz":
        quiz.show_quiz_page()
    elif page == "Analytics":
        analytics.show_analytics()
    elif page == "Profile":
        show_profile_page()

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
