import os
import json
from typing import Dict, Any, List

try:
    from ibm_watsonx_ai import APIClient
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False

class AIService:
    """Service class for interacting with IBM Granite AI model for quiz generation"""

    def __init__(self):
        self.url = "https://eu-gb.ml.cloud.ibm.com"
        self.api_key = os.getenv("IBM_API_KEY")
        self.project_id = os.getenv("IBM_PROJECT_ID")
        self.model_id = "ibm/granite-3-8b-instruct"
        
        if WATSONX_AVAILABLE and self.api_key and self.project_id:
            try:
                # Initialize API client
                credentials = {
                    "apikey": self.api_key,
                    "url": self.url
                }
                self.client = APIClient(credentials)
                self.client.set.default_project(self.project_id)

                # Initialize model
                self.parameters = {
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 2000,
                    GenParams.TEMPERATURE: 0.3,
                    GenParams.TOP_P: 0.9,
                    GenParams.STOP_SEQUENCES: []
                }
                self.model = ModelInference(
                    model_id=self.model_id,
                    api_client=self.client,
                    project_id=self.project_id,
                    params=self.parameters
                )
                self.configured = True
            except Exception as e:
                self.configured = False
        else:
            self.configured = False

    def is_configured(self) -> bool:
        """Check if the AI service is properly configured"""
        return self.configured

    def generate_quiz(self, subject: str, difficulty: str, num_questions: int = 5) -> Dict[str, Any]:
        """Generate a quiz using IBM Granite model or fallback demo content"""
        
        if self.is_configured():
            system_prompt = (
                "You are Granite, an AI language model developed by IBM in 2024. "
                "You are an expert educator and quiz creator with deep knowledge across multiple subjects. "
                "You create engaging, educational, and well-structured quizzes with clear explanations."
            )
            
            user_prompt = self._construct_quiz_prompt(subject, difficulty, num_questions)

            try:
                response = self.model.generate_text(
                    prompt=f"{system_prompt}\n\n{user_prompt}"
                )
                
                # Parse JSON response
                quiz_data = json.loads(response)
                return quiz_data
            except json.JSONDecodeError as e:
                raise Exception(f"Error parsing quiz data: {str(e)}")
            except Exception as e:
                raise Exception(f"Error generating quiz: {str(e)}")
        else:
            # Generate demo quiz for demonstration
            return self._generate_demo_quiz(subject, difficulty, num_questions)

    def _construct_quiz_prompt(self, subject: str, difficulty: str, num_questions: int) -> str:
        """Construct a detailed prompt for quiz generation"""
        
        prompt = f"""
Create a {difficulty.lower()} level quiz about {subject} with exactly {num_questions} multiple-choice questions.

REQUIREMENTS:
1. Each question should have 4 options (A, B, C, D)
2. Only one correct answer per question
3. Provide detailed explanations for why each answer is correct or incorrect
4. Questions should be appropriate for the {difficulty.lower()} difficulty level
5. Cover different aspects and concepts within {subject}

DIFFICULTY GUIDELINES:
- Easy: Basic concepts, straightforward questions, common knowledge
- Medium: Intermediate concepts, some analysis required, moderate complexity
- Hard: Advanced concepts, critical thinking, complex scenarios

RESPONSE FORMAT (JSON only, no additional text):
{{
    "subject": "{subject}",
    "difficulty": "{difficulty}",
    "total_questions": {num_questions},
    "questions": [
        {{
            "id": 1,
            "question": "Question text here?",
            "options": {{
                "A": "Option A text",
                "B": "Option B text", 
                "C": "Option C text",
                "D": "Option D text"
            }},
            "correct_answer": "A",
            "explanation": "Detailed explanation of why A is correct and why others are wrong",
            "topic": "Specific topic within the subject"
        }}
    ]
}}

Please provide ONLY the JSON response with no additional formatting or text.
"""
        return prompt

    def evaluate_quiz_answers(self, quiz_data: Dict, user_answers: Dict) -> Dict[str, Any]:
        """Evaluate quiz answers and provide detailed feedback"""
        
        total_questions = len(quiz_data['questions'])
        correct_answers = 0
        detailed_results = []
        
        for question in quiz_data['questions']:
            question_id = str(question['id'])
            user_answer = user_answers.get(question_id, '')
            correct_answer = question['correct_answer']
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_answers += 1
            
            detailed_results.append({
                'question_id': question['id'],
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question['explanation'],
                'topic': question['topic']
            })
        
        score_percentage = (correct_answers / total_questions) * 100
        
        # Generate performance feedback
        if score_percentage >= 90:
            performance_level = "Excellent"
            feedback = "Outstanding performance! You have a strong understanding of the subject."
        elif score_percentage >= 80:
            performance_level = "Good"
            feedback = "Good job! You understand most concepts well with room for minor improvements."
        elif score_percentage >= 70:
            performance_level = "Satisfactory"
            feedback = "Decent performance. Focus on reviewing the topics you missed."
        elif score_percentage >= 60:
            performance_level = "Needs Improvement"
            feedback = "You're getting there! Review the material and practice more."
        else:
            performance_level = "Poor"
            feedback = "Consider reviewing the fundamentals and taking practice quizzes."
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'performance_level': performance_level,
            'feedback': feedback,
            'detailed_results': detailed_results
        }

    def get_personalized_recommendations(self, quiz_results: List[Dict]) -> List[str]:
        """Generate personalized learning recommendations based on quiz history"""
        
        if not quiz_results:
            return ["Take your first quiz to get personalized recommendations!"]
        
        # Analyze performance patterns
        weak_topics = []
        strong_subjects = []
        
        for result in quiz_results[-5:]:  # Last 5 quizzes
            if result['score_percentage'] < 70:
                for detail in result['detailed_results']:
                    if not detail['is_correct']:
                        weak_topics.append(detail['topic'])
            elif result['score_percentage'] >= 85:
                strong_subjects.append(result['subject'])
        
        recommendations = []
        
        if weak_topics:
            common_weak_topics = list(set(weak_topics))[:3]
            recommendations.append(f"Focus on improving: {', '.join(common_weak_topics)}")
        
        if strong_subjects:
            recommendations.append(f"You're excelling in {', '.join(set(strong_subjects))}. Try advanced topics!")
        
        recommendations.extend([
            "Take quizzes regularly to track your progress",
            "Review explanations for incorrect answers",
            "Try different difficulty levels to challenge yourself"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_demo_quiz(self, subject: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Generate a demo quiz for demonstration purposes"""
        
        demo_questions = {
            "Mathematics": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What is 2 + 2?",
                        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                        "correct_answer": "B",
                        "explanation": "2 + 2 equals 4. This is basic addition.",
                        "topic": "Basic Arithmetic"
                    },
                    {
                        "id": 2,
                        "question": "What is 5 × 3?",
                        "options": {"A": "12", "B": "15", "C": "18", "D": "20"},
                        "correct_answer": "B",
                        "explanation": "5 × 3 = 15. Multiplication is repeated addition.",
                        "topic": "Basic Multiplication"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is the square root of 64?",
                        "options": {"A": "6", "B": "7", "C": "8", "D": "9"},
                        "correct_answer": "C",
                        "explanation": "√64 = 8 because 8² = 64.",
                        "topic": "Square Roots"
                    },
                    {
                        "id": 2,
                        "question": "Solve for x: 2x + 5 = 13",
                        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                        "correct_answer": "B",
                        "explanation": "2x + 5 = 13, so 2x = 8, therefore x = 4.",
                        "topic": "Linear Equations"
                    }
                ]
            },
            "Science": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What planet is closest to the Sun?",
                        "options": {"A": "Venus", "B": "Earth", "C": "Mercury", "D": "Mars"},
                        "correct_answer": "C",
                        "explanation": "Mercury is the closest planet to the Sun in our solar system.",
                        "topic": "Solar System"
                    },
                    {
                        "id": 2,
                        "question": "What gas do plants absorb from the atmosphere during photosynthesis?",
                        "options": {"A": "Oxygen", "B": "Nitrogen", "C": "Carbon Dioxide", "D": "Hydrogen"},
                        "correct_answer": "C",
                        "explanation": "Plants absorb carbon dioxide and release oxygen during photosynthesis.",
                        "topic": "Photosynthesis"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is the chemical symbol for gold?",
                        "options": {"A": "Go", "B": "Au", "C": "Ag", "D": "Gd"},
                        "correct_answer": "B",
                        "explanation": "Au is the chemical symbol for gold, from the Latin word 'aurum'.",
                        "topic": "Chemical Elements"
                    },
                    {
                        "id": 2,
                        "question": "What force keeps planets in orbit around the Sun?",
                        "options": {"A": "Magnetism", "B": "Nuclear force", "C": "Gravity", "D": "Electromagnetic force"},
                        "correct_answer": "C",
                        "explanation": "Gravity is the force that keeps planets in orbit around the Sun.",
                        "topic": "Physics - Forces"
                    }
                ]
            }
        }
        
        # Default questions for subjects not in demo
        default_questions = [
            {
                "id": 1,
                "question": f"This is a sample {difficulty.lower()} question about {subject}.",
                "options": {
                    "A": "Option A",
                    "B": "Option B (Correct)",
                    "C": "Option C", 
                    "D": "Option D"
                },
                "correct_answer": "B",
                "explanation": f"This is a demo explanation for a {subject} question at {difficulty.lower()} level.",
                "topic": f"{subject} Fundamentals"
            },
            {
                "id": 2,
                "question": f"Another sample {difficulty.lower()} question about {subject}.",
                "options": {
                    "A": "First choice",
                    "B": "Second choice",
                    "C": "Third choice (Correct)",
                    "D": "Fourth choice"
                },
                "correct_answer": "C",
                "explanation": f"This demonstrates how {subject} concepts work at {difficulty.lower()} difficulty.",
                "topic": f"Advanced {subject}"
            }
        ]
        
        # Get appropriate questions
        if subject in demo_questions and difficulty in demo_questions[subject]:
            available_questions = demo_questions[subject][difficulty]
        else:
            available_questions = default_questions
        
        # Select questions based on num_questions
        selected_questions = available_questions[:num_questions]
        
        # Update question IDs to be sequential
        for i, question in enumerate(selected_questions, 1):
            question["id"] = i
        
        return {
            "subject": subject,
            "difficulty": difficulty,
            "total_questions": len(selected_questions),
            "questions": selected_questions
        }
