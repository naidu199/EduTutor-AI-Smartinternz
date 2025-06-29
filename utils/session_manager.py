import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any

class SessionManager:
    """Manages user sessions and authentication"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'users' not in st.session_state:
            st.session_state.users = {}
        if 'quiz_history' not in st.session_state:
            st.session_state.quiz_history = {}
    
    def register_user(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        if username in st.session_state.users:
            return False, "Username already exists"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if "@" not in email:
            return False, "Please enter a valid email address"
        
        # Store user data
        st.session_state.users[username] = {
            'email': email,
            'password': password,  # In production, this should be hashed
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Initialize quiz history for new user
        st.session_state.quiz_history[username] = []
        
        return True, "Registration successful!"
    
    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate user login"""
        if username not in st.session_state.users:
            return False, "Username not found"
        
        if st.session_state.users[username]['password'] != password:
            return False, "Incorrect password"
        
        # Set authentication state
        st.session_state.authenticated = True
        st.session_state.current_user = username
        
        return True, "Login successful!"
    
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.current_user = None
    
    def get_current_user(self) -> Optional[str]:
        """Get current authenticated user"""
        return st.session_state.current_user if st.session_state.authenticated else None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.authenticated
    
    def save_quiz_result(self, quiz_data: Dict[str, Any], results: Dict[str, Any]):
        """Save quiz result to user's history"""
        if not self.is_authenticated():
            return
        
        username = self.get_current_user()
        
        quiz_record = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'subject': quiz_data['subject'],
            'difficulty': quiz_data['difficulty'],
            'total_questions': results['total_questions'],
            'correct_answers': results['correct_answers'],
            'score': results['score_percentage'],
            'performance_level': results['performance_level'],
            'detailed_results': results['detailed_results']
        }
        
        if username not in st.session_state.quiz_history:
            st.session_state.quiz_history[username] = []
        
        st.session_state.quiz_history[username].append(quiz_record)
    
    def get_user_quiz_history(self) -> list:
        """Get quiz history for current user"""
        if not self.is_authenticated():
            return []
        
        username = self.get_current_user()
        return st.session_state.quiz_history.get(username, [])
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        history = self.get_user_quiz_history()
        
        if not history:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'best_score': 0,
                'favorite_subject': 'None',
                'improvement_trend': 'No data'
            }
        
        total_quizzes = len(history)
        scores = [quiz['score'] for quiz in history]
        average_score = sum(scores) / total_quizzes
        best_score = max(scores)
        
        # Find most common subject
        subjects = [quiz['subject'] for quiz in history]
        favorite_subject = max(set(subjects), key=subjects.count) if subjects else 'None'
        
        # Calculate improvement trend (last 3 vs first 3 quizzes)
        if total_quizzes >= 6:
            early_avg = sum(scores[:3]) / 3
            recent_avg = sum(scores[-3:]) / 3
            if recent_avg > early_avg + 5:
                improvement_trend = "Improving"
            elif recent_avg < early_avg - 5:
                improvement_trend = "Declining"
            else:
                improvement_trend = "Stable"
        else:
            improvement_trend = "Not enough data"
        
        return {
            'total_quizzes': total_quizzes,
            'average_score': round(average_score, 1),
            'best_score': round(best_score, 1),
            'favorite_subject': favorite_subject,
            'improvement_trend': improvement_trend
        }
