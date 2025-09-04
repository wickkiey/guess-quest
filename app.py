"""
Streamlit Interview Application with CrewAI and Ollama
"""

import streamlit as st
import time
from typing import Optional
from ollama_client import OllamaClient
from agents import InterviewCrew


def init_session_state():
    """Initialize session state variables"""
    if 'ollama_client' not in st.session_state:
        st.session_state.ollama_client = None
    if 'interview_crew' not in st.session_state:
        st.session_state.interview_crew = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = ""
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = ""
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    if 'waiting_for_answer' not in st.session_state:
        st.session_state.waiting_for_answer = False


def check_ollama_connection(ollama_url: str) -> tuple[bool, Optional[OllamaClient], list]:
    """Check Ollama connection and get available models"""
    try:
        client = OllamaClient(ollama_url)
        if client.is_available():
            models = client.list_models()
            return True, client, models
        else:
            return False, None, []
    except Exception as e:
        st.error(f"Failed to connect to Ollama: {e}")
        return False, None, []


def display_interview_progress():
    """Display current interview progress"""
    if st.session_state.interview_crew:
        difficulty = st.session_state.interview_crew.difficulty_level
        max_difficulty = st.session_state.interview_crew.max_difficulty
        
        st.sidebar.subheader("📊 Interview Progress")
        st.sidebar.write(f"**Topic:** {st.session_state.selected_topic}")
        st.sidebar.write(f"**Difficulty Level:** {difficulty}/{max_difficulty}")
        
        # Progress bar
        progress = difficulty / max_difficulty
        st.sidebar.progress(progress)
        
        # Question count
        qa_count = len(st.session_state.qa_history)
        st.sidebar.write(f"**Questions Asked:** {qa_count}")


def display_qa_history():
    """Display Q&A history"""
    if st.session_state.qa_history:
        st.subheader("📚 Interview History")
        
        for i, qa in enumerate(st.session_state.qa_history, 1):
            with st.expander(f"Question {i} (Level {qa['difficulty']})"):
                st.write("**Question:**")
                st.write(qa['question'])
                st.write("**Your Answer:**")
                st.write(qa['answer'])
                
                if 'feedback' in qa:
                    feedback = qa['feedback']
                    st.write("**Feedback:**")
                    
                    # Score with color coding
                    score = feedback['score']
                    if score >= 8:
                        st.success(f"Score: {score}/10 - Excellent!")
                    elif score >= 6:
                        st.warning(f"Score: {score}/10 - Good")
                    else:
                        st.error(f"Score: {score}/10 - Needs Improvement")
                    
                    if feedback['correct']:
                        st.write("✅ **What was correct:**", feedback['correct'])
                    if feedback['improve']:
                        st.write("🔄 **What needs improvement:**", feedback['improve'])
                    if feedback['suggestion']:
                        st.write("💡 **Suggestion:**", feedback['suggestion'])


def main():
    st.set_page_config(
        page_title="AI Interview Assistant",
        page_icon="🎯",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("🎯 AI Interview Assistant")
    st.markdown("*Powered by CrewAI and Ollama*")
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Ollama connection settings
    ollama_url = st.sidebar.text_input(
        "Ollama URL",
        value="http://localhost:11434",
        help="URL of your local Ollama instance"
    )
    
    # Check connection button
    if st.sidebar.button("🔗 Connect to Ollama"):
        with st.sidebar.spinner("Connecting to Ollama..."):
            connected, client, models = check_ollama_connection(ollama_url)
            
            if connected:
                st.session_state.ollama_client = client
                st.sidebar.success("✅ Connected to Ollama!")
                
                if models:
                    st.sidebar.write(f"Available models: {', '.join(models)}")
                else:
                    st.sidebar.warning("No models found. Please pull a model first.")
            else:
                st.sidebar.error("❌ Failed to connect to Ollama")
                st.session_state.ollama_client = None
    
    # Model selection
    if st.session_state.ollama_client:
        try:
            available_models = st.session_state.ollama_client.list_models()
            if available_models:
                selected_model = st.sidebar.selectbox(
                    "Select Model",
                    available_models,
                    key="model_selector"
                )
                st.session_state.selected_model = selected_model
            else:
                st.sidebar.error("No models available. Please pull a model (e.g., 'ollama pull llama2')")
        except Exception as e:
            st.sidebar.error(f"Error fetching models: {e}")
    
    # Topic selection
    if st.session_state.ollama_client and st.session_state.selected_model:
        st.sidebar.subheader("📋 Interview Setup")
        
        # Predefined topics
        predefined_topics = [
            "Python Programming",
            "JavaScript Development",
            "Machine Learning",
            "Data Science",
            "Web Development",
            "System Design",
            "Database Design",
            "DevOps",
            "Cybersecurity",
            "Custom Topic"
        ]
        
        topic_choice = st.sidebar.selectbox("Choose Interview Topic", predefined_topics)
        
        if topic_choice == "Custom Topic":
            custom_topic = st.sidebar.text_input("Enter your custom topic:")
            final_topic = custom_topic if custom_topic else ""
        else:
            final_topic = topic_choice
        
        if final_topic:
            st.session_state.selected_topic = final_topic
            
            # Start interview button
            if not st.session_state.interview_started:
                if st.sidebar.button("🚀 Start Interview"):
                    # Initialize interview crew
                    st.session_state.interview_crew = InterviewCrew(
                        st.session_state.ollama_client,
                        st.session_state.selected_model
                    )
                    st.session_state.interview_crew.set_topic(final_topic)
                    st.session_state.interview_started = True
                    st.session_state.qa_history = []
                    st.rerun()
            else:
                if st.sidebar.button("🔄 Reset Interview"):
                    st.session_state.interview_started = False
                    st.session_state.current_question = ""
                    st.session_state.qa_history = []
                    st.session_state.waiting_for_answer = False
                    st.session_state.interview_crew = None
                    st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not st.session_state.ollama_client:
            st.info("👆 Please connect to Ollama in the sidebar to get started.")
            
            st.subheader("📖 Getting Started")
            st.markdown("""
            1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
            2. **Pull a model**: Run `ollama pull llama2` (or your preferred model)
            3. **Start Ollama**: Run `ollama serve` (usually starts automatically)
            4. **Connect**: Click "Connect to Ollama" in the sidebar
            5. **Select model and topic**: Choose your interview parameters
            6. **Start interviewing**: Begin your AI-powered interview session!
            """)
            
            st.subheader("🎯 Features")
            st.markdown("""
            - **Progressive Difficulty**: Questions start easy and get harder based on your performance
            - **Real-time Feedback**: Get immediate evaluation and suggestions
            - **Multiple Topics**: Choose from programming, ML, system design, and more
            - **Conversation History**: Track your progress throughout the interview
            - **Local AI**: Uses your local Ollama installation for privacy
            """)
        
        elif not st.session_state.selected_model:
            st.info("👆 Please select a model in the sidebar.")
        
        elif not st.session_state.selected_topic:
            st.info("👆 Please choose an interview topic in the sidebar.")
        
        elif st.session_state.interview_started:
            st.subheader(f"🎯 Interview: {st.session_state.selected_topic}")
            
            # Generate first question or continue interview
            if not st.session_state.current_question and not st.session_state.waiting_for_answer:
                with st.spinner("Generating your next question..."):
                    try:
                        question = st.session_state.interview_crew.run_question_generation()
                        st.session_state.current_question = question
                        st.session_state.waiting_for_answer = True
                    except Exception as e:
                        st.error(f"Error generating question: {e}")
            
            # Display current question
            if st.session_state.current_question:
                st.write("**Question:**")
                st.info(st.session_state.current_question)
                
                # Answer input
                if st.session_state.waiting_for_answer:
                    user_answer = st.text_area(
                        "Your Answer:",
                        height=150,
                        placeholder="Type your answer here..."
                    )
                    
                    if st.button("📝 Submit Answer"):
                        if user_answer.strip():
                            with st.spinner("Evaluating your answer..."):
                                try:
                                    # Evaluate the answer
                                    feedback = st.session_state.interview_crew.run_answer_evaluation(
                                        st.session_state.current_question,
                                        user_answer
                                    )
                                    
                                    # Add to history
                                    qa_entry = {
                                        'question': st.session_state.current_question,
                                        'answer': user_answer,
                                        'feedback': feedback,
                                        'difficulty': st.session_state.interview_crew.difficulty_level
                                    }
                                    st.session_state.qa_history.append(qa_entry)
                                    
                                    # Add to crew history
                                    st.session_state.interview_crew.add_to_history(
                                        st.session_state.current_question,
                                        user_answer
                                    )
                                    
                                    # Show feedback
                                    st.subheader("📋 Feedback")
                                    
                                    score = feedback['score']
                                    if score >= 8:
                                        st.success(f"Score: {score}/10 - Excellent work!")
                                    elif score >= 6:
                                        st.warning(f"Score: {score}/10 - Good answer, with room for improvement")
                                    else:
                                        st.error(f"Score: {score}/10 - Let's work on this together")
                                    
                                    if feedback['correct']:
                                        st.write("✅ **What you got right:**")
                                        st.write(feedback['correct'])
                                    
                                    if feedback['improve']:
                                        st.write("🔄 **Areas for improvement:**")
                                        st.write(feedback['improve'])
                                    
                                    if feedback['suggestion']:
                                        st.write("💡 **Suggestion for better answer:**")
                                        st.write(feedback['suggestion'])
                                    
                                    # Increase difficulty if recommended
                                    if feedback['increase_difficulty']:
                                        st.session_state.interview_crew.increase_difficulty()
                                        st.success("🎉 Great job! Moving to the next difficulty level.")
                                    
                                    # Reset for next question
                                    st.session_state.current_question = ""
                                    st.session_state.waiting_for_answer = False
                                    
                                    # Auto-continue button
                                    st.write("---")
                                    if st.button("➡️ Continue to Next Question"):
                                        st.rerun()
                                        
                                except Exception as e:
                                    st.error(f"Error evaluating answer: {e}")
                        else:
                            st.warning("Please provide an answer before submitting.")
    
    with col2:
        display_interview_progress()
    
    # Q&A History at the bottom
    if st.session_state.qa_history:
        st.write("---")
        display_qa_history()


if __name__ == "__main__":
    main()