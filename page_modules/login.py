import streamlit as st
from utils.session_manager import SessionManager

def show_login_page():
    """Display login and registration interface"""
    
    st.title("🎓 Welcome to EduTutor AI")
    st.markdown("### Your Personalized Learning Journey Starts Here")
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    session_manager = SessionManager()
    
    with tab1:
        show_login_form(session_manager)
    
    with tab2:
        show_registration_form(session_manager)

def show_login_form(session_manager: SessionManager):
    """Display login form"""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login", type="primary")
        
        if submit_button:
            if not username or not password:
                st.error("Please fill in all fields")
            else:
                success, message = session_manager.login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Demo account info
    with st.expander("Demo Account"):
        st.info("No account? Try the demo!")
        st.code("Username: demo\nPassword: demo123")
        
        if st.button("Use Demo Account"):
            # Create demo account if it doesn't exist
            if 'demo' not in st.session_state.users:
                session_manager.register_user('demo', 'demo@example.com', 'demo123')
            
            success, message = session_manager.login_user('demo', 'demo123')
            if success:
                st.success("Logged in with demo account!")
                st.rerun()

def show_registration_form(session_manager: SessionManager):
    """Display registration form"""
    st.subheader("Create New Account")
    
    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Sign Up", type="primary")
        
        if submit_button:
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = session_manager.register_user(username, email, password)
                if success:
                    st.success(message)
                    st.info("Please switch to the Login tab to sign in")
                else:
                    st.error(message)
    
    st.info("💡 **Tips for better learning:**\n"
            "- Take quizzes regularly\n"
            "- Review explanations carefully\n"
            "- Track your progress over time")
