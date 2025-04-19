import streamlit as st
import os
from dotenv import load_dotenv
from summarize_agent import EmailSummarizer
from access_messages import get_emails

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Email Summarizer",
    page_icon="📧",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
        color: black !important;
    }
    .summary-container {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-top: 20px;
    }
    /* Ensure password input text is black */
    input[type="password"] {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>📧 Email Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Get concise summaries of your emails in seconds</p>", unsafe_allow_html=True)

# Initialize the summarizer
@st.cache_resource
def get_summarizer():
    return EmailSummarizer()

summarizer = get_summarizer()

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("""
    This app uses AI to generate concise summaries of emails.
    
    Simply paste your email content in the text area and click 'Summarize'.
    """)
    
    st.header("Settings")
    api_key = st.text_input("OpenRouter API Key (optional)", 
                           value=os.getenv("OPENROUTER_API_KEY", ""), 
                           type="password",
                           help="Enter your OpenRouter API key if not set in environment variables")
    
    if st.button("Save API Key"):
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
            st.success("API Key saved for this session!")
            st.cache_resource.clear()
            summarizer = get_summarizer()
        else:
            st.error("Please enter an API key")

# Add tabs to the interface
tab1, tab2 = st.tabs(["📥 My Emails", "✍️ Manual Input"])

# Tab 1: Email Inbox
with tab1:
    st.header("Your Recent Emails")
    
    # Email credentials input
    with st.expander("Email Settings"):
        email_username = st.text_input("Gmail Address", 
                                     value=os.getenv("USERNAME", ""),
                                     help="Enter your Gmail address")
        email_password = st.text_input("App Password", 
                                     value=os.getenv("PASSWORD", ""),
                                     type="password",
                                     help="Enter your Gmail app password")
        
        if st.button("Save Email Settings"):
            if email_username and email_password:
                os.environ["USERNAME"] = email_username
                os.environ["PASSWORD"] = email_password
                st.success("Email settings saved for this session!")
            else:
                st.error("Please enter both email address and password")

    # Fetch and display emails
    if st.button("Fetch Recent Emails"):
        if not email_username or not email_password:
            st.error("Please enter your email credentials in Email Settings")
        else:
            with st.spinner("Fetching and summarizing emails..."):
                try:
                    emails = get_emails()
                    
                    for email_data in emails:
                        st.markdown("---")  # Separator between emails
                        st.markdown(f"### 📧 {email_data['subject']}")
                        
                        col1, col2 = st.columns([2, 3])
                        
                        with col1:
                            st.write("**From:**", email_data['from'])
                            st.write("**Subject:**", email_data['subject'])
                            
                            # Store email data
                            email_key = f"{email_data['subject']}_{email_data['from']}"
                            
                            # Original email content display removed
                            
                        with col2:
                            summary = summarizer.summarize(email_data['content'])
                            st.markdown("<div class='summary-container'>", unsafe_allow_html=True)
                            st.write("**Summary:**")
                            st.write(summary)
                            st.markdown("</div>", unsafe_allow_html=True)
                                
                except Exception as e:
                    st.error(f"Error fetching emails: {str(e)}")

# Tab 2: Manual Input
with tab2:
    st.header("Manual Email Input")

    # Sample emails for demonstration
    sample_emails = {
        "Meeting Reschedule": """
        Hi Team,
        
        The weekly team meeting has been rescheduled to Friday at 3 PM instead of Thursday. 
        Please update your calendars accordingly. Let me know if you have any scheduling conflicts.
        
        Best regards,
        Alice
        """,
        "Project Update": """
        Dear Team,
        
        I wanted to provide a quick update on Project X. We've completed the first phase ahead of schedule
        and will begin phase 2 next week. Please review the attached documentation and provide your feedback
        by Wednesday.
        
        Thanks,
        Bob
        """
    }

    # Email selection or custom input
    email_option = st.radio(
        "Choose an option:",
        ["Use sample email", "Enter your own email"]
    )

    if email_option == "Use sample email":
        sample_choice = st.selectbox("Select a sample email:", list(sample_emails.keys()))
        email_content = sample_emails[sample_choice]
        st.text_area("Email Content", email_content, height=250)
    else:
        email_content = st.text_area("Paste your email content here:", height=250)

    # Summarize button
    if st.button("Summarize Email", type="primary"):
        if not email_content.strip():
            st.error("Please enter some email content to summarize.")
        else:
            with st.spinner("Generating summary..."):
                try:
                    summary = summarizer.summarize(email_content)
                    
                    if summary.startswith('{"error":'):
                        import json
                        error_msg = json.loads(summary)["error"]
                        st.error(f"Error: {error_msg}")
                    else:
                        st.markdown("<div class='summary-container'>", unsafe_allow_html=True)
                        st.subheader("Summary")
                        st.write(summary)
                        st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Made by Prince")