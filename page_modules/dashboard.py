import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.session_manager import SessionManager
from services.ai_service import AIService

def show_dashboard():
    """Display the main dashboard"""
    st.header("📊 Learning Dashboard")
    
    session_manager = SessionManager()
    user_stats = session_manager.get_user_stats()
    quiz_history = session_manager.get_user_quiz_history()
    
    # Overview metrics
    show_overview_metrics(user_stats)
    
    # Charts and visualizations
    if quiz_history:
        show_performance_charts(quiz_history)
        show_recent_activity(quiz_history)
    else:
        show_getting_started()
    
    # Personalized recommendations
    show_recommendations(quiz_history)

def show_overview_metrics(user_stats):
    """Display key metrics in columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 Total Quizzes",
            value=user_stats['total_quizzes']
        )
    
    with col2:
        st.metric(
            label="📈 Average Score",
            value=f"{user_stats['average_score']}%"
        )
    
    with col3:
        st.metric(
            label="🏆 Best Score",
            value=f"{user_stats['best_score']}%"
        )
    
    with col4:
        st.metric(
            label="📚 Favorite Subject",
            value=user_stats['favorite_subject']
        )

def show_performance_charts(quiz_history):
    """Display performance visualization charts"""
    st.subheader("📈 Performance Analytics")
    
    # Create DataFrame from quiz history
    df = pd.DataFrame(quiz_history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score progression over time
        fig_line = px.line(
            df, 
            x='timestamp', 
            y='score',
            title='Score Progression Over Time',
            labels={'score': 'Score (%)', 'timestamp': 'Date'}
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        # Performance by subject
        subject_avg = df.groupby('subject')['score'].mean().reset_index()
        fig_bar = px.bar(
            subject_avg,
            x='subject',
            y='score',
            title='Average Score by Subject',
            labels={'score': 'Average Score (%)', 'subject': 'Subject'}
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Difficulty level performance
    if 'difficulty' in df.columns:
        difficulty_avg = df.groupby('difficulty')['score'].mean().reset_index()
        fig_difficulty = px.pie(
            difficulty_avg,
            values='score',
            names='difficulty',
            title='Performance by Difficulty Level'
        )
        st.plotly_chart(fig_difficulty, use_container_width=True)

def show_recent_activity(quiz_history):
    """Display recent quiz activity"""
    st.subheader("🕒 Recent Activity")
    
    # Show last 5 quizzes
    recent_quizzes = quiz_history[-5:]
    
    for quiz in reversed(recent_quizzes):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{quiz['subject']}** ({quiz['difficulty']})")
                st.caption(quiz['timestamp'])
            
            with col2:
                score_color = "green" if quiz['score'] >= 80 else "orange" if quiz['score'] >= 60 else "red"
                st.markdown(f"<span style='color: {score_color}'>{quiz['score']:.1f}%</span>", unsafe_allow_html=True)
            
            with col3:
                st.write(f"{quiz['correct_answers']}/{quiz['total_questions']}")
            
            with col4:
                performance_emoji = "🏆" if quiz['score'] >= 90 else "👍" if quiz['score'] >= 70 else "📚"
                st.write(f"{performance_emoji} {quiz['performance_level']}")
        
        st.divider()

def show_getting_started():
    """Display getting started information for new users"""
    st.subheader("🚀 Get Started with EduTutor AI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "**Welcome to EduTutor AI!** 🎉\n\n"
            "Start your personalized learning journey by taking your first quiz. "
            "Our AI-powered platform will adapt to your learning style and provide "
            "detailed feedback to help you improve."
        )
        
        if st.button("Take Your First Quiz 🎯", type="primary"):
            st.session_state.nav_selector = "Take Quiz"
            st.rerun()
    
    with col2:
        st.markdown(
            """
            ### ✨ Features You'll Love:
            - **AI-Generated Quizzes**: Dynamic questions tailored to your level
            - **Instant Feedback**: Detailed explanations for every answer
            - **Progress Tracking**: Visual analytics of your learning journey
            - **Personalized Recommendations**: AI-powered learning suggestions
            - **Multiple Subjects**: Wide range of topics to explore
            """
        )

def show_recommendations(quiz_history):
    """Display personalized learning recommendations"""
    st.subheader("💡 Personalized Recommendations")
    
    try:
        ai_service = AIService()
        if ai_service.is_configured():
            recommendations = ai_service.get_personalized_recommendations(quiz_history)
        else:
            recommendations = [
                "Take regular quizzes to track your progress",
                "Review explanations for incorrect answers",
                "Try different difficulty levels to challenge yourself",
                "Focus on consistent learning rather than cramming"
            ]
    except Exception as e:
        st.error(f"Could not generate personalized recommendations: {str(e)}")
        recommendations = [
            "Take regular quizzes to track your progress",
            "Review explanations for incorrect answers"
        ]
    
    for i, recommendation in enumerate(recommendations, 1):
        st.write(f"{i}. {recommendation}")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 New Quiz", use_container_width=True):
            st.session_state.nav_selector = "Take Quiz"
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.nav_selector = "Analytics"
            st.rerun()
    
    with col3:
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.nav_selector = "Profile"
            st.rerun()
