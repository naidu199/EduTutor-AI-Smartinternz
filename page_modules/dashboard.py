import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.session_manager import SessionManager
from services.ai_service import AIService

def show_dashboard():
    """Display the main dashboard"""
    
    # Modern hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🚀 Learning Dashboard</h1>
        <p style="color: #e2e8f0; margin-top: 0.5rem; font-size: 1.1rem;">Track your progress and accelerate your learning journey</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Gamified metrics with modern styling
    metrics = [
        {"label": "Quizzes Completed", "value": user_stats['total_quizzes'], "icon": "🎯", "color": "#3b82f6"},
        {"label": "Average Score", "value": f"{user_stats['average_score']}%", "icon": "📊", "color": "#10b981"},
        {"label": "Best Performance", "value": f"{user_stats['best_score']}%", "icon": "🏆", "color": "#f59e0b"},
        {"label": "Favorite Subject", "value": user_stats['favorite_subject'], "icon": "💡", "color": "#8b5cf6"}
    ]
    
    for i, (col, metric) in enumerate(zip([col1, col2, col3, col4], metrics)):
        with col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {metric['color']}22 0%, {metric['color']}11 100%); 
                        padding: 1.5rem; border-radius: 10px; border-left: 4px solid {metric['color']}; 
                        text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{metric['icon']}</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: {metric['color']};">{metric['value']}</div>
                <div style="font-size: 0.9rem; color: #64748b; margin-top: 0.2rem;">{metric['label']}</div>
            </div>
            """, unsafe_allow_html=True)

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
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center;">
        <h2 style="color: white; margin: 0;">🚀 Welcome to EduTutor AI</h2>
        <p style="color: #e2e8f0; margin: 1rem 0;">Your personalized learning journey starts here</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #1e293b; padding: 1.5rem; border-radius: 10px; border: 1px solid #334155;">
            <h3 style="color: #f8fafc; margin-top: 0;">🎯 Get Started</h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                Jump into your first AI-powered quiz and experience personalized learning. 
                Our platform adapts to your pace and provides detailed insights to accelerate your growth.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Your First Quiz", type="primary", use_container_width=True):
            st.session_state.requested_page = "Take Quiz"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background: #1e293b; padding: 1.5rem; border-radius: 10px; border: 1px solid #334155;">
            <h3 style="color: #f8fafc; margin-top: 0;">✨ Platform Features</h3>
            <ul style="color: #94a3b8; line-height: 1.8; padding-left: 1.2rem;">
                <li><strong>AI-Generated Content:</strong> Dynamic quizzes tailored to your level</li>
                <li><strong>Instant Feedback:</strong> Detailed explanations for every answer</li>
                <li><strong>Progress Analytics:</strong> Visual tracking of your learning journey</li>
                <li><strong>Smart Recommendations:</strong> AI-powered learning suggestions</li>
                <li><strong>Comprehensive Subjects:</strong> CS, Engineering, Math, and more</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

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
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("👤 Profile", use_container_width=True):
            st.rerun()
