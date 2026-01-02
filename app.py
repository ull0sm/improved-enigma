"""
EntryDesk - Karate Tournament Manager
Main Application Entry Point
"""

import streamlit as st
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="EntryDesk - Tournament Manager",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'styles.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize session state
from src.auth.session import init_session_state, is_authenticated, is_onboarding_complete, restore_session_from_cookie

init_session_state()

# Attempt to restore session from cookie (Persistent Auth)
restore_session_from_cookie()

# Check for OAuth callback (when returning from Google)
from src.auth.auth_handler import handle_oauth_callback

oauth_result = handle_oauth_callback()
if oauth_result:
    if oauth_result.get('success'):
        from src.auth.session import set_user_session
        set_user_session(
            oauth_result['user'],
            oauth_result['session'],
            oauth_result.get('is_admin', False)
        )
        st.rerun()
    else:
        st.error(oauth_result.get('error', 'Authentication failed'))

# Routing logic
if not is_authenticated():
    # Redirect to login
    st.switch_page("pages/1_🔐_Login.py")
elif not is_onboarding_complete():
    # Redirect to onboarding
    st.switch_page("pages/2_📝_Onboarding.py")
else:
    # Redirect to dashboard
    st.switch_page("pages/3_🏠_Dashboard.py")
