# EduTutor AI - Personalized Learning Platform

## Overview

EduTutor AI is a Streamlit-based educational platform that provides personalized quiz experiences powered by IBM Watson AI. The application allows users to create accounts, take AI-generated quizzes on various subjects, and track their learning progress through comprehensive analytics.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit (Python web framework)
- **UI Pattern**: Multi-page application with session-based navigation
- **Layout**: Wide layout with expandable sidebar for navigation
- **Visualization**: Plotly for interactive charts and analytics

### Backend Architecture
- **Runtime**: Python-based server-side rendering
- **Session Management**: Streamlit's built-in session state for user authentication and data persistence
- **AI Integration**: IBM Watson AI (Granite 3-8B Instruct model) for quiz generation
- **Data Storage**: In-memory storage using Streamlit session state (no persistent database)

### Authentication System
- Simple username/password authentication stored in session state
- No encryption or hashing implemented (development/demo purposes)
- Demo account available for testing (username: demo, password: demo123)

## Key Components

### Core Modules

1. **App.py** - Main application entry point and routing logic
2. **Pages Module** - Contains all UI pages:
   - `login.py` - Authentication interface
   - `dashboard.py` - Main learning dashboard with metrics and charts
   - `quiz.py` - Quiz generation and taking interface
   - `analytics.py` - Comprehensive learning analytics and insights

3. **Services Module**:
   - `ai_service.py` - IBM Watson AI integration for quiz generation

4. **Utils Module**:
   - `session_manager.py` - User session and authentication management

### Page Structure
- **Login/Registration**: Tab-based interface for user onboarding
- **Dashboard**: Overview metrics, performance charts, and recommendations
- **Quiz Taking**: AI-powered quiz generation with configurable subjects and difficulty
- **Analytics**: Detailed performance tracking and learning insights

## Data Flow

### User Journey
1. User authenticates via login page
2. Redirected to dashboard showing learning overview
3. Can navigate to take quizzes with AI-generated questions
4. Quiz results are stored in session state
5. Analytics page provides insights based on quiz history

### AI Quiz Generation Flow
1. User selects subject, difficulty, and number of questions
2. AI service constructs prompt for IBM Granite model
3. Model generates structured quiz with questions and answers
4. Quiz is presented to user with interactive interface
5. Results are calculated and stored in user's quiz history

### Data Persistence
- All data stored in Streamlit session state (temporary)
- User accounts, quiz history, and settings reset on browser refresh
- No database integration (purely in-memory storage)

## External Dependencies

### AI Services
- **IBM Watson AI**: Primary AI service for quiz generation
- **Model**: IBM Granite 3-8B Instruct
- **Authentication**: API key and project ID based
- **Region**: EU-GB (Europe - Great Britain)

### Python Libraries
- **streamlit**: Web application framework
- **plotly**: Interactive data visualization
- **pandas**: Data manipulation and analysis
- **ibm-watsonx-ai**: IBM Watson AI SDK
- **datetime**: Date and time utilities

### Configuration Requirements
- IBM_API_KEY environment variable
- IBM_PROJECT_ID environment variable
- Default values provided for development/testing

## Deployment Strategy

### Current Setup
- Designed for Streamlit deployment
- Single-file execution model
- Environment variables for AI service configuration
- No database setup required

### Scalability Considerations
- Session state storage limits scalability
- AI service calls may have rate limits
- No user data persistence between sessions

### Production Readiness
- Requires database integration for user persistence
- Password hashing and security improvements needed
- Error handling and logging should be enhanced
- Rate limiting for AI service calls recommended

## Changelog
- June 29, 2025: Initial setup with complete EduTutor AI platform
- June 29, 2025: Fixed navigation issues and implemented demo mode for AI service
- June 29, 2025: Added IBM Watson API integration with fallback demo content

## User Preferences

Preferred communication style: Simple, everyday language.