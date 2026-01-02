"""
Onboarding Page
New user profile setup - Dojo selection and personal details
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Setup Profile - EntryDesk",
    page_icon="🥋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Hide sidebar on onboarding page
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

from src.auth.session import (
    init_session_state, 
    is_authenticated, 
    is_onboarding_complete,
    get_current_user,
    load_coach_profile
)
from src.auth.supabase_client import get_supabase_client, get_authenticated_client
from src.auth.auth_handler import check_email_whitelist

init_session_state()

# Require authentication
if not is_authenticated():
    st.switch_page("pages/1_🔐_Login.py")

# If onboarding complete, redirect to dashboard
if is_onboarding_complete():
    st.switch_page("pages/3_🏠_Dashboard.py")

user = get_current_user()

# Header
st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 style="
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        ">👋 Welcome to EntryDesk!</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            Let's set up your profile to get started
        </p>
    </div>
""", unsafe_allow_html=True)

# Progress indicator
st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
    ">
        <div style="width: 2rem; height: 4px; background: #6366f1; border-radius: 2px;"></div>
        <div style="width: 2rem; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px;"></div>
        <div style="width: 2rem; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px;"></div>
    </div>
""", unsafe_allow_html=True)

# Onboarding Card
st.markdown("""
    <div style="
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        max-width: 500px;
        margin: 0 auto;
    ">
""", unsafe_allow_html=True)


def get_existing_dojos():
    """Fetch existing dojos from database."""
    try:
        supabase = get_supabase_client()
        # Public read access is allowed by RLS for dojos, so Anon client is fine here
        result = supabase.table('dojos').select('id, name').order('name').execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error loading dojos: {e}")
        return []


def create_dojo(name: str):
    """Create a new dojo."""
    try:
        # Use authenticated client for creating dojo
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        result = supabase.table('dojos').insert({'name': name.strip()}).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        if 'duplicate' in str(e).lower():
            st.error("A dojo with this name already exists")
        else:
            st.error(f"Error creating dojo: {e}")
        return None


def complete_onboarding(full_name: str, phone: str, dojo_id: str):
    """Complete the onboarding process by creating coach profile."""
    try:
        # Check if user is admin
        # Whitelist check can use anon client
        whitelist = check_email_whitelist(user.email)
        is_admin = whitelist.get('is_admin', False)
        
        # Create coach profile
        coach_data = {
            'id': user.id,
            'email': user.email,
            'full_name': full_name.strip(),
            'phone': phone.strip() if phone else None,
            'dojo_id': dojo_id,
            'is_admin': is_admin,
            'onboarding_complete': True
        }
        
        # Use authenticated client for creating profile
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        result = supabase.table('coaches').insert(coach_data).execute()
        
        if result.data:
            # Reload profile into session
            load_coach_profile()
            return True
        return False
        
    except Exception as e:
        if 'duplicate' in str(e).lower():
            st.error("Profile already exists. Refreshing...")
            load_coach_profile()
            st.rerun()
        else:
            st.error(f"Error completing setup: {e}")
        return False


# Get existing dojos
dojos = get_existing_dojos()
dojo_options = {d['name']: d['id'] for d in dojos}

with st.form("onboarding_form"):
    st.markdown("<h3 style='color: #e2e8f0; margin-top: 0;'>📋 Your Details</h3>", unsafe_allow_html=True)
    
    full_name = st.text_input(
        "Full Name *",
        placeholder="Enter your full name",
        help="This will be displayed in the app"
    )
    
    phone = st.text_input(
        "Phone Number",
        placeholder="+91 98765 43210 (optional)",
        help="For tournament communication"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>🏢 Your Dojo/Club</h3>", unsafe_allow_html=True)
    
    # Dojo selection
    dojo_choice = st.radio(
        "Select your dojo:",
        options=["existing", "new"],
        format_func=lambda x: "Select existing dojo" if x == "existing" else "Register new dojo",
        horizontal=True
    )
    
    selected_dojo_id = None
    
    if dojo_choice == "existing":
        if dojo_options:
            selected_dojo = st.selectbox(
                "Choose your dojo",
                options=list(dojo_options.keys()),
                index=0
            )
            selected_dojo_id = dojo_options[selected_dojo]
        else:
            st.info("No dojos registered yet. Please create a new one.")
            dojo_choice = "new"
    
    if dojo_choice == "new":
        new_dojo_name = st.text_input(
            "Dojo Name *",
            placeholder="e.g., Tiger Karate Academy"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Complete Setup", use_container_width=True)
    
    if submitted:
        # Validation
        if not full_name or not full_name.strip():
            st.error("Please enter your full name")
        elif dojo_choice == "new" and (not new_dojo_name or not new_dojo_name.strip()):
            st.error("Please enter your dojo name")
        elif dojo_choice == "existing" and not selected_dojo_id:
            st.error("Please select a dojo")
        else:
            with st.spinner("Setting up your profile..."):
                # Create new dojo if needed
                if dojo_choice == "new":
                    new_dojo = create_dojo(new_dojo_name)
                    if new_dojo:
                        selected_dojo_id = new_dojo['id']
                    else:
                        st.stop()
                
                # Complete onboarding
                if complete_onboarding(full_name, phone, selected_dojo_id):
                    st.success("✅ Profile created successfully!")
                    st.balloons()
                    st.switch_page("pages/3_🏠_Dashboard.py")

st.markdown("</div>", unsafe_allow_html=True)

# Email info
st.markdown(f"""
    <div style="text-align: center; margin-top: 1.5rem;">
        <p style="color: #64748b; font-size: 0.8rem;">
            Signed in as: <strong style="color: #94a3b8;">{user.email if user else 'Unknown'}</strong>
        </p>
    </div>
""", unsafe_allow_html=True)
