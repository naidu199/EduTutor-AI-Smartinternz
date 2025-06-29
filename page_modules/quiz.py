import streamlit as st
import json
from datetime import datetime
from services.ai_service import AIService
from utils.session_manager import SessionManager

def show_quiz_page():
    """Display the quiz interface"""
    
    # Initialize session state for quiz
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = None
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'quiz_results' not in st.session_state:
        st.session_state.quiz_results = None
    
    st.header("🎯 Take a Quiz")
    
    if st.session_state.current_quiz is None:
        show_quiz_setup()
    elif not st.session_state.quiz_submitted:
        show_quiz_questions()
    else:
        show_quiz_results()

def show_quiz_setup():
    """Display quiz configuration interface"""
    st.subheader("🔧 Configure Your Quiz")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.selectbox(
            "Select Subject:",
            [
                "Mathematics",
                "Science",
                "History",
                "Literature",
                "Geography",
                "Computer Science",
                "Biology",
                "Chemistry",
                "Physics",
                "Psychology",
                "Economics",
                "Art History"
            ]
        )
        
        difficulty = st.selectbox(
            "Select Difficulty:",
            ["Easy", "Medium", "Hard"]
        )
    
    with col2:
        num_questions = st.slider(
            "Number of Questions:",
            min_value=3,
            max_value=10,
            value=5
        )
        
        st.info(
            f"📋 **Quiz Preview:**\n"
            f"- Subject: {subject}\n"
            f"- Difficulty: {difficulty}\n"
            f"- Questions: {num_questions}\n"
            f"- Estimated time: {num_questions * 2} minutes"
        )
    
    # Generate quiz button
    if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
        generate_quiz(subject, difficulty, num_questions)

def generate_quiz(subject: str, difficulty: str, num_questions: int):
    """Generate a new quiz using AI service"""
    
    with st.spinner("🤖 AI is generating your personalized quiz..."):
        try:
            ai_service = AIService()
            
            if not ai_service.is_configured():
                st.error(
                    "⚠️ AI service not configured. Please contact your administrator.\n\n"
                    "Required environment variables:\n"
                    "- IBM_API_KEY\n"
                    "- IBM_PROJECT_ID"
                )
                return
            
            quiz_data = ai_service.generate_quiz(subject, difficulty, num_questions)
            
            # Store quiz in session state
            st.session_state.current_quiz = quiz_data
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = None
            
            st.success("✅ Quiz generated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating quiz: {str(e)}")
            st.info("💡 Please try again or contact support if the problem persists.")

def show_quiz_questions():
    """Display quiz questions for user to answer"""
    
    quiz_data = st.session_state.current_quiz
    
    # Quiz header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"📚 {quiz_data['subject']} Quiz")
    with col2:
        st.write(f"**Difficulty:** {quiz_data['difficulty']}")
    with col3:
        st.write(f"**Questions:** {quiz_data['total_questions']}")
    
    # Progress bar
    answered_questions = len([a for a in st.session_state.quiz_answers.values() if a])
    progress = answered_questions / quiz_data['total_questions']
    st.progress(progress, text=f"Progress: {answered_questions}/{quiz_data['total_questions']} questions answered")
    
    st.divider()
    
    # Display questions
    with st.form("quiz_form"):
        for i, question in enumerate(quiz_data['questions'], 1):
            st.subheader(f"Question {i}")
            st.write(question['question'])
            
            # Radio button for answer selection
            answer = st.radio(
                f"Select your answer for Question {i}:",
                options=list(question['options'].keys()),
                format_func=lambda x: f"{x}. {question['options'][x]}",
                key=f"q_{question['id']}",
                index=None
            )
            
            if answer:
                st.session_state.quiz_answers[str(question['id'])] = answer
            
            st.divider()
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button(
                "📝 Submit Quiz",
                type="primary",
                use_container_width=True
            )
            
            if submit_button:
                if len(st.session_state.quiz_answers) < quiz_data['total_questions']:
                    st.error("❌ Please answer all questions before submitting.")
                else:
                    submit_quiz()

def submit_quiz():
    """Process quiz submission and show results"""
    
    with st.spinner("📊 Evaluating your answers..."):
        try:
            ai_service = AIService()
            quiz_data = st.session_state.current_quiz
            user_answers = st.session_state.quiz_answers
            
            # Evaluate answers
            results = ai_service.evaluate_quiz_answers(quiz_data, user_answers)
            
            # Save results to session
            st.session_state.quiz_results = results
            st.session_state.quiz_submitted = True
            
            # Save to user history
            session_manager = SessionManager()
            session_manager.save_quiz_result(quiz_data, results)
            
            st.success("✅ Quiz submitted successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error evaluating quiz: {str(e)}")

def show_quiz_results():
    """Display quiz results and feedback"""
    
    results = st.session_state.quiz_results
    quiz_data = st.session_state.current_quiz
    
    # Results header
    st.subheader("🎉 Quiz Results")
    
    # Score display
    score_color = "green" if results['score_percentage'] >= 80 else "orange" if results['score_percentage'] >= 60 else "red"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{results['score_percentage']:.1f}%")
    with col2:
        st.metric("Correct Answers", f"{results['correct_answers']}/{results['total_questions']}")
    with col3:
        performance_emoji = "🏆" if results['score_percentage'] >= 90 else "👍" if results['score_percentage'] >= 70 else "📚"
        st.metric("Performance", f"{performance_emoji} {results['performance_level']}")
    
    # Feedback
    st.info(f"💬 **Feedback:** {results['feedback']}")
    
    # Detailed results
    with st.expander("📋 Detailed Question Review", expanded=True):
        for detail in results['detailed_results']:
            
            # Question header
            correct_icon = "✅" if detail['is_correct'] else "❌"
            st.write(f"{correct_icon} **Question {detail['question_id']}:** {detail['question']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Your Answer:** {detail['user_answer']}")
            with col2:
                st.write(f"**Correct Answer:** {detail['correct_answer']}")
            
            # Explanation
            if detail['is_correct']:
                st.success(f"**Explanation:** {detail['explanation']}")
            else:
                st.error(f"**Explanation:** {detail['explanation']}")
            
            st.write(f"**Topic:** {detail['topic']}")
            st.divider()
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            reset_quiz_state()
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            reset_quiz_state()
            st.session_state.nav_selector = "Analytics"
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            reset_quiz_state()
            st.session_state.nav_selector = "Dashboard"
            st.rerun()

def reset_quiz_state():
    """Reset quiz-related session state"""
    st.session_state.current_quiz = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.quiz_results = None
