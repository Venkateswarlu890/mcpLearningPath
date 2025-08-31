from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Callable, Any, List, Dict
import asyncio
import json
import re

# Interview configurations
INTERVIEW_TYPES = {
    "technical": {
        "python": "Python Developer",
        "data_science": "Data Scientist", 
        "machine_learning": "Machine Learning Engineer",
        "web_development": "Full Stack Developer",
        "devops": "DevOps Engineer"
    },
    "behavioral": {
        "general": "General Behavioral",
        "leadership": "Leadership & Management",
        "teamwork": "Team Collaboration",
        "problem_solving": "Problem Solving"
    }
}

LANGUAGES = {
    "english": "English",
    "telugu": "Telugu", 
    "hindi": "Hindi"
}

class MockInterviewSystem:
    def __init__(self, google_api_key: str):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key
        )
        self.conversation_history = []
        self.current_question_index = 0
        self.interview_type = None
        self.language = "english"
        self.difficulty = "intermediate"
        
    def initialize_interview(self, interview_type: str, role: str, language: str = "english", difficulty: str = "intermediate"):
        """Initialize the mock interview session"""
        self.interview_type = interview_type
        self.role = role
        self.language = language
        self.difficulty = difficulty
        self.current_question_index = 0
        self.conversation_history = []
        
        # Create interview setup prompt
        setup_prompt = self._create_setup_prompt()
        return setup_prompt
    
    def _create_setup_prompt(self) -> str:
        """Create the initial interview setup prompt"""
        language_instructions = {
            "english": "Conduct the interview in English.",
            "telugu": "Conduct the interview in Telugu. If the candidate responds in English, continue in Telugu.",
            "hindi": "Conduct the interview in Hindi. If the candidate responds in English, continue in Hindi."
        }
        
        difficulty_instructions = {
            "beginner": "Ask basic, fundamental questions suitable for entry-level candidates.",
            "intermediate": "Ask moderate difficulty questions that test practical knowledge and experience.",
            "advanced": "Ask challenging questions that test deep understanding and problem-solving skills."
        }
        
        prompt = f"""
You are an expert {self.interview_type} interviewer conducting a mock interview for a {self.role} position.

{difficulty_instructions.get(self.difficulty, difficulty_instructions["intermediate"])}
{language_instructions.get(self.language, language_instructions["english"])}

Interview Guidelines:
1. Ask one question at a time
2. Provide constructive feedback after each answer
3. Ask follow-up questions when appropriate
4. Maintain a professional but friendly tone
5. Focus on both technical skills and soft skills
6. Provide specific examples and scenarios
7. Give actionable feedback for improvement

Start the interview with a brief introduction and your first question.
"""
        return prompt
    
    def get_next_question(self, candidate_response: str = "") -> Dict[str, Any]:
        """Get the next interview question based on candidate's response"""
        if not self.conversation_history:
            # First question
            initial_prompt = self._create_setup_prompt()
            messages = [HumanMessage(content=initial_prompt)]
        else:
            # Continue conversation
            messages = self.conversation_history + [HumanMessage(content=candidate_response)]
        
        try:
            response = self.model.invoke(messages)
            self.conversation_history = messages + [response]
            
            # Extract question and feedback
            content = response.content
            question, feedback = self._parse_response(content)
            
            return {
                "question": question,
                "feedback": feedback,
                "question_number": self.current_question_index + 1,
                "total_questions": 10  # We'll do 10 questions per session
            }
        except Exception as e:
            return {
                "question": f"Error generating question: {str(e)}",
                "feedback": "",
                "question_number": self.current_question_index + 1,
                "total_questions": 10
            }
    
    def _parse_response(self, content: str) -> tuple:
        """Parse the AI response to extract question and feedback"""
        # Simple parsing - in a real implementation, you might want more sophisticated parsing
        lines = content.split('\n')
        question = ""
        feedback = ""
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if not question:
                    question = line
                else:
                    feedback += line + " "
        
        return question, feedback.strip()
    
    def evaluate_answer(self, question: str, answer: str) -> Dict[str, Any]:
        """Evaluate the candidate's answer and provide detailed feedback"""
        evaluation_prompt = f"""
As an expert interviewer, evaluate this candidate's answer:

Question: {question}
Answer: {answer}

Provide a detailed evaluation including:
1. Technical accuracy (1-10)
2. Communication clarity (1-10)
3. Problem-solving approach (1-10)
4. Specific strengths
5. Areas for improvement
6. Overall score (1-10)
7. Next question suggestion

Format your response as JSON:
{{
    "technical_score": 8,
    "communication_score": 7,
    "problem_solving_score": 9,
    "strengths": ["Good technical knowledge", "Clear explanation"],
    "improvements": ["Could provide more examples", "Should elaborate on implementation"],
    "overall_score": 8,
    "feedback": "Detailed feedback here",
    "next_question": "Suggested next question"
}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=evaluation_prompt)])
            # Try to parse JSON response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                return evaluation
            else:
                return {
                    "technical_score": 7,
                    "communication_score": 7,
                    "problem_solving_score": 7,
                    "strengths": ["Good attempt"],
                    "improvements": ["Could improve"],
                    "overall_score": 7,
                    "feedback": content,
                    "next_question": "Continue with next question"
                }
        except Exception as e:
            return {
                "technical_score": 5,
                "communication_score": 5,
                "problem_solving_score": 5,
                "strengths": ["Attempted to answer"],
                "improvements": ["Need more practice"],
                "overall_score": 5,
                "feedback": f"Error in evaluation: {str(e)}",
                "next_question": "Continue with next question"
            }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate a comprehensive final report of the interview"""
        if not self.conversation_history:
            return {"error": "No interview data available"}
        
        # Create a summary of the entire interview
        conversation_summary = "\n".join([
            f"{'Interviewer' if i % 2 == 0 else 'Candidate'}: {msg.content}"
            for i, msg in enumerate(self.conversation_history)
        ])
        
        report_prompt = f"""
Based on this mock interview conversation, generate a comprehensive final report:

{conversation_summary}

Provide a detailed report including:
1. Overall performance assessment
2. Technical skills evaluation
3. Communication skills evaluation
4. Problem-solving abilities
5. Specific strengths and weaknesses
6. Recommendations for improvement
7. Suggested next steps for preparation
8. Overall interview score (1-10)

Format as JSON:
{{
    "overall_score": 8,
    "technical_assessment": "Detailed technical evaluation",
    "communication_assessment": "Communication skills evaluation",
    "problem_solving_assessment": "Problem-solving evaluation",
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "next_steps": ["Step 1", "Step 2"],
    "detailed_feedback": "Comprehensive feedback"
}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=report_prompt)])
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                report = json.loads(json_match.group())
                return report
            else:
                return {
                    "overall_score": 7,
                    "technical_assessment": "Good technical knowledge demonstrated",
                    "communication_assessment": "Clear communication skills",
                    "problem_solving_assessment": "Good problem-solving approach",
                    "strengths": ["Technical knowledge", "Communication"],
                    "weaknesses": ["Could improve in some areas"],
                    "recommendations": ["Practice more", "Study specific topics"],
                    "next_steps": ["Continue learning", "Practice interviews"],
                    "detailed_feedback": content
                }
        except Exception as e:
            return {
                "overall_score": 5,
                "technical_assessment": "Basic technical knowledge",
                "communication_assessment": "Basic communication skills",
                "problem_solving_assessment": "Basic problem-solving skills",
                "strengths": ["Willingness to learn"],
                "weaknesses": ["Needs improvement"],
                "recommendations": ["Practice more", "Study fundamentals"],
                "next_steps": ["Continue learning", "Practice regularly"],
                "detailed_feedback": f"Error generating report: {str(e)}"
            }

def create_interview_questions(role: str, interview_type: str, language: str = "english") -> List[str]:
    """Generate sample interview questions based on role and type"""
    questions = {
        "python": [
            "Explain the difference between lists and tuples in Python.",
            "What are decorators and how do you use them?",
            "Explain the concept of generators in Python.",
            "How do you handle exceptions in Python?",
            "What is the difference between deep copy and shallow copy?"
        ],
        "data_science": [
            "Explain the difference between supervised and unsupervised learning.",
            "What is overfitting and how do you prevent it?",
            "Explain the concept of cross-validation.",
            "How do you handle missing data in a dataset?",
            "What is the difference between correlation and causation?"
        ],
        "machine_learning": [
            "Explain the bias-variance tradeoff.",
            "What are the different types of clustering algorithms?",
            "How do you evaluate a machine learning model?",
            "Explain the concept of feature engineering.",
            "What is regularization and why is it important?"
        ]
    }
    
    return questions.get(role, [
        "Tell me about your experience with this technology.",
        "How do you approach problem-solving?",
        "Describe a challenging project you worked on.",
        "How do you stay updated with industry trends?",
        "What are your career goals?"
    ])
