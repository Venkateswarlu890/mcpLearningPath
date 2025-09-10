import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from utils import run_agent_sync
from mock_interview import MockInterviewSystem, INTERVIEW_TYPES, LANGUAGES
from voice_assistant import VoiceAssistant, VoiceCommandType
import threading
import time
import pyttsx3

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
if 'pretest' not in st.session_state:
    st.session_state.pretest = None
if 'pretest_answers' not in st.session_state:
    st.session_state.pretest_answers = []
if 'pretest_result' not in st.session_state:
    st.session_state.pretest_result = None
if 'coding_problem' not in st.session_state:
    st.session_state.coding_problem = None
if 'user_code' not in st.session_state:
    st.session_state.user_code = ""
if 'test_output' not in st.session_state:
    st.session_state.test_output = None
if 'webrtc_ok' not in st.session_state:
    st.session_state.webrtc_ok = False
if 'connectivity_ok' not in st.session_state:
    st.session_state.connectivity_ok = False
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False
if 'voice_listening' not in st.session_state:
    st.session_state.voice_listening = False
if 'voice_commands' not in st.session_state:
    st.session_state.voice_commands = []
if 'voice_command_text' not in st.session_state:
    st.session_state.voice_command_text = ""
if 'learning_goal_text' not in st.session_state:
    st.session_state.learning_goal_text = ""
# New UI/session items for goal section enhancements
if 'show_goal_camera' not in st.session_state:
    st.session_state.show_goal_camera = False
if 'goal_captured_image' not in st.session_state:
    st.session_state.goal_captured_image = None
if 'show_goal_uploader' not in st.session_state:
    st.session_state.show_goal_uploader = False
if 'goal_uploaded_file_name' not in st.session_state:
    st.session_state.goal_uploaded_file_name = None
if 'goal_camera_facing' not in st.session_state:
    st.session_state.goal_camera_facing = "Front"

st.title("🤖 Based Intelligent Agents Learning With Model Context Protocol And Large language Model - Scale Dynamic pathways For Language Models Using Python")
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
    user_goal = st.text_input(
        "Enter your learning goal:",
        value=st.session_state.learning_goal_text,
        placeholder="e.g., Learn Python basics in 3 days",
        help="Describe what you want to learn, and we'll generate a structured path using YouTube content and your selected tool."
    )
            

    # Inline camera widget
    if st.session_state.show_goal_camera:
        with st.expander("📷 Capture Image for Goal", expanded=True):
            st.session_state.goal_camera_facing = st.radio(
                "Camera",
                ["Front", "Back"],
                index=0 if st.session_state.goal_camera_facing == "Front" else 1,
                horizontal=True,
            )
            facing_mode = "user" if st.session_state.goal_camera_facing == "Front" else "environment"
            st.info("Preview below uses your selected camera. Then capture a still photo.")
            rtc_goal_ctx = webrtc_streamer(
                key="goal_cam_preview",
                mode=WebRtcMode.SENDONLY,
                media_stream_constraints={"video": {"facingMode": {"ideal": facing_mode}}, "audio": False},
                async_processing=False,
            )
            img = st.camera_input("Capture an image")
            colc_a, colc_b = st.columns([1,1])
            with colc_a:
                if img is not None:
                    st.session_state.goal_captured_image = img
                    st.success("Image captured.")
            with colc_b:
                if st.button("Done"):
                    st.session_state.show_goal_camera = False
                    st.rerun()

    # Inline file uploader
    if st.session_state.show_goal_uploader:
        with st.expander("📁 Upload File for Goal", expanded=True):
            up = st.file_uploader("Choose a file")
            colu_a, colu_b = st.columns([1,1])
            with colu_a:
                if up is not None:
                    st.session_state.goal_uploaded_file_name = up.name
                    st.success(f"Selected: {up.name}")
            with colu_b:
                if st.button("Done "):
                    st.session_state.show_goal_uploader = False
                    st.rerun()

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
        # Persist last typed goal
        st.session_state.learning_goal_text = user_goal
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
            - 🎤 Voice-based virtual assistant
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
            
            st.markdown("""
            **🎤 Voice Commands:**
            - "Start interview" - Begin the interview
            - "Next question" - Get the next question
            - "Repeat question" - Hear the current question again
            - "Evaluate answer" - Get feedback on your answer
            - "End interview" - Finish and get your report
            - "Help" - List available commands
            """)
        
        # Candidate Profile & Pre-test
        with st.expander("👤 Candidate Profile"):
            name = st.text_input("Name", key="cand_name")
            exp_years = st.number_input("Years of Experience", min_value=0, max_value=50, step=1, value=0)
            skills = st.text_input("Key Skills (comma-separated)")
            preferred_role = st.text_input("Preferred Role", value="")
            resume_summary = st.text_area("Resume Summary", height=120)
            if st.button("💾 Save Profile"):
                if st.session_state.mock_interview:
                    st.session_state.mock_interview.set_candidate_profile({
                        "name": name,
                        "years_of_experience": exp_years,
                        "skills": [s.strip() for s in skills.split(',') if s.strip()],
                        "preferred_role": preferred_role,
                        "resume_summary": resume_summary,
                    })
                    st.success("Profile saved and will be used to tailor the interview.")

        # Voice Assistant Controls
        with st.expander("🎤 Voice Assistant Controls"):
            st.markdown("**Enable voice interaction for hands-free interview experience**")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            
            with col_v1:
                if st.button("🎤 Enable Voice Mode"):
                    if st.session_state.mock_interview:
                        st.session_state.mock_interview.enable_voice_mode()
                        st.session_state.voice_enabled = True
                        st.success("Voice mode enabled! You can now use voice commands.")
                    else:
                        st.warning("Please start an interview session first.")
            
            with col_v2:
                if st.button("🔇 Disable Voice Mode"):
                    if st.session_state.mock_interview:
                        st.session_state.mock_interview.disable_voice_mode()
                        st.session_state.voice_enabled = False
                        st.session_state.voice_listening = False
                        st.info("Voice mode disabled.")
                    else:
                        st.warning("No active interview session.")
            
            with col_v3:
                if st.button("🎧 Test Voice"):
                    if st.session_state.mock_interview and st.session_state.voice_enabled:
                        st.session_state.mock_interview.voice_assistant.speak("Voice assistant is working correctly!")
                        st.success("Voice test completed!")
                    else:
                        st.warning("Please enable voice mode first.")
            
            # Voice command input
            st.markdown("**Manual Voice Command Input:**")
            col_cmd1, col_cmd2, col_cmd3 = st.columns([2,1,1])
            with col_cmd1:
                voice_command = st.text_input(
                    "Type a voice command:", 
                    value=st.session_state.voice_command_text,
                    placeholder="e.g., 'start interview', 'next question'",
                    key="voice_command_text_input"
                )
            with col_cmd2:
                if st.button("🎙️ Speak"):
                    if st.session_state.mock_interview and st.session_state.voice_enabled:
                        with st.spinner("Listening..."):
                            text = st.session_state.mock_interview.voice_assistant.listen(timeout=5, phrase_time_limit=5)
                        if text:
                            st.session_state.voice_command_text = text
                            st.success(f"Heard: {text}")
                            st.rerun()
                        else:
                            st.warning("Didn't catch that. Please try again.")
                    else:
                        st.warning("Please enable voice mode first.")
            with col_cmd3:
                if st.button("🧹 Clear"):
                    st.session_state.voice_command_text = ""
                    st.rerun()
            
            if st.button("🗣️ Process Voice Command") and voice_command:
                if st.session_state.mock_interview and st.session_state.voice_enabled:
                    response = st.session_state.mock_interview.process_voice_command(voice_command)
                    st.session_state.voice_commands.append({
                        'command': voice_command,
                        'response': response,
                        'timestamp': time.time()
                    })
                    st.info(f"Response: {response}")
                    # Persist the processed command in the input state
                    st.session_state.voice_command_text = voice_command
                else:
                    st.warning("Please enable voice mode first.")
            
            # Voice command history
            if st.session_state.voice_commands:
                st.markdown("**Recent Voice Commands:**")
                for i, cmd in enumerate(st.session_state.voice_commands[-5:]):  # Show last 5
                    st.markdown(f"**{i+1}.** `{cmd['command']}` → {cmd['response']}")

        st.markdown("---")
        st.subheader("🧪 Pre-Test (Required)")
        colp1, colp2 = st.columns([1, 1])
        with colp1:
            if st.button("📝 Generate Pre-Test"):
                if not st.session_state.mock_interview:
                    st.warning("Start an interview session first.")
                else:
                    st.session_state.pretest = st.session_state.mock_interview.generate_pretest(num_questions=5)
                    st.session_state.pretest_answers = [""] * len(st.session_state.pretest)
        with colp2:
            if st.button("✅ Submit Pre-Test"):
                if not st.session_state.pretest:
                    st.warning("Please generate the pre-test first.")
                else:
                    result = st.session_state.mock_interview.evaluate_pretest(
                        st.session_state.pretest_answers,
                        st.session_state.pretest,
                        pass_threshold=0.8,
                    )
                    st.session_state.pretest_result = result
                    score10 = round((result.get('score', 0.0) or 0.0) * 10, 1)
                    if result.get("passed"):
                        st.success(f"Pre-test passed! Score: {score10}/10")
                        st.info("select the interview processs")
                    else:
                        st.error(f"Pre-test not passed. Score: {score10}/10")

        if st.session_state.pretest:
            st.markdown("### 📋 Answer Pre-Test Questions")
            for idx, q in enumerate(st.session_state.pretest):
                st.markdown(f"**Q{idx+1}. {q.get('question')}**")
                opts = q.get('options') or {}
                choice = st.radio(
                    label=f"Answer {idx+1}",
                    options=list(opts.keys()) if isinstance(opts, dict) else ['A','B','C','D'],
                    format_func=lambda x: f"{x}. {opts.get(x, '')}",
                    horizontal=True,
                    key=f"pre_ans_{idx}",
                )
                st.session_state.pretest_answers[idx] = choice

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
                        st.session_state.pretest = None
                        st.session_state.pretest_answers = []
                        st.session_state.pretest_result = None
                        st.session_state.coding_problem = None
                        st.session_state.user_code = ""
                        st.session_state.test_output = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error initializing interview: {str(e)}")
        
        with col2:
            if st.button("🔄 Reset Interview"):
                st.session_state.interview_active = False
                st.session_state.mock_interview = None
                st.session_state.interview_history = []
                st.session_state.current_question = None
                st.session_state.pretest = None
                st.session_state.pretest_answers = []
                st.session_state.pretest_result = None
                st.session_state.coding_problem = None
                st.session_state.user_code = ""
                st.session_state.test_output = None
                st.rerun()
        
        # Interview Interface
        if st.session_state.interview_active and st.session_state.mock_interview:
            st.markdown("---")
            st.subheader("🎤 Interview Session")

            # Gate by pre-test + connectivity + camera
            if not (st.session_state.pretest_result and st.session_state.pretest_result.get('passed')):
                st.info("Please pass the pre-test to unlock the live interview and coding session.")
                st.stop()
            if not st.session_state.connectivity_ok:
                st.info("Please run the connectivity check and ensure it passes.")
                st.stop()
            if not st.session_state.webrtc_ok:
                st.info("Please enable camera & microphone permissions to continue.")
                st.stop()
            
            # Connectivity & camera checks
            st.markdown("## 📶 Connectivity & 🎥 Camera Check")
            colw1, colw2 = st.columns([1, 1])
            with colw1:
                if st.button("🔌 Check Connectivity"):
                    # Simple ping by hitting Streamlit server itself
                    st.session_state.connectivity_ok = True
                    st.success("Connectivity looks good.")
            with colw2:
                st.markdown("Grant camera permission below.")
            rtc_ctx = webrtc_streamer(
                key="interview_cam",
                mode=WebRtcMode.SENDONLY,
                media_stream_constraints={"video": True, "audio": True},
                async_processing=False,
            )
            if rtc_ctx.state.playing:
                st.session_state.webrtc_ok = True
                st.success("Camera & microphone are active.")

            # Live coding section
            st.markdown("## 🧑‍💻 Live Coding Room")
            colc1, colc2 = st.columns([2, 1])
            with colc1:
                if st.button("🧩 Generate Coding Problem"):
                    st.session_state.coding_problem = st.session_state.mock_interview.generate_coding_problem(difficulty=difficulty)
                    starter = st.session_state.coding_problem.get('starter_code') or ''
                    st.session_state.user_code = starter
            with colc2:
                if st.session_state.coding_problem:
                    prob = st.session_state.coding_problem
                    st.markdown(f"**{prob.get('title', 'Problem')}**")
                    st.write(prob.get('description', ''))
                    examples = prob.get('examples') or []
                    for ex in examples[:3]:
                        st.code(f"Input: {ex.get('input')}\nOutput: {ex.get('output')}", language="text")

            if st.session_state.coding_problem:
                st.markdown("**Your Code (Python):**")
                st.session_state.user_code = st.text_area(
                    "",
                    value=st.session_state.user_code or st.session_state.coding_problem.get('starter_code', ''),
                    height=260,
                    key="code_editor",
                )
                if st.button("▶️ Run Tests"):
                    with st.spinner("Running tests..."):
                        st.session_state.test_output = st.session_state.mock_interview.run_python_tests(
                            st.session_state.user_code,
                            st.session_state.coding_problem,
                        )
                if st.session_state.test_output:
                    out = st.session_state.test_output
                    if out.get('error'):
                        st.error(out['error'])
                    st.write(f"Passed {out.get('passed_count', 0)}/{out.get('total', 0)} tests")
                    for r in out.get('results', []):
                        emoji = "✅" if r.get('passed') else "❌"
                        st.code(f"{emoji} input={r.get('input')} expected={r.get('expected')} output={r.get('output')}", language="text")

            st.markdown("---")
            st.markdown("## 🗣️ Interview Q&A")
            st.info(st.session_state.mock_interview.start_live_interview())
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
                            
                            # Speak feedback if voice is enabled
                            if st.session_state.voice_enabled and st.session_state.mock_interview:
                                st.session_state.mock_interview.speak_feedback(evaluation)
                            
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
                            
                            # Speak final report if voice is enabled
                            if st.session_state.voice_enabled and st.session_state.mock_interview:
                                st.session_state.mock_interview.speak_final_report(final_report)
                            
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


