from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Callable, Any, List, Dict
import asyncio
import json
import re
import textwrap
from voice_assistant import VoiceAssistant, VoiceCommandType

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
        # Candidate profile/context to tailor the interview
        self.candidate_profile: Dict[str, Any] = {
            "name": None,
            "years_of_experience": None,
            "skills": [],
            "preferred_role": None,
            "resume_summary": None,
        }
        # Pre-test state
        self.pretest_passed: bool = False
        self.pretest_result: Dict[str, Any] = {}
        
        # Voice assistant integration
        self.voice_assistant = VoiceAssistant(mock_interview_system=self)
        self.voice_enabled = False
        self.current_question = None
        # Adaptive context
        self.last_evaluation: Dict[str, Any] = {}
        self.non_verbal_notes: str = ""
        
    def initialize_interview(self, interview_type: str, role: str, language: str = "english", difficulty: str = "intermediate"):
        """Initialize the mock interview session"""
        self.interview_type = interview_type
        self.role = role
        self.language = language
        self.difficulty = difficulty
        self.current_question_index = 0
        self.conversation_history = []
        self.pretest_passed = False
        self.pretest_result = {}
        
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
        
        candidate_context = ""
        if any(self.candidate_profile.values()):
            candidate_context = (
                f"Candidate Context:\n"
                f"- Name: {self.candidate_profile.get('name') or 'N/A'}\n"
                f"- Experience: {self.candidate_profile.get('years_of_experience') or 'N/A'} years\n"
                f"- Skills: {', '.join(self.candidate_profile.get('skills') or []) or 'N/A'}\n"
                f"- Preferred Role: {self.candidate_profile.get('preferred_role') or 'N/A'}\n"
                f"- Resume Summary: {self.candidate_profile.get('resume_summary') or 'N/A'}\n"
            )

        prompt = f"""
You are an expert {self.interview_type} interviewer conducting a mock interview for a {self.role} position.

{candidate_context}
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
    
    def set_candidate_profile(self, profile: Dict[str, Any]) -> None:
        """Set or update candidate profile for tailoring interview."""
        self.candidate_profile.update(profile or {})

    def update_non_verbal_notes(self, notes: str) -> None:
        """Update notes about candidate's non-verbal cues (confidence, clarity, body language)."""
        self.non_verbal_notes = (notes or "").strip()

    def generate_pretest(self, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate a short pre-test to gate the live interview."""
        skill_hint = ", ".join(self.candidate_profile.get("skills") or [])
        resume_snippet = self.candidate_profile.get("resume_summary") or ""
        prompt = f"""
Create a {num_questions}-question multiple-choice pre-test for a candidate applying for {self.role}.
Tailor difficulty to {self.difficulty} and {self.interview_type}. Consider candidate skills: {skill_hint}.
Resume context: {resume_snippet}
Return JSON list where each item has: question, options (A-D), correct_option (A-D).
"""
        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            content = response.content
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                return questions
        except Exception:
            pass
        # Fallback simple pretest
        return [
            {
                "question": "Which data structure is immutable in Python?",
                "options": {"A": "List", "B": "Dictionary", "C": "Tuple", "D": "Set"},
                "correct_option": "C",
            }
        ]

    def evaluate_pretest(self, answers: List[str], questions: List[Dict[str, Any]], pass_threshold: float = 0.6) -> Dict[str, Any]:
        """Evaluate pre-test answers and set pass state."""
        total = min(len(answers), len(questions))
        correct = 0
        details: List[Dict[str, Any]] = []
        for idx in range(total):
            q = questions[idx]
            correct_option = (q.get("correct_option") or "").strip().upper()
            user_option = (answers[idx] or "").strip().upper()
            is_correct = user_option == correct_option
            if is_correct:
                correct += 1
            details.append({
                "question": q.get("question"),
                "selected": user_option,
                "correct": correct_option,
                "is_correct": is_correct,
            })
        score = (correct / total) if total else 0.0
        passed = score >= pass_threshold
        self.pretest_passed = passed
        self.pretest_result = {
            "total": total,
            "correct": correct,
            "score": score,
            "passed": passed,
            "details": details,
        }
        return self.pretest_result

    def start_live_interview(self) -> str:
        """Prepare the AI Agent live interview introduction. Requires pre-test pass."""
        if not self.pretest_passed:
            return "Pre-test not passed. Complete and pass the pre-test to start the live interview."
        agent_intro = (
            "You are an AI Interview Agent conducting a face-to-face style live interview. "
            "Follow real-time, adaptive questioning, ask one question at a time, and wait for candidate responses. "
            "Be empathetic, professional, and keep the session focused on the candidate's profile and role."
        )
        return agent_intro
    
    # ===== Real-time Coding Interview Helpers =====
    def generate_coding_problem(self, difficulty: Optional[str] = None) -> Dict[str, Any]:
        """Ask LLM to produce a coding problem statement with examples and hidden tests."""
        level = difficulty or self.difficulty
        skills = ", ".join(self.candidate_profile.get("skills") or [])
        prompt = f"""
Create one coding interview problem suitable for a live coding session.
Target role: {self.role}. Difficulty: {level}. Candidate skills: {skills}.
Return as JSON with fields: title, description, function_signature (Python), examples (array of {{input, output}}), starter_code, and tests (array of {{input, expected}}). Keep tests concise.
"""
        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            content = response.content
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                problem = json.loads(json_match.group())
                return problem
        except Exception:
            pass
        
        # Fallback simple problem
        return {
            "title": "Reverse String",
            "description": "Given a string s, return the reverse of s.",
            "function_signature": "def reverse_string(s: str) -> str:",
            "examples": [{"input": "hello", "output": "olleh"}],
            "starter_code": "def reverse_string(s: str) -> str:\n    # TODO: implement\n    return ''\n",
            "tests": [
                {"input": "hello", "expected": "olleh"},
                {"input": "", "expected": ""},
                {"input": "a", "expected": "a"}
            ],
        }

    def generate_questions_from_topic(self, topic: str, num_questions: int = 5) -> List[str]:
        """Generate a list of interview questions based on a user-provided topic or role."""
        topic = (topic or "").strip()
        if not topic:
            return []
        guide = f"Generate {num_questions} professional interview questions about '{topic}' tailored for a {self.role} role. One line per question, concise, no answers."
        try:
            response = self.model.invoke([HumanMessage(content=guide)])
            lines = [l.strip("- ") for l in response.content.splitlines() if l.strip()]
            # Filter likely question lines
            questions = [l for l in lines if l.endswith("?") or l.lower().startswith(("what", "how", "why", "when", "where", "which", "explain", "describe", "tell"))]
            if not questions:
                questions = lines[:num_questions]
            return questions[:num_questions]
        except Exception:
            # Minimal fallback
            return [f"Tell me about your experience with {topic}.", f"What are key challenges in {topic}?", f"How do you approach problems in {topic}?", f"Explain a project using {topic}.", f"What best practices do you follow in {topic}?"]

    def run_python_tests(self, user_code: str, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Very lightweight exec-based runner to validate deterministic examples. Not for untrusted code in production."""
        namespace: Dict[str, Any] = {}
        results: List[Dict[str, Any]] = []
        error: Optional[str] = None
        try:
            full_code = textwrap.dedent(user_code)
            exec(full_code, namespace)  # WARNING: Unsafe; acceptable for local mock usage only
            # Infer function name from signature or starter
            func_name = None
            sig = problem.get("function_signature") or ""
            m = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", sig)
            if m:
                func_name = m.group(1)
            if not func_name:
                error = "Unable to infer function name from signature."
            else:
                func = namespace.get(func_name)
                if not callable(func):
                    error = f"Function {func_name} not found or not callable."
                else:
                    for t in problem.get("tests", []):
                        test_input = t.get("input")
                        expected = t.get("expected")
                        try:
                            output = func(test_input)
                            passed = output == expected
                            results.append({
                                "input": test_input,
                                "expected": expected,
                                "output": output,
                                "passed": passed,
                            })
                        except Exception as inner_e:
                            results.append({
                                "input": test_input,
                                "expected": expected,
                                "output": str(inner_e),
                                "passed": False,
                            })
        except Exception as e:
            error = str(e)

        summary = {
            "passed": all(r.get("passed") for r in results) if results else False,
            "total": len(results),
            "passed_count": sum(1 for r in results if r.get("passed")),
            "error": error,
            "results": results,
        }
        return summary
    
    def get_next_question(self, candidate_response: str = "") -> Dict[str, Any]:
        """Get the next interview question based on candidate's response with adaptive follow-ups and optional hints."""
        if not self.pretest_passed:
            return {
                "question": "Pre-test not passed. Please complete and pass the pre-test to proceed to the live interview.",
                "feedback": "",
                "question_number": 0,
                "total_questions": 0
            }
        # Build adaptive context
        adaptive_clues = ""
        if self.last_evaluation:
            strengths = ", ".join(self.last_evaluation.get("strengths", [])[:3])
            improvements = ", ".join(self.last_evaluation.get("improvements", [])[:3])
            next_hint = self.last_evaluation.get("next_question") or ""
            adaptive_clues = (
                f"Prior evaluation summary:\n"
                f"- Strengths: {strengths or 'N/A'}\n"
                f"- Improvements: {improvements or 'N/A'}\n"
                f"- Suggested next focus: {next_hint or 'N/A'}\n"
            )
        non_verbal = f"Non-verbal cues noted: {self.non_verbal_notes}" if self.non_verbal_notes else ""
        adaptive_instructions = f"""
Act like a realistic face-to-face interviewer. Ask one question at a time and wait for the candidate.
If the candidate appears to struggle (uncertain language like 'not sure', or very brief response), give a gentle hint BEFORE asking the follow-up. Keep tone supportive but professional.
Consider any non-verbal notes if provided and keep sessions time-bounded.
{adaptive_clues}
{non_verbal}
Only output the next interviewer utterance (question and, if needed, one short hint), not JSON.
"""

        if not self.conversation_history:
            # First question with intro
            initial_prompt = self._create_setup_prompt() + "\nIntroduce yourself briefly, reassure the candidate, and ask the first tailored question."
            messages = [HumanMessage(content=initial_prompt + "\n\n" + adaptive_instructions)]
        else:
            # Continue conversation
            messages = self.conversation_history + [HumanMessage(content=candidate_response), HumanMessage(content=adaptive_instructions)]
        
        try:
            response = self.model.invoke(messages)
            self.conversation_history = messages + [response]
            
            # Extract question and feedback
            content = response.content
            question, feedback = self._parse_response(content)
            
            question_data = {
                "question": question,
                "feedback": feedback,
                "question_number": self.current_question_index + 1,
                "total_questions": 10  # We'll do 10 questions per session
            }
            
            # Store current question for voice assistant
            self.current_question = question_data
            
            # Speak the question if voice is enabled
            if self.voice_enabled and self.voice_assistant:
                self.voice_assistant.speak(f"Question {question_data['question_number']}: {question}")
            
            return question_data
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
                # Persist for adaptive follow-ups
                self.last_evaluation = evaluation
                return evaluation
            else:
                fallback = {
                    "technical_score": 7,
                    "communication_score": 7,
                    "problem_solving_score": 7,
                    "strengths": ["Good attempt"],
                    "improvements": ["Could improve"],
                    "overall_score": 7,
                    "feedback": content,
                    "next_question": "Continue with next question"
                }
                self.last_evaluation = fallback
                return fallback
        except Exception as e:
            err_eval = {
                "technical_score": 5,
                "communication_score": 5,
                "problem_solving_score": 5,
                "strengths": ["Attempted to answer"],
                "improvements": ["Need more practice"],
                "overall_score": 5,
                "feedback": f"Error in evaluation: {str(e)}",
                "next_question": "Continue with next question"
            }
            self.last_evaluation = err_eval
            return err_eval
    
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
    
    # Voice Assistant Integration Methods
    def enable_voice_mode(self):
        """Enable voice interaction mode"""
        self.voice_enabled = True
        if self.voice_assistant:
            self.voice_assistant.speak("Voice mode enabled. You can now use voice commands during the interview.")
    
    def disable_voice_mode(self):
        """Disable voice interaction mode"""
        self.voice_enabled = False
        if self.voice_assistant:
            self.voice_assistant.speak("Voice mode disabled.")
    
    def process_voice_command(self, voice_text: str) -> str:
        """Process voice command and return response"""
        if not self.voice_enabled or not self.voice_assistant:
            return "Voice mode is not enabled."
        
        # Process the voice input through the assistant
        command = self.voice_assistant.process_voice_input(voice_text)
        response = self.voice_assistant.execute_command(command)
        
        return response
    
    def start_voice_listening(self):
        """Start continuous voice listening"""
        if self.voice_enabled and self.voice_assistant:
            self.voice_assistant.start_continuous_listening()
            return "Voice listening started. Say 'help' for available commands."
        return "Voice mode is not enabled."
    
    def stop_voice_listening(self):
        """Stop continuous voice listening"""
        if self.voice_assistant:
            self.voice_assistant.stop_continuous_listening()
            return "Voice listening stopped."
        return "Voice assistant not available."
    
    def speak_question(self, question_data: Dict[str, Any]):
        """Speak the current question"""
        if self.voice_enabled and self.voice_assistant and question_data:
            question_text = f"Question {question_data.get('question_number', 1)}: {question_data.get('question', '')}"
            self.voice_assistant.speak(question_text)
    
    def speak_feedback(self, evaluation: Dict[str, Any]):
        """Speak evaluation feedback"""
        if self.voice_enabled and self.voice_assistant and evaluation:
            overall_score = evaluation.get('overall_score', 0)
            feedback_text = f"Your overall score is {overall_score} out of 10. {evaluation.get('feedback', '')}"
            self.voice_assistant.speak(feedback_text)
    
    def speak_final_report(self, report: Dict[str, Any]):
        """Speak the final interview report"""
        if self.voice_enabled and self.voice_assistant and report:
            overall_score = report.get('overall_score', 0)
            report_text = f"Interview completed. Your overall score is {overall_score} out of 10. "
            
            # Add key strengths
            strengths = report.get('strengths', [])
            if strengths:
                report_text += f"Your key strengths include: {', '.join(strengths[:3])}. "
            
            # Add recommendations
            recommendations = report.get('recommendations', [])
            if recommendations:
                report_text += f"Recommendations for improvement: {', '.join(recommendations[:2])}."
            
            self.voice_assistant.speak(report_text)
    

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
