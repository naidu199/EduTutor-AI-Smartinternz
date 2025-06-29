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
    
    # Initialize session state for selections
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = "Programming Fundamentals"
    if 'selected_difficulty' not in st.session_state:
        st.session_state.selected_difficulty = "Medium"
    
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   background-clip: text;">
            Configure Your AI-Powered Quiz
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced subject selection with categories
        st.markdown("#### Choose Your Subject")
        
        subject_categories = {
            "Computer Science & Engineering": [
                "Data Structures & Algorithms",
                "Programming Fundamentals",
                "Database Systems",
                "Software Engineering",
                "Computer Networks",
                "Operating Systems",
                "Machine Learning",
                "Artificial Intelligence",
                "Cybersecurity",
                "Web Development",
                "Mobile App Development",
                "Cloud Computing"
            ],
            "Engineering & Technology": [
                "Electrical Engineering",
                "Mechanical Engineering",
                "Civil Engineering",
                "Chemical Engineering",
                "Electronics & Communication",
                "Digital Signal Processing",
                "Control Systems",
                "Embedded Systems"
            ],
            "Mathematics & Sciences": [
                "Mathematics",
                "Physics",
                "Chemistry",
                "Biology",
                "Statistics",
                "Discrete Mathematics",
                "Linear Algebra",
                "Calculus"
            ],
            "General Studies": [
                "History",
                "Literature",
                "Geography",
                "Psychology",
                "Economics",
                "Philosophy",
                "Art History"
            ]
        }
        
        # Create expandable sections for each category
        for category, subjects in subject_categories.items():
            with st.expander(f"📚 {category}", expanded=(category == "Computer Science & Engineering")):
                cols = st.columns(2)
                for i, subject in enumerate(subjects):
                    with cols[i % 2]:
                        if st.button(f"{subject}", key=f"subject_{subject}", use_container_width=True):
                            st.session_state.selected_subject = subject
        
        st.info(f"Selected: **{st.session_state.selected_subject}**")
    
    with col2:
        st.markdown("#### Choose Difficulty Level")
        
        # Stylized difficulty selection
        difficulty_options = [
            {"name": "Beginner", "level": "Easy", "desc": "Perfect for getting started", "emoji": "🟢"},
            {"name": "Intermediate", "level": "Medium", "desc": "Challenge your knowledge", "emoji": "🟡"},
            {"name": "Advanced", "level": "Hard", "desc": "Test your expertise", "emoji": "🔴"}
        ]
        
        for option in difficulty_options:
            if st.button(
                f"{option['emoji']} {option['name']}\n{option['desc']}", 
                key=f"diff_{option['level']}", 
                use_container_width=True
            ):
                st.session_state.selected_difficulty = option['level']
            
        st.info(f"Level: **{st.session_state.selected_difficulty}**")
        
        num_questions = st.slider(
            "Number of Questions:",
            min_value=3,
            max_value=10,
            value=5
        )
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin: 1rem 0;">
            <h4>Quiz Preview</h4>
            <p><strong>Subject:</strong> {st.session_state.selected_subject}</p>
            <p><strong>Difficulty:</strong> {st.session_state.selected_difficulty}</p>
            <p><strong>Questions:</strong> {num_questions}</p>
            <p><strong>Estimated Time:</strong> {num_questions * 2} minutes</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate quiz button
    if st.button("Generate Quiz", type="primary", use_container_width=True):
        generate_quiz(st.session_state.selected_subject, st.session_state.selected_difficulty, num_questions)

def generate_quiz(subject: str, difficulty: str, num_questions: int):
    """Generate a new quiz using AI service"""
    
    with st.spinner("🤖 AI is generating your personalized quiz..."):
        try:
            ai_service = AIService()
            
            if not ai_service.is_configured():
                st.warning(
                    "🤖 Running in Demo Mode\n\n"
                    "The AI service is currently using demo content. "
                    "Demo quizzes are available to showcase the platform's capabilities."
                )
            
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
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            reset_quiz_state()
            st.rerun()

def reset_quiz_state():
    """Reset quiz-related session state"""
    st.session_state.current_quiz = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.quiz_results = None
