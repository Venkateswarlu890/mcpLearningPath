import streamlit as st
from utils import run_agent_sync
from mock_interview import MockInterviewSystem, INTERVIEW_TYPES, LANGUAGES

st.set_page_config(page_title="AI Learning & Interview Platform", page_icon="🤖", layout="wide")

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = ""
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'last_section' not in st.session_state:
    st.session_state.last_section = ""
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'mock_interview' not in st.session_state:
    st.session_state.mock_interview = None
if 'interview_active' not in st.session_state:
    st.session_state.interview_active = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'interview_history' not in st.session_state:
    st.session_state.interview_history = []

st.title("🤖 AI-Powered Learning & Interview Platform")
st.markdown("**Comprehensive Learning Paths + Mock Interview Simulations**")

# Sidebar for API and URL configuration
st.sidebar.header("🔧 Configuration")

# API Key input
google_api_key = st.sidebar.text_input("Google API Key", type="password", help="Required for both Learning Path and Mock Interview features")

# Pipedream URLs
st.sidebar.subheader("🔗 Pipedream URLs")
youtube_pipedream_url = st.sidebar.text_input("YouTube URL (Required)", 
    placeholder="Enter your Pipedream YouTube URL")

# Secondary tool selection
secondary_tool = st.sidebar.radio(
    "Select Secondary Tool:",
    ["Drive", "Notion"]
)

# Secondary tool URL input
if secondary_tool == "Drive":
    drive_pipedream_url = st.sidebar.text_input("Drive URL", 
        placeholder="Enter your Pipedream Drive URL")
    notion_pipedream_url = None
else:
    notion_pipedream_url = st.sidebar.text_input("Notion URL", 
        placeholder="Enter your Pipedream Notion URL")
    drive_pipedream_url = None

# Create tabs
tab1, tab2 = st.tabs(["📚 Learning Path Generator", "🎯 Mock Interview Simulator"])

# Tab 1: Learning Path Generator
with tab1:
    st.header("📚 AI-Powered Learning Path Generator")
    st.markdown("Generate personalized learning paths using YouTube content and external resources")
    
    # Quick guide
    st.info("""
    **Quick Guide:**
    1. Enter your Google API key and YouTube URL (required)
    2. Select and configure your secondary tool (Drive or Notion)
    3. Enter a clear learning goal, for example:
        - "I want to learn python basics in 3 days"
        - "I want to learn data science basics in 10 days"
    """)

    # Main content area
    st.subheader("🎯 Enter Your Learning Goal")
    user_goal = st.text_input("Enter your learning goal:",
                            help="Describe what you want to learn, and we'll generate a structured path using YouTube content and your selected tool.")

    # Progress area
    progress_container = st.container()
    progress_bar = st.empty()

    def update_progress(message: str):
        """Update progress in the Streamlit UI"""
        st.session_state.current_step = message
        
        # Determine section and update progress
        if "Setting up agent with tools" in message:
            section = "Setup"
            st.session_state.progress = 0.1
        elif "Added Google Drive integration" in message or "Added Notion integration" in message:
            section = "Integration"
            st.session_state.progress = 0.2
        elif "Creating AI agent" in message:
            section = "Setup"
            st.session_state.progress = 0.3
        elif "Generating your learning path" in message:
            section = "Generation"
            st.session_state.progress = 0.5
        elif "Learning path generation complete" in message:
            section = "Complete"
            st.session_state.progress = 1.0
            st.session_state.is_generating = False
        else:
            section = st.session_state.last_section or "Progress"
        
        st.session_state.last_section = section
        
        # Show progress bar
        progress_bar.progress(st.session_state.progress)
        
        # Update progress container with current status
        with progress_container:
            # Show section header if it changed
            if section != st.session_state.last_section and section != "Complete":
                st.write(f"**{section}**")
            
            # Show message with tick for completed steps
            if message == "Learning path generation complete!":
                st.success("All steps completed! 🎉")
            else:
                prefix = "✓" if st.session_state.progress >= 0.5 else "→"
                st.write(f"{prefix} {message}")

    # Generate Learning Path button
    if st.button("🚀 Generate Learning Path", type="primary", disabled=st.session_state.is_generating):
        if not google_api_key:
            st.error("Please enter your Google API key in the sidebar.")
        elif not youtube_pipedream_url:
            st.error("YouTube URL is required. Please enter your Pipedream YouTube URL in the sidebar.")
        elif (secondary_tool == "Drive" and not drive_pipedream_url) or (secondary_tool == "Notion" and not notion_pipedream_url):
            st.error(f"Please enter your Pipedream {secondary_tool} URL in the sidebar.")
        elif not user_goal:
            st.warning("Please enter your learning goal.")
        else:
            try:
                # Set generating flag
                st.session_state.is_generating = True
                
                # Reset progress
                st.session_state.current_step = ""
                st.session_state.progress = 0
                st.session_state.last_section = ""
                
                result = run_agent_sync(
                    google_api_key=google_api_key,
                    youtube_pipedream_url=youtube_pipedream_url,
                    drive_pipedream_url=drive_pipedream_url,
                    notion_pipedream_url=notion_pipedream_url,
                    user_goal=user_goal,
                    progress_callback=update_progress
                )
                
                # Display results
                st.header("📖 Your Personalized Learning Path")
                if result and "messages" in result:
                    for msg in result["messages"]:
                        st.markdown(f"📚 {msg.content}")
                else:
                    st.error("No results were generated. Please try again.")
                    st.session_state.is_generating = False
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your API keys and URLs, and try again.")
                st.session_state.is_generating = False

# Tab 2: Mock Interview Simulator
with tab2:
    st.header("🎯 AI-Powered Mock Interview Simulator")
    st.markdown("Practice interviews with AI-driven simulations in multiple languages")
    
    if not google_api_key:
        st.warning("⚠️ Please enter your Google API key in the sidebar to use the Mock Interview feature.")
    else:
        # Interview Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Interview Setup")
            
            # Interview type selection
            interview_category = st.selectbox(
                "Select Interview Category:",
                ["Technical", "Behavioral"]
            )
            
            # Role selection based on category
            if interview_category == "Technical":
                role = st.selectbox(
                    "Select Role:",
                    list(INTERVIEW_TYPES["technical"].keys()),
                    format_func=lambda x: INTERVIEW_TYPES["technical"][x]
                )
            else:
                role = st.selectbox(
                    "Select Role:",
                    list(INTERVIEW_TYPES["behavioral"].keys()),
                    format_func=lambda x: INTERVIEW_TYPES["behavioral"][x]
                )
            
            # Language selection
            language = st.selectbox(
                "Select Language:",
                list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x]
            )
            
            # Difficulty selection
            difficulty = st.selectbox(
                "Select Difficulty:",
                ["beginner", "intermediate", "advanced"]
            )
        
        with col2:
            st.subheader("📊 Interview Features")
            st.markdown("""
            **✨ Features:**
            - 🤖 AI-driven interview questions
            - 📝 Real-time feedback and evaluation
            - 🌍 Multi-language support (English, Telugu, Hindi)
            - 📈 Performance scoring and analysis
            - 🎯 Personalized difficulty levels
            - 📋 Comprehensive final reports
            """)
            
            st.markdown("""
            **🎯 Interview Types:**
            - **Technical:** Python, Data Science, ML, Web Dev, DevOps
            - **Behavioral:** Leadership, Teamwork, Problem Solving
            """)
        
        # Start/Reset Interview
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start New Interview", type="primary"):
                if not st.session_state.interview_active:
                    try:
                        # Initialize mock interview system
                        st.session_state.mock_interview = MockInterviewSystem(google_api_key)
                        st.session_state.mock_interview.initialize_interview(
                            interview_type=interview_category.lower(),
                            role=role,
                            language=language,
                            difficulty=difficulty
                        )
                        st.session_state.interview_active = True
                        st.session_state.interview_history = []
                        st.session_state.current_question = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error initializing interview: {str(e)}")
        
        with col2:
            if st.button("🔄 Reset Interview"):
                st.session_state.interview_active = False
                st.session_state.mock_interview = None
                st.session_state.interview_history = []
                st.session_state.current_question = None
                st.rerun()
        
        # Interview Interface
        if st.session_state.interview_active and st.session_state.mock_interview:
            st.markdown("---")
            st.subheader("🎤 Interview Session")
            
            # Get current question if not set
            if st.session_state.current_question is None:
                with st.spinner("🤖 Preparing your first question..."):
                    question_data = st.session_state.mock_interview.get_next_question()
                    st.session_state.current_question = question_data
            
            # Display current question
            if st.session_state.current_question:
                question_data = st.session_state.current_question
                
                # Question display
                st.markdown(f"**Question {question_data['question_number']}/{question_data['total_questions']}:**")
                st.info(f"🤔 {question_data['question']}")
                
                # Answer input
                candidate_answer = st.text_area(
                    "Your Answer:",
                    placeholder="Type your answer here...",
                    height=150
                )
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("📤 Submit Answer"):
                        if candidate_answer.strip():
                            # Evaluate answer
                            with st.spinner("🤖 Evaluating your answer..."):
                                evaluation = st.session_state.mock_interview.evaluate_answer(
                                    question_data['question'], 
                                    candidate_answer
                                )
                                
                                # Store in history
                                st.session_state.interview_history.append({
                                    'question': question_data['question'],
                                    'answer': candidate_answer,
                                    'evaluation': evaluation
                                })
                                
                                # Get next question
                                next_question = st.session_state.mock_interview.get_next_question(candidate_answer)
                                st.session_state.current_question = next_question
                                
                                st.rerun()
                        else:
                            st.warning("Please provide an answer before submitting.")
                
                with col2:
                    if st.button("⏭️ Skip Question"):
                        # Get next question without evaluation
                        next_question = st.session_state.mock_interview.get_next_question("I would like to skip this question.")
                        st.session_state.current_question = next_question
                        st.rerun()
                
                # Display evaluation if available
                if st.session_state.interview_history:
                    st.markdown("---")
                    st.subheader("📊 Recent Evaluations")
                    
                    for i, history_item in enumerate(st.session_state.interview_history[-3:]):  # Show last 3
                        with st.expander(f"Question {i+1}: {history_item['question'][:50]}..."):
                            evaluation = history_item['evaluation']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Technical", f"{evaluation.get('technical_score', 0)}/10")
                            with col2:
                                st.metric("Communication", f"{evaluation.get('communication_score', 0)}/10")
                            with col3:
                                st.metric("Overall", f"{evaluation.get('overall_score', 0)}/10")
                            
                            st.markdown("**Strengths:**")
                            for strength in evaluation.get('strengths', []):
                                st.markdown(f"✅ {strength}")
                            
                            st.markdown("**Areas for Improvement:**")
                            for improvement in evaluation.get('improvements', []):
                                st.markdown(f"🔧 {improvement}")
                            
                            st.markdown(f"**Feedback:** {evaluation.get('feedback', 'No feedback available')}")
                
                # End interview option
                if len(st.session_state.interview_history) >= 5:  # Allow ending after 5 questions
                    st.markdown("---")
                    if st.button("🏁 End Interview & Generate Report"):
                        with st.spinner("🤖 Generating comprehensive report..."):
                            final_report = st.session_state.mock_interview.generate_final_report()
                            
                            st.markdown("---")
                            st.header("📋 Final Interview Report")
                            
                            # Overall score
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Overall Score", f"{final_report.get('overall_score', 0)}/10")
                            with col2:
                                st.metric("Questions Answered", len(st.session_state.interview_history))
                            with col3:
                                st.metric("Language", LANGUAGES.get(language, language).title())
                            
                            # Detailed assessments
                            st.subheader("📊 Detailed Assessments")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Technical Assessment:**")
                                st.info(final_report.get('technical_assessment', 'No assessment available'))
                                
                                st.markdown("**Communication Assessment:**")
                                st.info(final_report.get('communication_assessment', 'No assessment available'))
                            
                            with col2:
                                st.markdown("**Problem-Solving Assessment:**")
                                st.info(final_report.get('problem_solving_assessment', 'No assessment available'))
                            
                            # Strengths and weaknesses
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**💪 Strengths:**")
                                for strength in final_report.get('strengths', []):
                                    st.markdown(f"✅ {strength}")
                            
                            with col2:
                                st.markdown("**🔧 Areas for Improvement:**")
                                for weakness in final_report.get('weaknesses', []):
                                    st.markdown(f"⚠️ {weakness}")
                            
                            # Recommendations
                            st.subheader("🎯 Recommendations")
                            for recommendation in final_report.get('recommendations', []):
                                st.markdown(f"💡 {recommendation}")
                            
                            # Next steps
                            st.subheader("🚀 Next Steps")
                            for step in final_report.get('next_steps', []):
                                st.markdown(f"📈 {step}")
                            
                            # Detailed feedback
                            st.subheader("📝 Detailed Feedback")
                            st.markdown(final_report.get('detailed_feedback', 'No detailed feedback available'))
                            
                            # Reset interview
                            if st.button("🔄 Start New Interview"):
                                st.session_state.interview_active = False
                                st.session_state.mock_interview = None
                                st.session_state.interview_history = []
                                st.session_state.current_question = None
                                st.rerun()
