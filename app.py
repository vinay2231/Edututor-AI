import streamlit as st
import os
from utils.ai_assessment import AIAssessmentEngine
from utils.data_processing import DataProcessor
from utils.visualization import create_progress_chart
from data.student_data import get_student_data, get_all_students
from data.sample_assessments import get_available_assessments

# Set page configuration
st.set_page_config(
    page_title="EduTutor AI - Personalized Learning & Assessment",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for enhanced visual design
st.markdown("""
<style>
    /* Main container styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #4B8BF4;
        margin-bottom: 1rem;
    }
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 2px solid #F0F2F6;
    }
    h2 {
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    h3 {
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* Card style elements */
    .info-card, .stExpander {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4B8BF4;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    /* Metrics */
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    /* Category-specific cards */
    .math-card {
        border-left: 4px solid #4285F4;
    }
    .science-card {
        border-left: 4px solid #34A853;
    }
    .language-card {
        border-left: 4px solid #FBBC05;
    }
    .history-card {
        border-left: 4px solid #EA4335;
    }
    
    /* Sidebar styling */
    .css-1oe6o3n.e1fqkh3o10, .css-1oe6o3n {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        opacity: 0.85;
        transform: translateY(-1px);
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: #4B8BF4;
    }
    
    /* Table styling */
    .dataframe {
        border: none;
    }
    .dataframe tbody tr:nth-child(odd) {
        background-color: #f8f9fa;
    }
    .dataframe tbody tr:hover {
        background-color: #eaecef;
    }
    
    /* Info, success, warning boxes */
    .info-box {
        background-color: #e8f0fe;
        border-left: 4px solid #4B8BF4;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .success-box {
        background-color: #e6f4ea;
        border-left: 4px solid #34A853;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .warning-box {
        background-color: #fef7e0;
        border-left: 4px solid #FBBC05;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Dashboard animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fadein {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* Hover effects for clickable elements */
    .stExpander:hover, .stButton button:hover {
        cursor: pointer;
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sidebar for navigation with enhanced visuals
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <div style='background-color: #4B8BF4; display: inline-block; padding: 1rem; border-radius: 50%; margin-bottom: 0.5rem;'>
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
    </div>
    <h1 style='font-size: 1.8rem; margin-bottom: 0.2rem; color: #4B8BF4;'>EduTutor AI</h1>
    <p style='color: #666; font-size: 0.9rem; margin: 0;'>Personalized Learning & Assessment</p>
</div>
""", unsafe_allow_html=True)

# Login functionality with improved UI
if not st.session_state.authenticated:
    st.sidebar.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.2rem; border-radius: 0.5rem; margin: 1rem 0; 
         border-left: 4px solid #4B8BF4; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
        <h2 style='font-size: 1.3rem; margin-bottom: 1rem; color: #4B8BF4;'>Login</h2>
    </div>
    """, unsafe_allow_html=True)
    
    user_type = st.sidebar.selectbox("Select User Type", ["Student", "Teacher"])
    
    if user_type == "Student":
        students = get_all_students()
        student_ids = [s['id'] for s in students]
        student_names = [f"{s['first_name']} {s['last_name']}" for s in students]
        
        st.sidebar.markdown("""<p style='margin-bottom: 0.3rem; color: #666;'>Select your name:</p>""", unsafe_allow_html=True)
        selected_student = st.sidebar.selectbox("", student_names, label_visibility="collapsed")
        selected_index = student_names.index(selected_student)
        
        st.sidebar.markdown("""<p style='margin: 0.8rem 0 0.3rem 0; color: #666;'>Enter your password:</p>""", unsafe_allow_html=True)
        password = st.sidebar.text_input("", type="password", label_visibility="collapsed", 
                                       placeholder="Use 'password' for demo")
        
        # Login button with better styling
        login_btn = st.sidebar.button("Login", use_container_width=True)
        
        if login_btn:
            if password == "password":  # In a real app, use proper authentication
                st.session_state.user_type = "student"
                st.session_state.current_user = student_ids[selected_index]
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
                
    else:  # Teacher login
        st.sidebar.markdown("""<p style='margin-bottom: 0.3rem; color: #666;'>Teacher ID:</p>""", unsafe_allow_html=True)
        teacher_id = st.sidebar.text_input("", label_visibility="collapsed", placeholder="Enter your teacher ID")
        
        st.sidebar.markdown("""<p style='margin: 0.8rem 0 0.3rem 0; color: #666;'>Enter your password:</p>""", unsafe_allow_html=True)
        password = st.sidebar.text_input(" ", type="password", label_visibility="collapsed", 
                                       placeholder="Use 'teacher' for demo")
        
        # Login button with better styling
        login_btn = st.sidebar.button("Login", use_container_width=True)
        
        if login_btn:
            if password == "teacher":  # In a real app, use proper authentication
                st.session_state.user_type = "teacher"
                st.session_state.current_user = teacher_id
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
                
    # Add demo instructions
    st.sidebar.markdown("""
    <div style='background-color: #e8f0fe; padding: 1rem; border-radius: 0.5rem; margin-top: 1.5rem; 
         border-left: 4px solid #4B8BF4; font-size: 0.9rem;'>
        <p style='margin: 0 0 0.5rem 0; font-weight: 600; color: #4B8BF4;'>Demo Credentials:</p>
        <p style='margin: 0 0 0.3rem 0;'><b>Student:</b> Any name from the list</p>
        <p style='margin: 0 0 0.3rem 0;'><b>Password:</b> password</p>
        <hr style='margin: 0.5rem 0; border-color: #c6d9f7;'>
        <p style='margin: 0 0 0.3rem 0;'><b>Teacher ID:</b> Any ID (e.g., T1001)</p>
        <p style='margin: 0;'><b>Password:</b> teacher</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display user info with enhanced styling
    if st.session_state.user_type == "student":
        student_data = get_student_data(st.session_state.current_user)
        if student_data:
            st.sidebar.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; 
                 margin-bottom: 1rem; border-left: 4px solid #4B8BF4; text-align: center;'>
                <div style='font-size: 0.85rem; color: #666; margin-bottom: 0.2rem;'>STUDENT</div>
                <div style='font-size: 1.2rem; font-weight: 600; color: #4B8BF4;'>
                    {student_data['first_name']} {student_data['last_name']}
                </div>
                <div style='font-size: 0.85rem; color: #666; margin-top: 0.2rem;'>ID: {student_data['id']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Teacher display
        teacher_id = st.session_state.current_user if st.session_state.current_user else "T1001"
        st.sidebar.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; 
             margin-bottom: 1rem; border-left: 4px solid #4B8BF4; text-align: center;'>
            <div style='font-size: 0.85rem; color: #666; margin-bottom: 0.2rem;'>TEACHER</div>
            <div style='font-size: 1.2rem; font-weight: 600; color: #4B8BF4;'>
                Teacher Profile
            </div>
            <div style='font-size: 0.85rem; color: #666; margin-top: 0.2rem;'>ID: {teacher_id}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation links section with a more modern look
    st.sidebar.markdown("""
    <div style='background-color: #f8f9fa; padding: 0.8rem; border-radius: 0.5rem; 
         margin-bottom: 1rem; border-left: 4px solid #4B8BF4;'>
        <h2 style='font-size: 1.2rem; margin-bottom: 0.8rem; color: #4B8BF4;'>Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button with improved styling
    if st.sidebar.button("Logout", type="primary", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
    if st.session_state.user_type == "student":
        # Check if there's a current assessment in progress
        if st.session_state.get('page') == "assessment":
            page = "assessment"
            # Add a back button to return to the assessments list
            if st.sidebar.button("← Back to Assessments", use_container_width=True):
                st.session_state.page = None
                st.rerun()
        elif st.session_state.get('page') == "essay_assessment":
            page = "essay_assessment"
            # Add a back button
            if st.sidebar.button("← Back to Dashboard", use_container_width=True):
                st.session_state.page = None
                st.rerun()
        else:
            page = st.sidebar.radio(
                "Go to:",
                ["Dashboard", "Available Assessments", "Learning Path", "My Progress", "AI Essay Grading"]
            )
        
        if page == "Dashboard":
            # Student Dashboard
            # Welcome section with hero banner
            if student_data:
                st.markdown(f"""
                <div style="background-color: #4B8BF4; padding: 2rem; border-radius: 0.8rem; margin-bottom: 2rem; 
                    background-image: linear-gradient(135deg, #4B8BF4, #3267d6); color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h1 style="margin: 0; color: white; font-size: 2.2rem;">Welcome, {student_data['first_name']}!</h1>
                    <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 1.5rem 0; font-size: 1.1rem;">
                        Your personalized learning journey continues
                    </p>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <div style="background: rgba(255,255,255,0.2); padding: 0.7rem 1rem; border-radius: 0.5rem; backdrop-filter: blur(5px);">
                            <div style="font-size: 0.85rem; opacity: 0.8;">Overall Average</div>
                            <div style="font-size: 1.5rem; font-weight: 600;">
                                {sum([
                                    student_data['performance']['math'], 
                                    student_data['performance']['science'],
                                    student_data['performance']['language_arts'],
                                    student_data['performance']['history']
                                ]) / 4:.1f}%
                            </div>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); padding: 0.7rem 1rem; border-radius: 0.5rem; backdrop-filter: blur(5px);">
                            <div style="font-size: 0.85rem; opacity: 0.8;">Completed Assessments</div>
                            <div style="font-size: 1.5rem; font-weight: 600;">{student_data['completed_assessments']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Modern layout with cards
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    # Progress section with improved styling
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">📊</span>
                        Your Progress
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    fig = create_progress_chart(student_data)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Upcoming assessments with card styling
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin: 1.5rem 0 1rem 0;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">📝</span>
                        Upcoming Assessments
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    assessments = get_available_assessments()
                    for i, assessment in enumerate(assessments[:3]):
                        subject_color = "#4285F4" if assessment['subject'] == "Math" else "#34A853" if assessment['subject'] == "Science" else "#FBBC05" if assessment['subject'] == "Language Arts" else "#EA4335"
                        
                        st.markdown(f"""
                        <div style="border-left: 4px solid {subject_color}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;
                            background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <div style="font-weight: 600; font-size: 1.1rem; color: #333;">{assessment['title']}</div>
                                <div style="background-color: {subject_color}; color: white; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 1rem;">
                                    {assessment['subject']}
                                </div>
                            </div>
                            <div style="color: #666; margin-bottom: 0.5rem; font-size: 0.9rem;">Due: {assessment['due_date']}</div>
                            <div style="margin: 0.8rem 0; font-size: 0.9rem;">Type: {assessment['type']} • Est. Time: {assessment['estimated_time']} min</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Start button outside the markdown for functionality
                        st.button(f"Start {assessment['title']}", key=f"start_{assessment['id']}", type="primary", use_container_width=(i==0))
                
                with col2:
                    # Personalized recommendations with visually distinct cards
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">🧠</span>
                        Personalized Recommendations
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Dynamic recommendations based on student performance
                    if student_data['performance']['math'] < 70:
                        st.markdown("""
                        <div style="border-left: 4px solid #4285F4; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;
                            background-color: #e8f0fe; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; color: #4285F4;">📘 Math Practice</div>
                            <div style="color: #333; font-size: 0.95rem;">Based on your recent performance, we recommend focusing on Algebra concepts, specifically equation solving and linear functions.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if student_data['performance']['science'] < 80:
                        st.markdown("""
                        <div style="border-left: 4px solid #34A853; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;
                            background-color: #e6f4ea; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; color: #34A853;">🧪 Science Review</div>
                            <div style="color: #333; font-size: 0.95rem;">Review the cell biology materials to improve your understanding of cellular structures and processes.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if student_data['completed_assessments'] < 5:
                        st.markdown("""
                        <div style="border-left: 4px solid #FBBC05; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;
                            background-color: #fef7e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; color: #FBBC05;">✍️ Complete More Assessments</div>
                            <div style="color: #333; font-size: 0.95rem;">Take more practice quizzes to help us personalize your learning path and improve your mastery of the subjects.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Recent feedback section with modern styling
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin: 1.5rem 0 1rem 0;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">💬</span>
                        Recent Feedback
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("Math Quiz - Functions"):
                        st.markdown("""
                        <div style="border-left: 4px solid #4285F4; padding: 0.8rem; border-radius: 0.5rem;
                            background-color: #f8f9fa; font-size: 0.95rem;">
                            You did well with linear functions but need more practice with quadratic equations. 
                            Review the properties of parabolas and their transformations.
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with st.expander("Science Lab - DNA Extraction"):
                        st.markdown("""
                        <div style="border-left: 4px solid #34A853; padding: 0.8rem; border-radius: 0.5rem;
                            background-color: #f8f9fa; font-size: 0.95rem;">
                            Your understanding of the procedure is excellent. Work on explaining the theoretical 
                            principles behind the steps and the biological significance of the extraction process.
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Quick actions card
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin: 1.5rem 0 1rem 0;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">⚡</span>
                        Quick Actions
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("My Study Plan", use_container_width=True):
                            st.session_state.page = "Learning Path"
                            st.rerun()
                    with col2:
                        if st.button("Practice Now", use_container_width=True):
                            st.session_state.page = "Available Assessments"
                            st.rerun()
        
        elif page == "Available Assessments":
            st.title("Available Assessments")
            
            assessments = get_available_assessments()
            for assessment in assessments:
                with st.expander(f"{assessment['title']} - {assessment['subject']}"):
                    st.write(f"**Due Date:** {assessment['due_date']}")
                    st.write(f"**Description:** {assessment['description']}")
                    st.write(f"**Type:** {assessment['type']}")
                    st.write(f"**Estimated Time:** {assessment['estimated_time']} minutes")
                    if st.button(f"Start Assessment", key=f"start_assessment_{assessment['id']}"):
                        st.session_state.current_assessment = assessment['id']
                        st.session_state.page = "assessment"
                        st.rerun()
        
        elif page == "Learning Path":
            if student_data:
                # Modern header with motivational message
                st.markdown(f"""
                <div style="background-color: #4B8BF4; padding: 2rem; border-radius: 0.8rem; margin-bottom: 2rem; 
                    background-image: linear-gradient(135deg, #4B8BF4, #3267d6); color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h1 style="margin: 0; color: white; font-size: 2.2rem;">Your Learning Journey</h1>
                    <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                        Personalized path to mastery based on your learning style: <b>{student_data['learning_style']}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Split into two columns for better layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Current Level with visual representation
                    subjects = ["Math", "Science", "Language Arts", "History"]
                    current_levels = [student_data['performance']['math'] // 10, 
                                    student_data['performance']['science'] // 10,
                                    student_data['performance']['language_arts'] // 10,
                                    student_data['performance']['history'] // 10]
                    
                    # Subject colors
                    subject_colors = {
                        "Math": "#4285F4",        # Google Blue
                        "Science": "#34A853",     # Google Green
                        "Language Arts": "#FBBC05", # Google Yellow
                        "History": "#EA4335"      # Google Red
                    }
                    
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin-bottom: 1.2rem;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">📚</span>
                        Current Mastery Levels
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Display as cards with better visual representation
                    subject_cards = ""
                    for subject, level in zip(subjects, current_levels):
                        subject_color = subject_colors.get(subject, "#4B8BF4")
                        # Create progress circles
                        progress_html = ""
                        for i in range(10):
                            if i < level:
                                # Filled circle for completed levels
                                progress_html += f'<span style="display: inline-block; width: 15px; height: 15px; border-radius: 50%; background-color: {subject_color}; margin-right: 4px;"></span>'
                            else:
                                # Empty circle for incomplete levels
                                progress_html += f'<span style="display: inline-block; width: 15px; height: 15px; border-radius: 50%; border: 1px solid {subject_color}; margin-right: 4px;"></span>'
                        
                        # Create subject card
                        subject_cards += f"""
                        <div style="background-color: white; border-left: 4px solid {subject_color}; padding: 1rem; 
                            border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-weight: 600; font-size: 1.1rem; color: #333;">{subject}</div>
                                <div style="font-size: 1rem; color: {subject_color}; font-weight: 600;">Level {level}/10</div>
                            </div>
                            <div style="margin-top: 0.8rem;">
                                {progress_html}
                            </div>
                        </div>
                        """
                    
                    st.markdown(subject_cards, unsafe_allow_html=True)
                    
                    # Recommended modules section with enhanced styling
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin: 1.8rem 0 1.2rem 0;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">🧩</span>
                        Recommended Learning Modules
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Math recommendations with modern toggle
                    with st.expander("**Mathematics**", expanded=True):
                        math_level = current_levels[0]
                        
                        # Cards for recommended modules
                        if math_level < 5:
                            modules = [
                                {"title": "Foundational Algebra", "icon": "📊", "description": "Strengthen your understanding of algebraic fundamentals including equations, expressions, and inequalities.", "time": "4-6 weeks", "difficulty": "Beginner"},
                                {"title": "Number Theory Basics", "icon": "🔢", "description": "Learn key properties of numbers, factors, multiples, and prime numbers with practical applications.", "time": "3-4 weeks", "difficulty": "Beginner"}
                            ]
                        elif math_level < 8:
                            modules = [
                                {"title": "Advanced Functions", "icon": "📈", "description": "Master different function types including quadratic, exponential, and logarithmic functions.", "time": "5-7 weeks", "difficulty": "Intermediate"},
                                {"title": "Geometry Essentials", "icon": "📐", "description": "Explore spatial relationships, triangles, circles, and coordinate geometry with proofs.", "time": "4-6 weeks", "difficulty": "Intermediate"}
                            ]
                        else:
                            modules = [
                                {"title": "Calculus Concepts", "icon": "🧮", "description": "Begin exploring calculus principles including limits, derivatives, and basic integration.", "time": "6-8 weeks", "difficulty": "Advanced"},
                                {"title": "Statistical Analysis", "icon": "🔍", "description": "Advanced data interpretation, hypothesis testing, and statistical inference techniques.", "time": "5-7 weeks", "difficulty": "Advanced"}
                            ]
                        
                        # Display modules as modern cards with functional buttons
                        for i, module in enumerate(modules):
                            # Create the card with unique styling
                            st.markdown(f"""
                            <div style="background-color: white; border-left: 4px solid #4285F4; padding: 1rem; 
                                border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <div style="font-weight: 600; font-size: 1.1rem; color: #333;">{module["icon"]} {module["title"]}</div>
                                    <div style="background-color: #e8f0fe; color: #4285F4; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 1rem; font-weight: 500;">
                                        {module["difficulty"]}
                                    </div>
                                </div>
                                <div style="color: #555; margin-bottom: 0.8rem; font-size: 0.95rem;">
                                    {module["description"]}
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="color: #666; font-size: 0.9rem;">
                                        <i>Estimated time: {module["time"]}</i>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add a button that works outside of the markdown for module start
                            if st.button(f"Start {module['title']}", key=f"math_module_{i}", type="primary" if i == 0 else "secondary"):
                                st.session_state.current_module = {
                                    "title": module["title"],
                                    "subject": "Math",
                                    "difficulty": module["difficulty"],
                                    "description": module["description"],
                                    "icon": module["icon"]
                                }
                                st.success(f"Starting {module['title']} module...")
                                
                        # Show module content if a module is selected
                        if st.session_state.get('current_module'):
                            module = st.session_state.current_module
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.8rem; margin: 1.5rem 0; 
                                border-left: 4px solid #4285F4;">
                                <h3 style="margin-top: 0; font-size: 1.4rem; color: #4285F4; display: flex; align-items: center;">
                                    <span style="margin-right: 0.5rem;">{module["icon"]}</span> {module["title"]} Module
                                </h3>
                                <p style="color: #555; margin-bottom: 1rem;">
                                    {module["description"]}
                                </p>
                                <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <h4 style="margin-top: 0; font-size: 1.1rem; color: #333;">Learning Objectives</h4>
                                    <ul style="margin-bottom: 0; padding-left: 1.5rem; color: #555;">
                                        <li>Understand key concepts related to {module["title"].lower()}</li>
                                        <li>Apply mathematical reasoning to solve problems</li>
                                        <li>Develop critical thinking skills through practical examples</li>
                                    </ul>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-top: 1.5rem;">
                                    <div style="background-color: #e8f0fe; color: #4285F4; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.9rem;">
                                        <span style="font-weight: 500;">Difficulty:</span> {module["difficulty"]}
                                    </div>
                                    <div style="background-color: #e8f0fe; color: #4285F4; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.9rem;">
                                        <span style="font-weight: 500;">Subject:</span> {module["subject"]}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Lesson modules with continue buttons
                            lessons = ["Introduction", "Core Concepts", "Practice Problems", "Advanced Applications"]
                            
                            for i, lesson in enumerate(lessons):
                                with st.expander(f"Lesson {i+1}: {lesson}", expanded=(i==0)):
                                    st.markdown(f"""
                                    <div style="padding: 0.5rem 0;">
                                        <p>This is the content for the {lesson.lower()} section of {module['title']}.</p>
                                        <p>In a complete implementation, this would include interactive content, videos, and exercises.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if i < len(lessons) - 1:
                                        if st.button(f"Continue to {lessons[i+1]}", key=f"continue_lesson_{i}"):
                                            # This would open the next lesson in a real implementation
                                            pass
                                    else:
                                        if st.button("Complete Module", key="complete_module", type="primary"):
                                            st.balloons()
                                            st.success("Congratulations! You've completed this module.")
                                            # In a real implementation, this would mark the module as completed
                    
                    # Science recommendations
                    with st.expander("**Science**"):
                        science_level = current_levels[1]
                        
                        # Cards for recommended modules
                        if science_level < 5:
                            modules = [
                                {"title": "Scientific Method", "icon": "🧪", "description": "Master the process of scientific inquiry, hypothesis formation, and experimental design.", "time": "3-5 weeks", "difficulty": "Beginner"},
                                {"title": "Basic Biology", "icon": "🌱", "description": "Introduction to living systems, cell structure, and fundamental biological processes.", "time": "4-6 weeks", "difficulty": "Beginner"}
                            ]
                        elif science_level < 8:
                            modules = [
                                {"title": "Chemistry Fundamentals", "icon": "⚗️", "description": "Study matter, chemical reactions, and the periodic table with practical applications.", "time": "5-7 weeks", "difficulty": "Intermediate"},
                                {"title": "Physics Principles", "icon": "🔋", "description": "Explore forces, energy, and motion through Newton's laws and energy conservation.", "time": "5-7 weeks", "difficulty": "Intermediate"}
                            ]
                        else:
                            modules = [
                                {"title": "Molecular Biology", "icon": "🧬", "description": "Advanced cellular concepts, DNA, and genetic expression with laboratory techniques.", "time": "6-8 weeks", "difficulty": "Advanced"},
                                {"title": "Astrophysics Introduction", "icon": "🌌", "description": "Understanding the cosmos, stellar evolution, and fundamental forces of the universe.", "time": "6-8 weeks", "difficulty": "Advanced"}
                            ]
                        
                        # Display modules as modern cards with functional buttons
                        for i, module in enumerate(modules):
                            # Create the card with unique styling
                            st.markdown(f"""
                            <div style="background-color: white; border-left: 4px solid #34A853; padding: 1rem; 
                                border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <div style="font-weight: 600; font-size: 1.1rem; color: #333;">{module["icon"]} {module["title"]}</div>
                                    <div style="background-color: #e6f4ea; color: #34A853; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 1rem; font-weight: 500;">
                                        {module["difficulty"]}
                                    </div>
                                </div>
                                <div style="color: #555; margin-bottom: 0.8rem; font-size: 0.95rem;">
                                    {module["description"]}
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="color: #666; font-size: 0.9rem;">
                                        <i>Estimated time: {module["time"]}</i>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add a button that works outside of the markdown for module start
                            if st.button(f"Start {module['title']}", key=f"science_module_{i}", type="primary" if i == 0 else "secondary"):
                                st.session_state.current_science_module = {
                                    "title": module["title"],
                                    "subject": "Science",
                                    "difficulty": module["difficulty"],
                                    "description": module["description"],
                                    "icon": module["icon"]
                                }
                                st.success(f"Starting {module['title']} module...")
                                
                        # Show module content if a module is selected
                        if st.session_state.get('current_science_module'):
                            module = st.session_state.current_science_module
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.8rem; margin: 1.5rem 0; 
                                border-left: 4px solid #34A853;">
                                <h3 style="margin-top: 0; font-size: 1.4rem; color: #34A853; display: flex; align-items: center;">
                                    <span style="margin-right: 0.5rem;">{module["icon"]}</span> {module["title"]} Module
                                </h3>
                                <p style="color: #555; margin-bottom: 1rem;">
                                    {module["description"]}
                                </p>
                                <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <h4 style="margin-top: 0; font-size: 1.1rem; color: #333;">Learning Objectives</h4>
                                    <ul style="margin-bottom: 0; padding-left: 1.5rem; color: #555;">
                                        <li>Understand key principles of {module["title"].lower()}</li>
                                        <li>Apply scientific methodology to investigate concepts</li>
                                        <li>Develop analytical skills through experiments and observation</li>
                                    </ul>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-top: 1.5rem;">
                                    <div style="background-color: #e6f4ea; color: #34A853; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.9rem;">
                                        <span style="font-weight: 500;">Difficulty:</span> {module["difficulty"]}
                                    </div>
                                    <div style="background-color: #e6f4ea; color: #34A853; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.9rem;">
                                        <span style="font-weight: 500;">Subject:</span> {module["subject"]}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Science module components with interactive elements
                            components = ["Theoretical Concepts", "Lab Experiments", "Data Analysis", "Real-World Applications"]
                            
                            for i, component in enumerate(components):
                                with st.expander(f"Component {i+1}: {component}", expanded=(i==0)):
                                    st.markdown(f"""
                                    <div style="padding: 0.5rem 0;">
                                        <p>This is the content for the {component.lower()} component of {module['title']}.</p>
                                        <p>In a complete implementation, this would include interactive simulations, video demonstrations, and laboratory guides.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if component == "Lab Experiments":
                                        st.info("Virtual lab simulations would be available here in the full implementation.")
                                    
                                    if i < len(components) - 1:
                                        if st.button(f"Continue to {components[i+1]}", key=f"continue_component_{i}"):
                                            # This would open the next component in a real implementation
                                            pass
                                    else:
                                        if st.button("Complete Science Module", key="complete_science_module", type="primary"):
                                            st.balloons()
                                            st.success("Congratulations! You've completed this science module.")
                                            # In a real implementation, this would mark the module as completed
                
                with col2:
                    # Learning style adaptation section
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">🧠</span>
                        Your Learning Style
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Learning style card
                    learning_style = student_data['learning_style']
                    learning_style_icon = "👁️" if learning_style == "Visual" else "👂" if learning_style == "Auditory" else "✍️" if learning_style == "Reading/Writing" else "🤸"
                    learning_style_color = "#4B8BF4" if learning_style == "Visual" else "#34A853" if learning_style == "Auditory" else "#FBBC05" if learning_style == "Reading/Writing" else "#EA4335"
                    
                    learning_style_description = ""
                    learning_style_tips = []
                    
                    if learning_style == "Visual":
                        learning_style_description = "You learn best through visual aids like charts, graphs, and images."
                        learning_style_tips = [
                            "Use color-coding in your notes",
                            "Create mind maps for complex topics",
                            "Watch video tutorials when available",
                            "Transform text into diagrams"
                        ]
                    elif learning_style == "Auditory":
                        learning_style_description = "You learn best through listening, discussions, and verbal explanations."
                        learning_style_tips = [
                            "Record lessons to listen again later",
                            "Participate actively in study discussions",
                            "Explain concepts out loud to yourself",
                            "Use rhythm or music for memorization"
                        ]
                    elif learning_style == "Reading/Writing":
                        learning_style_description = "You learn best through text-based materials and writing."
                        learning_style_tips = [
                            "Take detailed notes in your own words",
                            "Rewrite key concepts multiple times",
                            "Create written summaries of lessons",
                            "Use flashcards for key terms"
                        ]
                    else:  # Kinesthetic
                        learning_style_description = "You learn best through hands-on activities and physical experiences."
                        learning_style_tips = [
                            "Use physical movement while studying",
                            "Create models or demonstrations",
                            "Take frequent, active breaks",
                            "Apply concepts to real-world scenarios"
                        ]
                    
                    st.markdown(f"""
                    <div style="background-color: white; border-left: 4px solid {learning_style_color}; padding: 1.2rem; 
                        border-radius: 0.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                            <div style="background-color: {learning_style_color}; color: white; height: 40px; width: 40px; 
                                border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                margin-right: 0.8rem; font-size: 1.5rem;">{learning_style_icon}</div>
                            <div>
                                <div style="font-weight: 600; font-size: 1.2rem; color: #333;">{learning_style} Learner</div>
                                <div style="color: #666; font-size: 0.9rem;">Your primary learning style</div>
                            </div>
                        </div>
                        <div style="color: #555; margin-bottom: 1rem; font-size: 0.95rem; padding-left: 0.2rem;">
                            {learning_style_description}
                        </div>
                        <div style="background-color: #f8f9fa; padding: 0.8rem; border-radius: 0.4rem;">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; color: #333;">Study Tips for Your Style:</div>
                            <ul style="margin: 0; padding-left: 1.5rem; color: #555;">
                    """, unsafe_allow_html=True)
                    
                    # Add tips as list items
                    for tip in learning_style_tips:
                        st.markdown(f'<li style="margin-bottom: 0.3rem;">{tip}</li>', unsafe_allow_html=True)
                    
                    st.markdown("""
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Weekly focus section
                    st.markdown("""
                    <h2 style="display: flex; align-items: center; margin: 1.5rem 0 1rem 0;">
                        <span style="background-color: #4B8BF4; color: white; height: 32px; width: 32px; 
                            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; 
                            margin-right: 0.5rem; font-size: 1rem;">📅</span>
                        Weekly Focus Plan
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Generate a weekly plan based on student performance
                    weak_areas = []
                    if student_data['performance']['math'] < 70:
                        weak_areas.append(("Mathematics", "#4285F4"))
                    if student_data['performance']['science'] < 70:
                        weak_areas.append(("Science", "#34A853"))
                    if student_data['performance']['language_arts'] < 70:
                        weak_areas.append(("Language Arts", "#FBBC05"))
                    if student_data['performance']['history'] < 70:
                        weak_areas.append(("History", "#EA4335"))
                    
                    if weak_areas:
                        # Focus areas this week
                        st.markdown("""
                        <div style="background-color: white; padding: 1.2rem; border-radius: 0.5rem; 
                            margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="font-weight: 600; margin-bottom: 0.8rem; color: #333; font-size: 1.05rem;">
                                Focus areas this week:
                            </div>
                        """, unsafe_allow_html=True)
                        
                        for area, color in weak_areas:
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; 
                                margin-bottom: 0.8rem; border-left: 3px solid {color}; padding-left: 0.8rem;">
                                <div style="color: #333; font-weight: 500;">{area}</div>
                                <div style="color: #666;">3 hours recommended</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download study plan button
                        if st.button("Download Study Plan", type="primary", use_container_width=True):
                            st.success("Study plan downloaded successfully!")
                            # In a complete implementation, this would trigger a file download
                    else:
                        # For high-performing students
                        st.markdown("""
                        <div style="background-color: #e6f4ea; border-left: 4px solid #34A853; padding: 1rem; 
                            border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; color: #34A853;">
                                🎉 Congratulations!
                            </div>
                            <div style="color: #333; margin-bottom: 0.8rem; font-size: 0.95rem;">
                                You're performing well across all subjects. Here's our recommended focus:
                            </div>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem; color: #555;">
                                <li style="margin-bottom: 0.3rem;">Advanced project work: 4 hours</li>
                                <li style="margin-bottom: 0.3rem;">Peer tutoring: 2 hours</li>
                                <li style="margin-bottom: 0.3rem;">Exploration of new topics: 3 hours</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add a challenge button with functionality
                        if st.button("View Advanced Challenges", type="primary", use_container_width=True):
                            st.session_state.show_advanced_challenges = True
                            
                        # Display advanced challenges if button was clicked
                        if st.session_state.get('show_advanced_challenges', False):
                            st.markdown("""
                            <h3 style="margin-top: 1.5rem; font-size: 1.4rem; color: #4B8BF4;">Advanced Challenges</h3>
                            """, unsafe_allow_html=True)
                            
                            challenges = [
                                {"title": "Research Project", "subject": "Science", "difficulty": "Advanced", "description": "Conduct an in-depth analysis of renewable energy technologies and their environmental impact."},
                                {"title": "Mathematical Modeling", "subject": "Math", "difficulty": "Advanced", "description": "Create mathematical models to predict population growth patterns under various constraints."},
                                {"title": "Literary Analysis", "subject": "Language Arts", "difficulty": "Advanced", "description": "Compare and contrast narrative techniques in classic and contemporary literature."}
                            ]
                            
                            for i, challenge in enumerate(challenges):
                                subject_color = "#4285F4" if challenge["subject"] == "Math" else "#34A853" if challenge["subject"] == "Science" else "#FBBC05"
                                
                                st.markdown(f"""
                                <div style="background-color: white; border-left: 4px solid {subject_color}; padding: 1rem; 
                                    border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                        <div style="font-weight: 600; font-size: 1.1rem; color: #333;">{challenge["title"]}</div>
                                        <div style="background-color: {subject_color}; color: white; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 1rem;">
                                            {challenge["subject"]}
                                        </div>
                                    </div>
                                    <div style="color: #555; margin-bottom: 0.8rem; font-size: 0.95rem;">
                                        {challenge["description"]}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Accept challenge button
                                st.button(f"Accept Challenge", key=f"accept_challenge_{i}", type="primary" if i == 0 else "secondary")
        
        elif page == "assessment":
            # Import and display assessment page
            from pages.assessment import app as assessment_app
            assessment_app()
            
        elif page == "AI Essay Grading":
            # Set the page in session state for navigation
            st.session_state.page = "essay_assessment"
            # Import and display the AI-powered essay assessment page
            from pages.essay_assessment import app as essay_assessment_app
            essay_assessment_app()
            
        elif page == "essay_assessment":
            # Import and display the AI-powered essay assessment page
            from pages.essay_assessment import app as essay_assessment_app
            essay_assessment_app()
            
        elif page == "My Progress":
            st.title("My Academic Progress")
            
            # Overall performance chart
            st.subheader("Performance Overview")
            data_processor = DataProcessor()
            performance_data = {
                'Subject': ['Math', 'Science', 'Language Arts', 'History'],
                'Score': [
                    student_data['performance']['math'],
                    student_data['performance']['science'],
                    student_data['performance']['language_arts'],
                    student_data['performance']['history']
                ]
            }
            fig = data_processor.create_subject_performance_chart(performance_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Progress over time (mock data for demonstration)
            st.subheader("Progress Over Time")
            progress_data = {
                'Month': ['January', 'February', 'March', 'April', 'May'],
                'Math': [65, 68, 72, 75, student_data['performance']['math']],
                'Science': [70, 72, 75, 78, student_data['performance']['science']],
                'Language Arts': [80, 82, 80, 83, student_data['performance']['language_arts']],
                'History': [75, 77, 80, 78, student_data['performance']['history']]
            }
            fig = data_processor.create_progress_over_time_chart(progress_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Assessment history
            st.subheader("Recent Assessment Results")
            
            assessment_history = [
                {"name": "Math Quiz - Algebra", "score": 85, "date": "2023-05-10", "feedback": "Strong algebraic manipulation skills. Work on word problems."},
                {"name": "Science Lab - Chemistry", "score": 78, "date": "2023-05-05", "feedback": "Good understanding of chemical reactions. Review balancing equations."},
                {"name": "Language Arts - Essay", "score": 90, "date": "2023-04-28", "feedback": "Excellent thesis and supporting arguments. Focus on transition sentences."},
                {"name": "History - Civil War Test", "score": 82, "date": "2023-04-20", "feedback": "Strong on key events and figures. Add more detail on economic factors."}
            ]
            
            for assessment in assessment_history:
                with st.expander(f"{assessment['name']} - Score: {assessment['score']}%"):
                    st.write(f"**Date:** {assessment['date']}")
                    st.write(f"**AI Feedback:** {assessment['feedback']}")
                    
                    # Show strength and improvement areas with color coding
                    if assessment['score'] >= 85:
                        st.success("**Strength:** Excellent understanding of core concepts")
                    elif assessment['score'] >= 75:
                        st.info("**Strength:** Good grasp of fundamentals")
                    else:
                        st.warning("**Area for improvement:** Core concept review recommended")
    
    else:  # Teacher view
        page = st.sidebar.radio(
            "Go to:",
            ["Class Overview", "Student Performance", "Assessment Management"]
        )
        
        if page == "Class Overview":
            st.title("Class Overview Dashboard")
            
            # Display class statistics
            st.subheader("Class Performance Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Mock class statistics for demo purposes
            with col1:
                st.metric("Class Average", "78%", "+2%")
            with col2:
                st.metric("Assessments Completed", "42", "+5")
            with col3:
                st.metric("Active Students", "28", "-1")
            with col4:
                st.metric("At-Risk Students", "5", "-2")
            
            # Subject performance
            st.subheader("Performance by Subject")
            data_processor = DataProcessor()
            class_performance = {
                'Subject': ['Math', 'Science', 'Language Arts', 'History'],
                'Average Score': [75, 80, 82, 77]
            }
            fig = data_processor.create_subject_performance_chart(class_performance)
            st.plotly_chart(fig, use_container_width=True)
            
            # Student list with quick stats
            st.subheader("Student Overview")
            
            students = get_all_students()
            
            # Create expandable sections for each student with basic info
            for student in students:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{student['first_name']} {student['last_name']}**")
                with col2:
                    avg_score = sum([
                        student['performance']['math'], 
                        student['performance']['science'],
                        student['performance']['language_arts'],
                        student['performance']['history']
                    ]) / 4
                    st.write(f"Avg: {avg_score:.1f}%")
                with col3:
                    st.write(f"Complete: {student['completed_assessments']}")
                with col4:
                    if avg_score < 70:
                        st.write("⚠️ At Risk")
                    elif avg_score > 90:
                        st.write("⭐ Excellent")
                    else:
                        st.write("✓ On Track")
                
                st.write("---")
        
        elif page == "Student Performance":
            st.title("Student Performance Analytics")
            
            # Student selector
            students = get_all_students()
            student_names = [f"{s['first_name']} {s['last_name']}" for s in students]
            selected_student = st.selectbox("Select Student", student_names)
            selected_index = student_names.index(selected_student)
            student = students[selected_index]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader(f"{student['first_name']} {student['last_name']}")
                st.write(f"**ID:** {student['id']}")
                st.write(f"**Grade Level:** {student['grade_level']}")
                st.write(f"**Completed Assessments:** {student['completed_assessments']}")
                
                # Learning style and preferences
                st.subheader("Learning Profile")
                st.write(f"**Primary Learning Style:** {student['learning_style']}")
                st.write("**Subject Engagement:**")
                for subject, level in student['engagement'].items():
                    st.write(f"- {subject.capitalize()}: {level}/10")
            
            with col2:
                # Performance chart
                st.subheader("Subject Performance")
                performance_data = {
                    'Subject': ['Math', 'Science', 'Language Arts', 'History'],
                    'Score': [
                        student['performance']['math'],
                        student['performance']['science'],
                        student['performance']['language_arts'],
                        student['performance']['history']
                    ]
                }
                data_processor = DataProcessor()
                fig = data_processor.create_subject_performance_chart(performance_data)
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed assessment history
            st.subheader("Recent Assessment History")
            
            # Mock assessment history for demonstration
            assessment_history = [
                {"name": "Math Quiz - Algebra", "score": 85, "date": "2023-05-10", "national_avg": 78},
                {"name": "Science Lab - Chemistry", "score": 78, "date": "2023-05-05", "national_avg": 75},
                {"name": "Language Arts - Essay", "score": 90, "date": "2023-04-28", "national_avg": 82},
                {"name": "History - Civil War Test", "score": 82, "date": "2023-04-20", "national_avg": 80}
            ]
            
            for assessment in assessment_history:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{assessment['name']}**")
                with col2:
                    st.write(f"Score: {assessment['score']}%")
                with col3:
                    st.write(f"Date: {assessment['date']}")
                with col4:
                    comparison = assessment['score'] - assessment['national_avg']
                    if comparison > 0:
                        st.write(f"📈 +{comparison}% vs avg")
                    elif comparison < 0:
                        st.write(f"📉 {comparison}% vs avg")
                    else:
                        st.write(f"📊 At average")
                
                st.write("---")
            
            # AI-generated intervention suggestions
            st.subheader("Personalized Intervention Suggestions")
            
            # Generate suggestions based on student performance
            lowest_subject = min(student['performance'].items(), key=lambda x: x[1])
            
            if lowest_subject[1] < 70:
                st.warning(f"**Intervention Needed:** {lowest_subject[0].capitalize()} performance is below target.")
                st.write("**Suggested Actions:**")
                st.write("1. Schedule one-on-one tutoring session")
                st.write("2. Provide additional practice materials")
                st.write("3. Assign peer learning partner")
                st.write("4. Consider modified assessment approach")
            elif student['completed_assessments'] < 5:
                st.info("**Monitoring Suggested:** Student has completed few assessments.")
                st.write("**Suggested Actions:**")
                st.write("1. Ensure student is aware of all required assignments")
                st.write("2. Check for technical difficulties with platform access")
                st.write("3. Provide assessment calendar and reminders")
            else:
                st.success("**On Track:** Student is performing adequately across subjects.")
                st.write("**Suggested Actions:**")
                st.write("1. Challenge with advanced material in strong subjects")
                st.write("2. Encourage peer tutoring opportunities")
                st.write("3. Consider project-based assessments to boost engagement")
        
        elif page == "Assessment Management":
            st.title("Assessment Management")
            
            tab1, tab2 = st.tabs(["Current Assessments", "Create New Assessment"])
            
            with tab1:
                st.subheader("Active Assessments")
                
                assessments = get_available_assessments()
                for assessment in assessments:
                    with st.expander(f"{assessment['title']} - {assessment['subject']}"):
                        st.write(f"**Due Date:** {assessment['due_date']}")
                        st.write(f"**Description:** {assessment['description']}")
                        st.write(f"**Type:** {assessment['type']}")
                        
                        # Mock completion statistics
                        st.write("**Completion Statistics:**")
                        completed = assessment.get('completed', 18)
                        total = 28  # Total students
                        st.progress(completed/total)
                        st.write(f"{completed}/{total} students completed")
                        
                        # Average score if any completions
                        if completed > 0:
                            avg_score = assessment.get('avg_score', 76)
                            st.write(f"**Average Score:** {avg_score}%")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.button("View Submissions", key=f"view_{assessment['id']}")
                        with col2:
                            st.button("Edit Assessment", key=f"edit_{assessment['id']}")
            
            with tab2:
                st.subheader("Create New Assessment")
                
                assessment_title = st.text_input("Assessment Title")
                subject = st.selectbox("Subject", ["Math", "Science", "Language Arts", "History"])
                assessment_type = st.selectbox("Assessment Type", ["Quiz", "Test", "Essay", "Project", "Lab"])
                
                due_date = st.date_input("Due Date")
                estimated_time = st.slider("Estimated Completion Time (minutes)", 5, 120, 30)
                
                st.subheader("Assessment Content")
                description = st.text_area("Assessment Description")
                
                # Different input methods based on assessment type
                if assessment_type in ["Quiz", "Test"]:
                    st.write("**Add Questions:**")
                    
                    with st.expander("Question 1"):
                        st.text_area("Question Text", key="q1_text")
                        q1_type = st.selectbox("Question Type", ["Multiple Choice", "True/False", "Short Answer"], key="q1_type")
                        
                        if q1_type == "Multiple Choice":
                            st.text_input("Option A", key="q1_a")
                            st.text_input("Option B", key="q1_b")
                            st.text_input("Option C", key="q1_c")
                            st.text_input("Option D", key="q1_d")
                            st.selectbox("Correct Answer", ["A", "B", "C", "D"], key="q1_correct")
                    
                    st.button("+ Add Another Question")
                
                elif assessment_type == "Essay":
                    st.text_area("Essay Prompt")
                    st.number_input("Word Count Minimum", min_value=100, max_value=5000, value=500)
                    st.number_input("Word Count Maximum", min_value=100, max_value=5000, value=1000)
                    
                    st.write("**Rubric Criteria:**")
                    st.text_input("Criteria 1 (e.g., Thesis Statement)")
                    st.text_input("Criteria 2 (e.g., Evidence Quality)")
                    st.text_input("Criteria 3 (e.g., Organization)")
                    st.button("+ Add Rubric Criteria")
                
                elif assessment_type in ["Project", "Lab"]:
                    st.text_area("Project/Lab Instructions")
                    st.text_area("Deliverables")
                    st.text_area("Evaluation Criteria")
                    
                    st.checkbox("Allow File Uploads")
                    st.checkbox("Allow Team Submissions")
                
                # AI grading options
                st.subheader("AI Assessment Settings")
                st.checkbox("Enable AI Grading", value=True)
                st.checkbox("Generate Personalized Feedback", value=True)
                st.checkbox("Provide Improvement Suggestions", value=True)
                
                # Save the new assessment
                if st.button("Create Assessment"):
                    if assessment_title and description:
                        st.success(f"Assessment '{assessment_title}' created successfully!")
                        # In a complete implementation, this would save to a database
                    else:
                        st.error("Please fill in all required fields.")

# Main content area when not authenticated
if not st.session_state.authenticated:
    st.title("EduTutor AI - Personalized Learning and Assessment System")
    
    st.write("""
    ### Transform the learning experience with AI-powered personalization
    
    EduTutor AI provides educators and students with a comprehensive platform for personalized learning 
    and automated assessment. Our system adapts to individual learning styles and needs, providing 
    real-time feedback and customized learning paths.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎯 Personalized Learning")
        st.write("Adaptive learning paths tailored to each student's strengths and areas for improvement")
    
    with col2:
        st.subheader("✍️ Automated Assessment")
        st.write("AI-powered assessment that provides immediate, detailed feedback on student work")
    
    with col3:
        st.subheader("📊 Actionable Insights")
        st.write("Comprehensive analytics for teachers to monitor progress and identify intervention needs")
    
    st.info("Please log in using the sidebar to access the platform.")
    
    st.write("---")
    
    st.write("""
    ### How It Works
    
    1. **Students** receive personalized learning paths and complete assessments at their own pace
    2. **AI** evaluates submissions and provides detailed, contextual feedback
    3. **Teachers** gain insights into student performance with reduced grading workload
    4. **Everyone** benefits from a more efficient, effective learning environment
    """)
