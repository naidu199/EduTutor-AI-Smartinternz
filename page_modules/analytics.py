import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from utils.session_manager import SessionManager

def show_analytics():
    """Display comprehensive analytics and insights"""
    
    st.header("📈 Learning Analytics")
    
    session_manager = SessionManager()
    quiz_history = session_manager.get_user_quiz_history()
    
    if not quiz_history:
        show_no_data_message()
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(quiz_history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # Analytics sections
    show_performance_overview(df)
    show_subject_analysis(df)
    show_progress_tracking(df)
    show_learning_insights(df)

def show_no_data_message():
    """Display message when no quiz data is available"""
    
    st.info(
        "📊 **No Analytics Data Available**\n\n"
        "Take some quizzes to see your learning analytics and insights here!"
    )
    
    if st.button("🎯 Take Your First Quiz", type="primary"):
        st.session_state.nav_selector = "Take Quiz"
        st.rerun()

def show_performance_overview(df):
    """Display overall performance metrics and trends"""
    
    st.subheader("📊 Performance Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = df['score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}%")
    
    with col2:
        best_score = df['score'].max()
        st.metric("Best Score", f"{best_score:.1f}%")
    
    with col3:
        improvement = calculate_improvement_trend(df)
        st.metric("Improvement Trend", improvement)
    
    with col4:
        consistency = calculate_consistency_score(df)
        st.metric("Consistency Score", f"{consistency:.1f}/10")
    
    # Performance over time chart
    fig_performance = px.line(
        df,
        x='timestamp',
        y='score',
        title='Score Progression Over Time',
        labels={'score': 'Score (%)', 'timestamp': 'Date'},
        markers=True
    )
    
    # Add trend line
    fig_performance.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['score'].rolling(window=3, center=True).mean(),
            mode='lines',
            name='Trend Line',
            line=dict(dash='dash', color='red')
        )
    )
    
    st.plotly_chart(fig_performance, use_container_width=True)

def show_subject_analysis(df):
    """Display subject-wise performance analysis"""
    
    st.subheader("📚 Subject Analysis")
    
    # Subject performance comparison
    subject_stats = df.groupby('subject').agg({
        'score': ['mean', 'count', 'std'],
        'timestamp': 'max'
    }).round(2)
    
    subject_stats.columns = ['Average Score', 'Quizzes Taken', 'Score Variance', 'Last Attempt']
    subject_stats = subject_stats.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart of average scores by subject
        fig_subjects = px.bar(
            subject_stats,
            x='subject',
            y='Average Score',
            title='Average Score by Subject',
            text='Average Score'
        )
        fig_subjects.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_subjects, use_container_width=True)
    
    with col2:
        # Quiz frequency by subject
        fig_frequency = px.pie(
            subject_stats,
            values='Quizzes Taken',
            names='subject',
            title='Quiz Distribution by Subject'
        )
        st.plotly_chart(fig_frequency, use_container_width=True)
    
    # Subject details table
    st.subheader("📋 Subject Performance Details")
    
    # Add performance indicators
    subject_stats['Performance'] = subject_stats['Average Score'].apply(
        lambda x: "🏆 Excellent" if x >= 90 else "👍 Good" if x >= 80 else "📚 Needs Work"
    )
    
    st.dataframe(
        subject_stats[['subject', 'Average Score', 'Quizzes Taken', 'Performance']],
        use_container_width=True,
        hide_index=True
    )

def show_progress_tracking(df):
    """Display progress tracking and learning patterns"""
    
    st.subheader("📈 Progress Tracking")
    
    # Learning streak calculation
    learning_streak = calculate_learning_streak(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Learning Streak", f"{learning_streak} days")
    
    with col2:
        recent_activity = len(df[df['timestamp'] >= datetime.now() - timedelta(days=7)])
        st.metric("Quizzes This Week", recent_activity)
    
    with col3:
        monthly_average = calculate_monthly_average(df)
        st.metric("Monthly Average", f"{monthly_average:.1f} quizzes")
    
    # Daily activity heatmap
    if len(df) > 7:
        show_activity_heatmap(df)
    
    # Difficulty progression
    show_difficulty_progression(df)

def show_difficulty_progression(df):
    """Show progression across difficulty levels"""
    
    if 'difficulty' in df.columns:
        st.subheader("🎯 Difficulty Level Analysis")
        
        difficulty_stats = df.groupby('difficulty')['score'].agg(['mean', 'count']).round(2)
        difficulty_stats.columns = ['Average Score', 'Attempts']
        
        fig_difficulty = px.bar(
            difficulty_stats.reset_index(),
            x='difficulty',
            y='Average Score',
            title='Performance by Difficulty Level',
            text='Average Score',
            color='difficulty',
            color_discrete_map={'Easy': 'green', 'Medium': 'orange', 'Hard': 'red'}
        )
        fig_difficulty.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_difficulty, use_container_width=True)

def show_activity_heatmap(df):
    """Display learning activity heatmap"""
    
    # Create daily activity data
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour
    
    activity_matrix = df.groupby(['day_of_week', 'hour']).size().reset_index(name='activity_count')
    
    # Create heatmap
    fig_heatmap = px.density_heatmap(
        activity_matrix,
        x='hour',
        y='day_of_week',
        z='activity_count',
        title='Learning Activity Heatmap',
        labels={'hour': 'Hour of Day', 'day_of_week': 'Day of Week'}
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

def show_learning_insights(df):
    """Display AI-generated insights and recommendations"""
    
    st.subheader("💡 Learning Insights")
    
    insights = generate_learning_insights(df)
    
    for insight in insights:
        st.info(f"💭 {insight}")
    
    # Recommendations
    st.subheader("🎯 Personalized Recommendations")
    
    recommendations = generate_recommendations(df)
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

def calculate_improvement_trend(df):
    """Calculate improvement trend over time"""
    
    if len(df) < 4:
        return "Not enough data"
    
    # Compare first quarter vs last quarter
    quarter_size = max(2, len(df) // 4)
    early_scores = df.head(quarter_size)['score'].mean()
    recent_scores = df.tail(quarter_size)['score'].mean()
    
    improvement = recent_scores - early_scores
    
    if improvement > 10:
        return "📈 Strong Improvement"
    elif improvement > 5:
        return "📊 Improving"
    elif improvement > -5:
        return "📉 Stable"
    else:
        return "📉 Declining"

def calculate_consistency_score(df):
    """Calculate consistency score based on score variance"""
    
    score_std = df['score'].std()
    
    # Convert standard deviation to 0-10 scale (lower std = higher consistency)
    consistency = max(0, 10 - (score_std / 10))
    return consistency

def calculate_learning_streak(df):
    """Calculate current learning streak in days"""
    
    if df.empty:
        return 0
    
    # Get unique dates and sort them
    unique_dates = sorted(df['date'].unique(), reverse=True)
    
    streak = 0
    current_date = datetime.now().date()
    
    for date in unique_dates:
        if date == current_date or date == current_date - timedelta(days=streak + 1):
            streak += 1
            current_date = date
        else:
            break
    
    return streak

def calculate_monthly_average(df):
    """Calculate monthly average quiz frequency"""
    
    if df.empty:
        return 0
    
    days_active = (df['timestamp'].max() - df['timestamp'].min()).days + 1
    monthly_average = len(df) * 30 / days_active if days_active > 0 else len(df)
    
    return monthly_average

def generate_learning_insights(df):
    """Generate insights based on learning patterns"""
    
    insights = []
    
    # Performance trend
    if len(df) >= 5:
        recent_avg = df.tail(3)['score'].mean()
        overall_avg = df['score'].mean()
        
        if recent_avg > overall_avg + 5:
            insights.append("Your recent performance shows significant improvement! Keep up the excellent work.")
        elif recent_avg < overall_avg - 5:
            insights.append("Your recent scores have dipped. Consider reviewing fundamental concepts.")
    
    # Subject analysis
    if 'subject' in df.columns:
        subject_scores = df.groupby('subject')['score'].mean()
        best_subject = subject_scores.idxmax()
        worst_subject = subject_scores.idxmin()
        
        if subject_scores[best_subject] - subject_scores[worst_subject] > 20:
            insights.append(f"You excel in {best_subject} but struggle with {worst_subject}. Focus more practice time on {worst_subject}.")
    
    # Learning frequency
    avg_gap = calculate_average_gap_between_quizzes(df)
    if avg_gap > 7:
        insights.append("Try to maintain more consistent study habits. Regular practice leads to better retention.")
    elif avg_gap < 1:
        insights.append("Great job maintaining a consistent learning schedule!")
    
    return insights

def generate_recommendations(df):
    """Generate personalized recommendations"""
    
    recommendations = []
    
    # Based on performance
    avg_score = df['score'].mean()
    if avg_score < 70:
        recommendations.append("Focus on easier difficulty levels to build confidence before advancing")
        recommendations.append("Review explanations carefully after each quiz")
    elif avg_score > 85:
        recommendations.append("Challenge yourself with harder difficulty levels")
        recommendations.append("Explore new subjects to broaden your knowledge")
    
    # Based on frequency
    quiz_frequency = len(df) / max(1, (datetime.now().date() - df['date'].min()).days)
    if quiz_frequency < 0.3:  # Less than once every 3 days
        recommendations.append("Increase your quiz frequency for better learning retention")
    
    # Subject diversity
    if 'subject' in df.columns:
        unique_subjects = df['subject'].nunique()
        if unique_subjects < 3:
            recommendations.append("Try quizzes in different subjects to develop well-rounded knowledge")
    
    return recommendations

def calculate_average_gap_between_quizzes(df):
    """Calculate average days between quizzes"""
    
    if len(df) < 2:
        return 0
    
    df_sorted = df.sort_values('timestamp')
    gaps = df_sorted['timestamp'].diff().dt.days.dropna()
    
    return gaps.mean() if not gaps.empty else 0
