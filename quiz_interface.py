import streamlit as st
import requests
import json
import random

def parse_question(question_text):
    """Parse a single question text into its components."""
    lines = question_text.split('\n')
    question = next(line.replace('Question:', '').strip() for line in lines if 'Question:' in line)
    choices = [line.strip() for line in lines if line.strip().startswith(('A)', 'B)', 'C)', 'D)'))]
    correct_answer = next(line.replace('Correct Answer:', '').strip() for line in lines if 'Correct Answer:' in line)
    return {
        'question': question,
        'choices': choices,
        'correct_answer': correct_answer
    }

def main():
    st.title("Quiz Generator App")
    
    # Initialize session state
    if 'questions' not in st.session_state:
        st.session_state.questions = []
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.completed = False
        st.session_state.answered_questions = set()

    # File uploader
    if not st.session_state.questions:
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        
        if uploaded_file:
            # Send PDF to FastAPI backend
            files = {"file": uploaded_file}
            response = requests.post("http://localhost:8000/upload/", files=files)
            
            if response.status_code == 200:
                quiz_data = response.json()
                st.session_state.questions = [parse_question(q) for q in quiz_data["quiz_questions"]]
                st.rerun()

    # Display quiz
    if st.session_state.questions and not st.session_state.completed:
        current_q = st.session_state.questions[st.session_state.current_question]
        
        # Display progress
        progress = st.session_state.current_question / len(st.session_state.questions)
        st.progress(progress)
        st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")
        
        # Display question
        st.write("### Question:")
        st.write(current_q['question'])
        
        # Display choices as radio buttons
        user_answer = st.radio("Choose your answer:", current_q['choices'], key=f"q_{st.session_state.current_question}")
        
        if st.button("Submit Answer"):
            selected_letter = user_answer.split(")")[0]
            if selected_letter == current_q['correct_answer']:
                st.success("Correct! 🎉")
                st.session_state.score += 1
            else:
                st.error(f"Wrong answer. The correct answer was {current_q['correct_answer']}")
            
            st.session_state.answered_questions.add(st.session_state.current_question)
            
            # Move to next question
            if st.session_state.current_question < len(st.session_state.questions) - 1:
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.session_state.completed = True
                st.rerun()
    
    # Show final score
    if st.session_state.completed:
        score_percentage = (st.session_state.score / len(st.session_state.questions)) * 100
        st.write("### Quiz Completed!")
        st.write(f"Your final score: {st.session_state.score}/{len(st.session_state.questions)} ({score_percentage:.1f}%)")
        
        # Show final score
    if st.session_state.completed:
        score_percentage = (st.session_state.score / len(st.session_state.questions)) * 100
        
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("# 🎯 Quiz Results")
            st.markdown("---")
            
            # Display score with custom styling
            st.markdown(f"""
            ### Score Details:
            - **Total Questions:** {len(st.session_state.questions)}
            - **Correct Answers:** {st.session_state.score}
            - **Success Rate:** {score_percentage:.1f}%
            """)
            
            # Add performance message based on score
            if score_percentage >= 80:
                st.success("🌟 Excellent performance! Outstanding work!")
            elif score_percentage >= 60:
                st.info("👍 Good job! Keep practicing!")
            else:
                st.warning("📚 Keep learning! You can do better!")
        
        with col2:
            # Add a circular progress indicator
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <h1 style="color: {'green' if score_percentage >= 60 else 'orange'};">
                        {score_percentage:.1f}%
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Add restart button with better styling
        if st.button("📝 Start New Quiz", use_container_width=True):
            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.completed = False
            st.session_state.answered_questions = set()
            st.rerun()

if __name__ == "__main__":
    main()