import os
import json
import requests
from typing import Dict, Any, List
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG for more detailed logging
logger = logging.getLogger(__name__)

try:
    from ibm_watsonx_ai import APIClient
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    logger.warning("IBM Watson AI SDK not available. Using fallback generation.")

class AIService:
    """Service class for interacting with IBM Granite AI model for quiz generation"""

    def __init__(self):
        # Use the same URL as your working SDLC service
        self.url = "https://eu-gb.ml.cloud.ibm.com"  # Changed from us-south
        self.api_key = os.getenv("IBM_API_KEY", "gVlNnx0CgD8YMT813nCKEgYlkux2Grh7sN2K2dI0XKQK")
        self.project_id = os.getenv("IBM_PROJECT_ID", "08334910-e7ec-4e32-990d-be70ab4159ad")
        self.model_id = "ibm/granite-3-8b-instruct"
        self.configured = False
        self.client = None
        self.model = None

        # Initialize IBM Watson client if credentials are available
        if self.api_key and self.project_id:
            self._initialize_watson_client()
        else:
            logger.warning("IBM Watson credentials not found. Using fallback generation.")

    def _initialize_watson_client(self):
        """Initialize the IBM Watson client using the same approach as SDLC service"""
        try:
            if WATSONX_AVAILABLE:
                credentials = {
                    "apikey": self.api_key,
                    "url": self.url
                }
                self.client = APIClient(credentials)

                # Set default project without error handling to see if it works
                try:
                    self.client.set.default_project(self.project_id)
                    logger.info("Project set successfully")
                except Exception as project_error:
                    logger.warning(f"Could not set default project: {project_error}")
                    # Continue without setting project - we'll pass it in API calls

                # Initialize model with same parameters as SDLC service
                self.parameters = {
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 2000,  # Reduced from 3000 to match SDLC
                    GenParams.TEMPERATURE: 0.3,      # Reduced from 0.7 to match SDLC
                    GenParams.TOP_P: 0.9,
                    GenParams.STOP_SEQUENCES: []
                }

                self.model = ModelInference(
                    model_id=self.model_id,
                    api_client=self.client,
                    project_id=self.project_id,  # Explicitly pass project_id
                    params=self.parameters
                )
                self.configured = True
                logger.info("IBM Watson AI client initialized successfully")
            else:
                logger.warning("IBM Watson SDK not available")
        except Exception as e:
            logger.error(f"Failed to initialize IBM Watson client: {e}")
            self.configured = False

    def is_configured(self) -> bool:
        """Check if the AI service is properly configured"""
        return self.configured and bool(self.api_key and self.project_id)

    def generate_quiz(self, subject: str, difficulty: str, num_questions: int = 5) -> Dict[str, Any]:
        """Generate a quiz using IBM Granite model"""
        logger.info(f"Generating quiz: {subject} - {difficulty} - {num_questions} questions")

        try:
            # First try IBM Watson AI if properly configured
            if self.is_configured():
                logger.info("Using IBM Watson AI for quiz generation")
                quiz_data = self._generate_with_watson_ai(subject, difficulty, num_questions)
                if quiz_data:
                    logger.info("Successfully generated quiz with IBM Watson AI")
                    return quiz_data
                else:
                    logger.warning("IBM Watson AI generation failed, falling back to REST API")

            # Try REST API as fallback with corrected grant type
            if self.api_key and self.project_id:
                logger.info("Trying IBM Watson REST API")
                quiz_data = self._generate_with_rest_api(subject, difficulty, num_questions)
                if quiz_data:
                    logger.info("Successfully generated quiz with REST API")
                    return quiz_data
                else:
                    logger.warning("REST API generation failed, using fallback")

            # Final fallback to enhanced generation
            logger.info("Using enhanced fallback generation")
            return self._generate_enhanced_quiz(subject, difficulty, num_questions)

        except Exception as e:
            logger.error(f"Error in quiz generation: {e}")
            return self._generate_enhanced_quiz(subject, difficulty, num_questions)

    def _generate_with_watson_ai(self, subject: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Generate quiz using IBM Watson AI SDK - simplified like SDLC service"""
        try:
            prompt = self._construct_detailed_prompt(subject, difficulty, num_questions)

            # Generate text using the model (simplified like SDLC service)
            response = self.model.generate_text(prompt=prompt)

            # Handle response similar to SDLC service
            generated_text = str(response) if response else ''

            logger.info(f"Generated text length: {len(generated_text)}")

            if generated_text:
                return self._parse_generated_quiz(generated_text, subject, difficulty, num_questions)
            else:
                logger.warning("No text generated from Watson AI")
                return None

        except Exception as e:
            logger.error(f"Watson AI SDK error: {e}")
            return None

    def _generate_with_rest_api(self, subject: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Generate quiz using IBM Watson REST API with corrected grant type"""
        try:
            # Get access token with corrected grant type
            access_token = self._get_access_token()
            if not access_token:
                logger.error("Failed to get access token")
                return None

            # Prepare the request
            api_url = f"{self.url}/ml/v1/text/generation?version=2023-05-29"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            prompt = self._construct_detailed_prompt(subject, difficulty, num_questions)

            # Use same parameters as SDLC service
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 2000,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "stop_sequences": []
                },
                "model_id": self.model_id,
                "project_id": self.project_id
            }

            logger.info("Making request to IBM Watson API...")
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            logger.info(f"API Response Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("results", [{}])[0].get("generated_text", "")

                logger.info(f"Generated text length: {len(generated_text)}")

                if generated_text:
                    return self._parse_generated_quiz(generated_text, subject, difficulty, num_questions)
                else:
                    logger.warning("Empty generated text from API")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"REST API error: {e}")
            return None

    def _get_access_token(self) -> str:
        """Get IBM Cloud access token with corrected grant type"""
        try:
            token_url = "https://iam.cloud.ibm.com/identity/token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            # Fixed grant type - removed 'urn:iam:' prefix
            data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self.api_key}"

            response = requests.post(token_url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                logger.error(f"Token request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None

    def _construct_detailed_prompt(self, subject: str, difficulty: str, num_questions: int) -> str:
        """Construct a detailed prompt for quiz generation - simplified like SDLC service"""
        system_prompt = (
            "You are Granite, an AI language model developed by IBM in 2024. "
            "You are an expert educator and quiz creator with deep knowledge across multiple subjects. "
            "You provide detailed, structured, and practical educational content."
        )

        user_prompt = f"""Create a {num_questions}-question quiz about {subject} at {difficulty} difficulty level.

PROJECT DETAILS:
- Subject: {subject}
- Difficulty: {difficulty}
- Number of Questions: {num_questions}

REQUIREMENTS:
1. Create exactly {num_questions} multiple choice questions
2. Each question should have 4 options (A, B, C, D)
3. Provide correct answer and explanation for each
4. Questions should be appropriate for {difficulty.lower()} level
5. Cover different aspects of {subject}

CRITICAL: Return ONLY valid JSON in the exact format below. Do not include any text before or after the JSON.

{{
  "subject": "{subject}",
  "difficulty": "{difficulty}",
  "total_questions": {num_questions},
  "questions": [
    {{
      "id": 1,
      "question": "Your question here",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Explanation of correct answer",
      "topic": "Specific topic"
    }}
  ]
}}

Make sure all property names are in double quotes and all string values are in double quotes. Return only the JSON, no additional text."""

        return f"{system_prompt}\n\n{user_prompt}"

    def _parse_generated_quiz(self, generated_text: str, subject: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Parse quiz content from generated text with improved error handling"""
        try:
            # Clean the generated text
            text = generated_text.strip()
            logger.info(f"Parsing generated text: {text[:200]}...")

            # Log the full generated text for debugging (first 1000 chars)
            logger.debug(f"Full generated text sample: {text[:1000]}...")

            # Try to find JSON content
            json_start = text.find('{')
            if json_start == -1:
                logger.warning("No JSON start found in generated text")
                logger.debug(f"Full generated text: {text}")
                return None

            json_end = text.rfind('}')
            if json_end == -1 or json_end <= json_start:
                logger.warning("No valid JSON end found in generated text")
                logger.debug(f"Full generated text: {text}")
                return None

            json_str = text[json_start:json_end + 1]
            logger.debug(f"Extracted JSON string: {json_str[:500]}...")

            try:
                quiz_data = json.loads(json_str)
                logger.info("Successfully parsed JSON on first attempt")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.debug(f"Problematic JSON around error: {json_str[max(0, e.pos-50):e.pos+50]}")

                # Try to fix common JSON issues
                logger.info("Attempting to fix JSON issues...")
                json_str = self._fix_json_issues(json_str)
                logger.debug(f"Fixed JSON string: {json_str[:500]}...")

                try:
                    quiz_data = json.loads(json_str)
                    logger.info("Successfully parsed JSON after fixes")
                except json.JSONDecodeError as e2:
                    logger.error(f"JSON still invalid after fixes: {e2}")
                    logger.debug(f"Final JSON that failed: {json_str}")

                    # Try one more aggressive fix - extract just the structure we need
                    logger.info("Attempting aggressive JSON reconstruction...")
                    quiz_data = self._reconstruct_quiz_json(text, subject, difficulty, num_questions)  # Use full text, not just json_str
                    if not quiz_data:
                        return None

            # Validate the structure
            if self._validate_quiz_structure(quiz_data, num_questions):
                logger.info("Quiz structure validation passed")
                return quiz_data
            else:
                logger.warning("Quiz structure validation failed")
                return None

        except Exception as e:
            logger.error(f"Error parsing generated quiz: {e}")
            logger.debug(f"Full generated text that caused error: {generated_text}")
            return None

    def _fix_json_issues(self, json_str: str) -> str:
        """Fix common JSON issues in generated text with improved handling"""
        import re

        logger.info("Applying comprehensive JSON fixes...")

        # First, let's log the original to see what we're working with
        logger.debug(f"Original JSON snippet: {json_str[:200]}...")

        # Remove any trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

        # Fix common quote issues
        json_str = json_str.replace('"', '"').replace('"', '"')
        json_str = json_str.replace(''', "'").replace(''', "'")

        # Handle newlines in strings properly
        json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

        # Fix unquoted property names - more comprehensive approach
        # This handles cases like: subject: "value", id: 1, etc.
        json_str = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)

        # Fix single quotes to double quotes, but be careful with nested quotes
        # First protect any escaped quotes
        json_str = json_str.replace("\\'", "__ESCAPED_QUOTE__")
        json_str = json_str.replace('\\"', "__ESCAPED_DOUBLE_QUOTE__")

        # Now replace single quotes with double quotes
        json_str = re.sub(r"'([^']*)'", r'"\1"', json_str)

        # Restore escaped quotes
        json_str = json_str.replace("__ESCAPED_QUOTE__", "\\'")
        json_str = json_str.replace("__ESCAPED_DOUBLE_QUOTE__", '\\"')

        # Fix property names that might still be unquoted after options object
        # Handle cases like: A: "option", B: "option", etc.
        json_str = re.sub(r'([ABCD])\s*:', r'"\1":', json_str)

        # Fix boolean and null values
        json_str = re.sub(r'\b(true|false|null)\b', lambda m: m.group(1).lower(), json_str, flags=re.IGNORECASE)

        # Fix common formatting issues
        json_str = re.sub(r'\s*,\s*', ', ', json_str)  # Normalize comma spacing
        json_str = re.sub(r'\s*:\s*', ': ', json_str)  # Normalize colon spacing

        # Fix bracket/brace spacing
        json_str = re.sub(r'\{\s+', '{ ', json_str)
        json_str = re.sub(r'\s+\}', ' }', json_str)
        json_str = re.sub(r'\[\s+', '[ ', json_str)
        json_str = re.sub(r'\s+\]', ' ]', json_str)

        # Remove extra whitespace but preserve structure
        json_str = re.sub(r'\n\s*\n', '\n', json_str)  # Remove empty lines

        logger.debug(f"Fixed JSON snippet: {json_str[:200]}...")
        return json_str

    def _validate_quiz_structure(self, quiz_data: Dict, expected_questions: int) -> bool:
        """Validate that the generated quiz has the correct structure"""
        try:
            # Check required top-level fields
            required_fields = ["subject", "difficulty", "total_questions", "questions"]
            for field in required_fields:
                if field not in quiz_data:
                    logger.error(f"Missing required field: {field}")
                    return False

            # Check question count
            if not isinstance(quiz_data["questions"], list):
                logger.error("Questions field is not a list")
                return False

            if len(quiz_data["questions"]) != expected_questions:
                logger.error(f"Expected {expected_questions} questions, got {len(quiz_data['questions'])}")
                return False

            # Validate each question
            for i, question in enumerate(quiz_data["questions"]):
                if not self._validate_question_structure(question, i):
                    return False

            logger.info("Quiz structure validation successful")
            return True

        except Exception as e:
            logger.error(f"Error validating quiz structure: {e}")
            return False

    def _validate_question_structure(self, question: Dict, index: int) -> bool:
        """Validate individual question structure"""
        try:
            required_fields = ["id", "question", "options", "correct_answer", "explanation", "topic"]
            for field in required_fields:
                if field not in question:
                    logger.error(f"Question {index}: Missing required field '{field}'")
                    return False

            # Validate options
            if not isinstance(question["options"], dict):
                logger.error(f"Question {index}: Options is not a dict")
                return False

            expected_options = {"A", "B", "C", "D"}
            if set(question["options"].keys()) != expected_options:
                logger.error(f"Question {index}: Invalid option keys")
                return False

            # Validate correct answer
            if question["correct_answer"] not in question["options"]:
                logger.error(f"Question {index}: Correct answer not in options")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating question {index}: {e}")
            return False

    def _generate_enhanced_quiz(self, subject: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Generate quiz with enhanced educational content as fallback"""
        logger.info(f"Generating enhanced quiz for {subject} - {difficulty}")

        # Enhanced question bank with proper educational content
        enhanced_questions = {
            "Programming Fundamentals": {
                "Easy": [
                    {
                        "question": "What is a variable in programming?",
                        "options": {
                            "A": "A function that performs calculations",
                            "B": "A storage location with an associated name",
                            "C": "A type of loop structure",
                            "D": "A debugging tool"
                        },
                        "correct_answer": "B",
                        "explanation": "A variable is a storage location paired with an associated symbolic name that contains data, referred to as the variable's value.",
                        "topic": "Programming Concepts"
                    },
                    {
                        "question": "Which of the following is a programming language?",
                        "options": {
                            "A": "HTML",
                            "B": "CSS",
                            "C": "Python",
                            "D": "JSON"
                        },
                        "correct_answer": "C",
                        "explanation": "Python is a high-level programming language. HTML and CSS are markup languages, while JSON is a data format.",
                        "topic": "Programming Languages"
                    },
                    {
                        "question": "What is the purpose of comments in code?",
                        "options": {
                            "A": "To make code run faster",
                            "B": "To explain what the code does",
                            "C": "To create variables",
                            "D": "To handle errors"
                        },
                        "correct_answer": "B",
                        "explanation": "Comments are used to explain code functionality and make it more readable for other developers.",
                        "topic": "Code Documentation"
                    }
                ],
                "Medium": [
                    {
                        "question": "What is the time complexity of binary search?",
                        "options": {
                            "A": "O(n)",
                            "B": "O(log n)",
                            "C": "O(n²)",
                            "D": "O(1)"
                        },
                        "correct_answer": "B",
                        "explanation": "Binary search has O(log n) time complexity because it eliminates half of the remaining elements with each comparison.",
                        "topic": "Algorithm Analysis"
                    },
                    {
                        "question": "What is recursion?",
                        "options": {
                            "A": "A type of loop",
                            "B": "A function calling itself",
                            "C": "An error handling technique",
                            "D": "A data structure"
                        },
                        "correct_answer": "B",
                        "explanation": "Recursion is a programming technique where a function calls itself to solve a smaller instance of the same problem.",
                        "topic": "Programming Techniques"
                    },
                    {
                        "question": "What is the purpose of version control systems like Git?",
                        "options": {
                            "A": "To compile code faster",
                            "B": "To track changes in code over time",
                            "C": "To debug applications",
                            "D": "To optimize performance"
                        },
                        "correct_answer": "B",
                        "explanation": "Version control systems track changes to files over time, allowing developers to collaborate and maintain code history.",
                        "topic": "Development Tools"
                    },
                    {
                        "question": "What is object-oriented programming?",
                        "options": {
                            "A": "Programming with objects and classes",
                            "B": "Programming only with functions",
                            "C": "Programming without variables",
                            "D": "Programming for web applications"
                        },
                        "correct_answer": "A",
                        "explanation": "Object-oriented programming is a programming paradigm based on the concept of objects and classes that contain data and methods.",
                        "topic": "Programming Paradigms"
                    },
                    {
                        "question": "What is an API?",
                        "options": {
                            "A": "A type of database",
                            "B": "Application Programming Interface",
                            "C": "A programming language",
                            "D": "A web browser"
                        },
                        "correct_answer": "B",
                        "explanation": "API stands for Application Programming Interface, which defines how different software components should communicate.",
                        "topic": "Software Architecture"
                    }
                ]
            },
            "Machine Learning": {
                "Easy": [
                    {
                        "question": "What is supervised learning?",
                        "options": {
                            "A": "Learning without any data",
                            "B": "Learning with labeled training data",
                            "C": "Learning only from images",
                            "D": "Learning without algorithms"
                        },
                        "correct_answer": "B",
                        "explanation": "Supervised learning uses labeled training data to learn a mapping from inputs to outputs.",
                        "topic": "ML Fundamentals"
                    }
                ],
                "Medium": [
                    {
                        "question": "What is overfitting in machine learning?",
                        "options": {
                            "A": "When a model learns training data too well, including noise",
                            "B": "When a model has too few parameters",
                            "C": "When a model trains too slowly",
                            "D": "When a model uses too little data"
                        },
                        "correct_answer": "A",
                        "explanation": "Overfitting occurs when a model learns the training data too well, including its noise and outliers, leading to poor generalization.",
                        "topic": "Model Performance"
                    }
                ]
            }
        }

        # Get questions for the subject and difficulty
        if subject in enhanced_questions and difficulty in enhanced_questions[subject]:
            available_questions = enhanced_questions[subject][difficulty]
        else:
            available_questions = self._create_generic_questions(subject, difficulty, num_questions)

        # Select and format questions
        selected_questions = []
        for i in range(min(num_questions, len(available_questions))):
            question = available_questions[i].copy()
            question["id"] = i + 1
            selected_questions.append(question)

        # Generate additional questions if needed
        while len(selected_questions) < num_questions:
            additional_q = {
                "id": len(selected_questions) + 1,
                "question": f"What is an important concept in {subject}?",
                "options": {
                    "A": f"Basic {subject.lower()} principle",
                    "B": f"Advanced {subject.lower()} concept",
                    "C": f"Alternative {subject.lower()} approach",
                    "D": f"Specialized {subject.lower()} technique"
                },
                "correct_answer": "B",
                "explanation": f"This represents important concepts in {subject.lower()} at {difficulty.lower()} level.",
                "topic": f"{subject} Concepts"
            }
            selected_questions.append(additional_q)

        return {
            "subject": subject,
            "difficulty": difficulty,
            "total_questions": len(selected_questions),
            "questions": selected_questions
        }

    def _create_generic_questions(self, subject: str, difficulty: str, count: int) -> List[Dict]:
        """Create educational questions for subjects not in the enhanced bank"""
        questions = []

        for i in range(count):
            questions.append({
                "question": f"What is a fundamental concept in {subject}?",
                "options": {
                    "A": f"Basic {subject.lower()} principle A",
                    "B": f"Core {subject.lower()} concept",
                    "C": f"Advanced {subject.lower()} theory",
                    "D": f"Specialized {subject.lower()} application"
                },
                "correct_answer": "B",
                "explanation": f"This question tests understanding of core {subject.lower()} concepts at {difficulty.lower()} level.",
                "topic": f"{subject} Fundamentals"
            })

        return questions

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

        # Debug: Print available keys to understand data structure
        # if quiz_results:
        #     print("Sample quiz result keys:", list(quiz_results[0].keys()))
        #     print("Sample quiz result:", quiz_results[0])

        # Analyze performance patterns
        weak_topics = []
        strong_subjects = []

        try:
            for result in quiz_results[-5:]:  # Last 5 quizzes
                # Try different possible key names for score
                score_percentage = None

                # Check various possible key names
                if 'score_percentage' in result:
                    score_percentage = result['score_percentage']
                elif 'score' in result:
                    score_percentage = result['score']
                elif 'percentage' in result:
                    score_percentage = result['percentage']
                elif 'total_score' in result:
                    score_percentage = result['total_score']
                else:
                    # If no score found, skip this result
                    continue

                # Analyze weak performance
                if score_percentage < 70:
                    # Check if detailed_results exists
                    if 'detailed_results' in result and result['detailed_results']:
                        for detail in result['detailed_results']:
                            if not detail.get('is_correct', True):  # Default to True if key missing
                                if 'topic' in detail:
                                    weak_topics.append(detail['topic'])
                                elif 'subject' in detail:
                                    weak_topics.append(detail['subject'])

                    # Also add subject to weak topics if overall score is low
                    if 'subject' in result:
                        weak_topics.append(result['subject'])

                # Analyze strong performance
                elif score_percentage >= 85:
                    if 'subject' in result:
                        strong_subjects.append(result['subject'])

        except Exception as e:
            print(f"Error analyzing quiz results: {e}")
            return [
                "Take regular quizzes to track your progress",
                "Review explanations for incorrect answers",
                "Try different difficulty levels to challenge yourself"
            ]

        # Generate recommendations
        recommendations = []

        if weak_topics:
            # Get unique weak topics and limit to top 3
            common_weak_topics = list(set(weak_topics))[:3]
            recommendations.append(f"Focus on improving: {', '.join(common_weak_topics)}")

        if strong_subjects:
            unique_strong_subjects = list(set(strong_subjects))
            recommendations.append(f"You're excelling in {', '.join(unique_strong_subjects)}. Try advanced topics!")

        # Add general recommendations
        recommendations.extend([
            "Take quizzes regularly to track your progress",
            "Review explanations for incorrect answers",
            "Try different difficulty levels to challenge yourself"
        ])

        return recommendations[:5]

    def _reconstruct_quiz_json(self, malformed_json: str, subject: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Attempt to reconstruct quiz JSON from severely malformed text"""
        import re

        try:
            logger.info("Attempting to reconstruct quiz JSON from malformed text")
            logger.debug(f"Malformed JSON sample: {malformed_json[:500]}...")

            # Try to extract questions using regex patterns
            questions = []

            # Look for question patterns - various formats
            question_patterns = [
                r'"question"["\']?\s*:\s*["\']([^"\']+)["\']',
                r'question["\']?\s*:\s*["\']([^"\']+)["\']',
                r'"question"["\']?\s*:\s*"([^"]+)"',
                r'question["\']?\s*:\s*"([^"]+)"',
                r'"question"["\']?\s*:\s*\'([^\']+)\'',
                r'question["\']?\s*:\s*\'([^\']+)\'',
                r'Question\s*\d*[:\-]?\s*([^?\n]*\?)',  # Match questions ending with ?
                r'Q\d*[:\-]?\s*([^?\n]*\?)'  # Match Q1: format
            ]

            # Look for options patterns - more flexible
            option_patterns = [
                # Standard JSON format
                r'"options"["\']?\s*:\s*\{\s*"A"["\']?\s*:\s*["\']([^"\']+)["\'][,\s]*"B"["\']?\s*:\s*["\']([^"\']+)["\'][,\s]*"C"["\']?\s*:\s*["\']([^"\']+)["\'][,\s]*"D"["\']?\s*:\s*["\']([^"\']+)["\']',
                # Without quotes around keys
                r'"options"["\']?\s*:\s*\{\s*A["\']?\s*:\s*["\']([^"\']+)["\'][,\s]*B["\']?\s*:\s*["\']([^"\']+)["\'][,\s]*C["\']?\s*:\s*["\']([^"\']+)["\'][,\s]*D["\']?\s*:\s*["\']([^"\']+)["\']',
                # Simple format: A) option B) option
                r'A\)\s*([^\n]+)\s*B\)\s*([^\n]+)\s*C\)\s*([^\n]+)\s*D\)\s*([^\n]+)',
                # Simple format: A: option B: option
                r'A:\s*([^\n]+)\s*B:\s*([^\n]+)\s*C:\s*([^\n]+)\s*D:\s*([^\n]+)',
                # Format with quotes: "A": "option"
                r'"A":\s*"([^"]+)"\s*,?\s*"B":\s*"([^"]+)"\s*,?\s*"C":\s*"([^"]+)"\s*,?\s*"D":\s*"([^"]+)"'
            ]

            # Look for correct answer patterns
            answer_patterns = [
                r'"correct_answer"["\']?\s*:\s*["\']([ABCD])["\']',
                r'correct_answer["\']?\s*:\s*["\']([ABCD])["\']',
                r'Answer[:\-\s]*([ABCD])',
                r'Correct[:\-\s]*([ABCD])',
                r'answer[:\-\s]*([ABCD])'
            ]

            # Look for explanation patterns
            explanation_patterns = [
                r'"explanation"["\']?\s*:\s*["\']([^"\']+)["\']',
                r'explanation["\']?\s*:\s*["\']([^"\']+)["\']',
                r'Explanation[:\-]\s*([^\n]+)',
                r'Because[:\-]?\s*([^\n]+)',
                r'This is because[:\-]?\s*([^\n]+)'
            ]

            # Try to find all questions, options, answers, and explanations
            found_questions = []
            found_options = []
            found_answers = []
            found_explanations = []

            # Search for questions
            for pattern in question_patterns:
                matches = re.findall(pattern, malformed_json, re.IGNORECASE | re.DOTALL)
                if matches:
                    found_questions.extend([match.strip() for match in matches])

            # Search for options (this is trickier)
            for pattern in option_patterns:
                matches = re.findall(pattern, malformed_json, re.IGNORECASE | re.DOTALL)
                if matches:
                    found_options.extend(matches)

            # Search for answers
            for pattern in answer_patterns:
                matches = re.findall(pattern, malformed_json, re.IGNORECASE)
                if matches:
                    found_answers.extend([match.strip().upper() for match in matches])

            # Search for explanations
            for pattern in explanation_patterns:
                matches = re.findall(pattern, malformed_json, re.IGNORECASE | re.DOTALL)
                if matches:
                    found_explanations.extend([match.strip() for match in matches])

            logger.info(f"Found {len(found_questions)} questions, {len(found_options)} option sets, {len(found_answers)} answers, {len(found_explanations)} explanations")

            # If we still don't have options, try a different approach
            if not found_options and found_questions:
                logger.info("Trying alternative option extraction...")
                # Try to find options in a different way - look for A, B, C, D patterns near questions
                alt_option_pattern = r'(?:A[:\)\.])\s*([^\n\r]+)(?:\s*B[:\)\.])\s*([^\n\r]+)(?:\s*C[:\)\.])\s*([^\n\r]+)(?:\s*D[:\)\.])\s*([^\n\r]+)'
                alt_matches = re.findall(alt_option_pattern, malformed_json, re.IGNORECASE | re.DOTALL)
                if alt_matches:
                    found_options.extend(alt_matches)
                    logger.info(f"Found {len(alt_matches)} option sets using alternative pattern")

            # Reconstruct questions
            max_items = min(len(found_questions), max(len(found_options), 1))  # At least try with 1 if we have questions

            if max_items == 0:
                logger.warning("Could not extract any valid question data")
                return None

            # Pad missing data
            while len(found_answers) < max_items:
                found_answers.append("A")  # Default answer

            while len(found_explanations) < max_items:
                found_explanations.append(f"This tests knowledge of {subject.lower()} concepts.")

            # Build questions array
            for i in range(min(max_items, num_questions)):
                # Handle options
                if i < len(found_options) and found_options[i] and len(found_options[i]) >= 4:
                    # We have proper options
                    options = {
                        "A": str(found_options[i][0]).strip(),
                        "B": str(found_options[i][1]).strip(),
                        "C": str(found_options[i][2]).strip(),
                        "D": str(found_options[i][3]).strip()
                    }
                else:
                    # Generate default options
                    options = {
                        "A": f"Option A for {subject.lower()}",
                        "B": f"Option B for {subject.lower()}",
                        "C": f"Option C for {subject.lower()}",
                        "D": f"Option D for {subject.lower()}"
                    }

                question = {
                    "id": i + 1,
                    "question": found_questions[i] if i < len(found_questions) else f"Question {i+1} about {subject}",
                    "options": options,
                    "correct_answer": found_answers[i] if i < len(found_answers) else "A",
                    "explanation": found_explanations[i] if i < len(found_explanations) else f"This tests {subject.lower()} knowledge.",
                    "topic": f"{subject} Concepts"
                }
                questions.append(question)

            if not questions:
                logger.warning("No valid questions could be reconstructed")
                return None

            # Build final quiz structure
            reconstructed_quiz = {
                "subject": subject,
                "difficulty": difficulty,
                "total_questions": len(questions),
                "questions": questions
            }

            logger.info(f"Successfully reconstructed quiz with {len(questions)} questions")
            return reconstructed_quiz

        except Exception as e:
            logger.error(f"Error in JSON reconstruction: {e}")
            return None


