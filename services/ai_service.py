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
            "Programming Fundamentals": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What is a variable in programming?",
                        "options": {"A": "A function", "B": "A storage location with a name", "C": "A loop", "D": "An error"},
                        "correct_answer": "B",
                        "explanation": "A variable is a storage location paired with an associated symbolic name that stores data.",
                        "topic": "Basic Programming Concepts"
                    },
                    {
                        "id": 2,
                        "question": "Which of the following is a programming language?",
                        "options": {"A": "HTML", "B": "CSS", "C": "Python", "D": "JSON"},
                        "correct_answer": "C",
                        "explanation": "Python is a high-level programming language, while HTML and CSS are markup languages, and JSON is a data format.",
                        "topic": "Programming Languages"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is the time complexity of binary search?",
                        "options": {"A": "O(n)", "B": "O(log n)", "C": "O(n²)", "D": "O(1)"},
                        "correct_answer": "B",
                        "explanation": "Binary search has O(log n) time complexity because it eliminates half the search space with each comparison.",
                        "topic": "Algorithm Analysis"
                    },
                    {
                        "id": 2,
                        "question": "What is recursion in programming?",
                        "options": {"A": "A loop", "B": "A function calling itself", "C": "An error", "D": "A data type"},
                        "correct_answer": "B",
                        "explanation": "Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem.",
                        "topic": "Programming Concepts"
                    }
                ]
            },
            "Data Structures & Algorithms": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What is an array?",
                        "options": {"A": "A single variable", "B": "A collection of elements", "C": "A function", "D": "A loop"},
                        "correct_answer": "B",
                        "explanation": "An array is a data structure that stores a collection of elements, typically of the same type.",
                        "topic": "Basic Data Structures"
                    },
                    {
                        "id": 2,
                        "question": "What does LIFO stand for?",
                        "options": {"A": "Last In First Out", "B": "Last In Final Out", "C": "List In File Out", "D": "Loop In Function Out"},
                        "correct_answer": "A",
                        "explanation": "LIFO stands for Last In First Out, which is the principle behind stack data structure.",
                        "topic": "Stack Operations"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is the average time complexity of hash table lookup?",
                        "options": {"A": "O(n)", "B": "O(log n)", "C": "O(1)", "D": "O(n²)"},
                        "correct_answer": "C",
                        "explanation": "Hash tables provide O(1) average time complexity for lookup operations due to direct indexing.",
                        "topic": "Hash Tables"
                    },
                    {
                        "id": 2,
                        "question": "Which traversal visits root node last?",
                        "options": {"A": "Preorder", "B": "Inorder", "C": "Postorder", "D": "Level order"},
                        "correct_answer": "C",
                        "explanation": "In postorder traversal, we visit left subtree, then right subtree, and finally the root node.",
                        "topic": "Tree Traversal"
                    }
                ]
            },
            "Web Development": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What does HTML stand for?",
                        "options": {"A": "Hyper Text Markup Language", "B": "High Tech Modern Language", "C": "Home Tool Markup Language", "D": "Hyper Transfer Markup Language"},
                        "correct_answer": "A",
                        "explanation": "HTML stands for HyperText Markup Language, used for creating web pages.",
                        "topic": "Web Fundamentals"
                    },
                    {
                        "id": 2,
                        "question": "Which HTTP method is used to retrieve data?",
                        "options": {"A": "POST", "B": "GET", "C": "PUT", "D": "DELETE"},
                        "correct_answer": "B",
                        "explanation": "GET method is used to retrieve data from a server without modifying anything.",
                        "topic": "HTTP Methods"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is the box model in CSS?",
                        "options": {"A": "A design pattern", "B": "Content, padding, border, margin", "C": "A JavaScript framework", "D": "A database concept"},
                        "correct_answer": "B",
                        "explanation": "The CSS box model consists of content, padding, border, and margin areas around an element.",
                        "topic": "CSS Layout"
                    },
                    {
                        "id": 2,
                        "question": "What is AJAX used for?",
                        "options": {"A": "Styling web pages", "B": "Creating databases", "C": "Asynchronous web requests", "D": "Server configuration"},
                        "correct_answer": "C",
                        "explanation": "AJAX allows web pages to make asynchronous requests to update content without refreshing the entire page.",
                        "topic": "Web Technologies"
                    }
                ]
            },
            "Database Systems": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What does SQL stand for?",
                        "options": {"A": "Simple Query Language", "B": "Structured Query Language", "C": "System Query Language", "D": "Standard Query Language"},
                        "correct_answer": "B",
                        "explanation": "SQL stands for Structured Query Language, used for managing relational databases.",
                        "topic": "Database Fundamentals"
                    },
                    {
                        "id": 2,
                        "question": "What is a primary key?",
                        "options": {"A": "A backup key", "B": "A unique identifier for records", "C": "A password", "D": "A foreign reference"},
                        "correct_answer": "B",
                        "explanation": "A primary key uniquely identifies each record in a database table.",
                        "topic": "Database Design"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is normalization in databases?",
                        "options": {"A": "Data backup", "B": "Reducing data redundancy", "C": "Increasing performance", "D": "Data encryption"},
                        "correct_answer": "B",
                        "explanation": "Normalization is the process of organizing data to reduce redundancy and improve data integrity.",
                        "topic": "Database Normalization"
                    },
                    {
                        "id": 2,
                        "question": "What is ACID in database transactions?",
                        "options": {"A": "A programming language", "B": "Atomicity, Consistency, Isolation, Durability", "C": "A database type", "D": "A query optimization technique"},
                        "correct_answer": "B",
                        "explanation": "ACID represents four key properties of database transactions: Atomicity, Consistency, Isolation, and Durability.",
                        "topic": "Transaction Properties"
                    }
                ]
            },
            "Mobile App Development": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What is Android Studio?",
                        "options": {"A": "A music player", "B": "An integrated development environment", "C": "A mobile game", "D": "A web browser"},
                        "correct_answer": "B",
                        "explanation": "Android Studio is the official IDE for Android app development.",
                        "topic": "Development Tools"
                    },
                    {
                        "id": 2,
                        "question": "Which language is primarily used for iOS development?",
                        "options": {"A": "Java", "B": "Python", "C": "Swift", "D": "C++"},
                        "correct_answer": "C",
                        "explanation": "Swift is Apple's programming language for iOS, macOS, and other Apple platforms.",
                        "topic": "iOS Development"
                    },
                    {
                        "id": 3,
                        "question": "What does APK stand for?",
                        "options": {"A": "Android Package Kit", "B": "Application Package Kit", "C": "Android Program Kit", "D": "App Package Key"},
                        "correct_answer": "A",
                        "explanation": "APK stands for Android Package Kit, the file format for Android applications.",
                        "topic": "Android Fundamentals"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is React Native used for?",
                        "options": {"A": "Web development only", "B": "Cross-platform mobile development", "C": "Desktop applications", "D": "Server-side programming"},
                        "correct_answer": "B",
                        "explanation": "React Native allows developers to build mobile apps for both iOS and Android using JavaScript.",
                        "topic": "Cross-platform Development"
                    },
                    {
                        "id": 2,
                        "question": "What is the purpose of Android manifest file?",
                        "options": {"A": "Store user data", "B": "Define app permissions and components", "C": "Handle network requests", "D": "Manage app themes"},
                        "correct_answer": "B",
                        "explanation": "The Android manifest file declares app components, permissions, and other essential information.",
                        "topic": "Android Architecture"
                    },
                    {
                        "id": 3,
                        "question": "What is MVP pattern in mobile development?",
                        "options": {"A": "Model-View-Presenter", "B": "Mobile-View-Pattern", "C": "Multi-Version-Platform", "D": "Minimum-Viable-Product"},
                        "correct_answer": "A",
                        "explanation": "MVP (Model-View-Presenter) is an architectural pattern that separates concerns in mobile applications.",
                        "topic": "Architecture Patterns"
                    }
                ]
            },
            "Machine Learning": {
                "Easy": [
                    {
                        "id": 1,
                        "question": "What is supervised learning?",
                        "options": {"A": "Learning without data", "B": "Learning with labeled data", "C": "Learning by observation", "D": "Learning without algorithms"},
                        "correct_answer": "B",
                        "explanation": "Supervised learning uses labeled training data to learn patterns and make predictions.",
                        "topic": "ML Fundamentals"
                    },
                    {
                        "id": 2,
                        "question": "What does AI stand for?",
                        "options": {"A": "Automated Intelligence", "B": "Artificial Intelligence", "C": "Advanced Integration", "D": "Algorithm Implementation"},
                        "correct_answer": "B",
                        "explanation": "AI stands for Artificial Intelligence, the simulation of human intelligence in machines.",
                        "topic": "AI Basics"
                    }
                ],
                "Medium": [
                    {
                        "id": 1,
                        "question": "What is overfitting in machine learning?",
                        "options": {"A": "Model performs too well on training data", "B": "Model has too few parameters", "C": "Model trains too quickly", "D": "Model uses too little data"},
                        "correct_answer": "A",
                        "explanation": "Overfitting occurs when a model learns training data too well, including noise and outliers.",
                        "topic": "Model Performance"
                    },
                    {
                        "id": 2,
                        "question": "What is a neural network?",
                        "options": {"A": "A computer network", "B": "A biological system", "C": "A computational model inspired by brain", "D": "A database structure"},
                        "correct_answer": "C",
                        "explanation": "Neural networks are computational models inspired by biological neural networks in the brain.",
                        "topic": "Deep Learning"
                    }
                ]
            }
        }
        
        # Generate multiple questions for each difficulty level to support user's choice
        def generate_more_questions(base_questions, subject, difficulty, target_count):
            """Generate additional questions by creating variations"""
            if len(base_questions) >= target_count:
                return base_questions[:target_count]
            
            additional_questions = []
            question_templates = {
                "Programming Fundamentals": [
                    "What is the difference between a compiler and an interpreter?",
                    "Which data type is used to store true/false values?",
                    "What is the purpose of comments in code?",
                ],
                "Data Structures & Algorithms": [
                    "What is the worst-case time complexity of quicksort?",
                    "Which data structure uses FIFO principle?",
                    "What is dynamic programming?",
                ],
                "Web Development": [
                    "What is the difference between GET and POST methods?",
                    "Which CSS property is used to change text color?",
                    "What is responsive web design?",
                ],
                "Mobile App Development": [
                    "What is the difference between native and hybrid apps?",
                    "Which database is commonly used in mobile apps?",
                    "What is the purpose of app lifecycle methods?",
                ],
                "Machine Learning": [
                    "What is the difference between classification and regression?",
                    "What is cross-validation in machine learning?",
                    "What is gradient descent?",
                ]
            }
            
            # Add more questions if we have templates
            if subject in question_templates:
                templates = question_templates[subject]
                for i, template in enumerate(templates):
                    if len(base_questions) + len(additional_questions) >= target_count:
                        break
                    additional_questions.append({
                        "id": len(base_questions) + i + 1,
                        "question": template,
                        "options": {
                            "A": f"Option A for {subject}",
                            "B": f"Correct answer for {subject}",
                            "C": f"Option C for {subject}",
                            "D": f"Option D for {subject}"
                        },
                        "correct_answer": "B",
                        "explanation": f"This is a {difficulty.lower()} level question about {subject} concepts.",
                        "topic": f"{subject} Advanced Topics"
                    })
            
            return base_questions + additional_questions
        
        # Get appropriate questions
        if subject in demo_questions and difficulty in demo_questions[subject]:
            available_questions = demo_questions[subject][difficulty]
            # Generate more questions if needed
            if len(available_questions) < num_questions:
                available_questions = generate_more_questions(available_questions, subject, difficulty, num_questions)
        else:
            # For subjects not in demo_questions, create generic questions
            available_questions = []
            for i in range(num_questions):
                available_questions.append({
                    "id": i + 1,
                    "question": f"Sample {difficulty.lower()} question {i+1} about {subject}.",
                    "options": {
                        "A": f"Option A for {subject}",
                        "B": f"Correct answer for {subject}",
                        "C": f"Option C for {subject}",
                        "D": f"Option D for {subject}"
                    },
                    "correct_answer": "B",
                    "explanation": f"This is a {difficulty.lower()} level question about {subject} concepts.",
                    "topic": f"{subject} Fundamentals"
                })
        
        # Select exactly the number of questions requested
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
