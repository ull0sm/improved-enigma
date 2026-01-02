"""
Login Page
Ultra-clean authentication interface with Email + Google OAuth
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Login - EntryDesk",
    page_icon="🥋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Hide sidebar on login page
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

from src.auth.session import init_session_state, is_authenticated, is_onboarding_complete, set_user_session
from src.auth.auth_handler import (
    sign_in_with_email, 
    sign_up_with_email, 
    get_google_oauth_url,
    check_email_whitelist
)

init_session_state()

# If already authenticated, redirect
if is_authenticated():
    if is_onboarding_complete():
        st.switch_page("pages/3_🏠_Dashboard.py")
    else:
        st.switch_page("pages/2_📝_Onboarding.py")

# Login Page UI
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        ">🥋 EntryDesk</h1>
        <p style="color: #64748b; margin-top: 0.5rem; font-size: 1rem;">
            Tournament Registration Manager
        </p>
    </div>
""", unsafe_allow_html=True)

# Login Card Container
st.markdown("""
    <div style="
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        max-width: 400px;
        margin: 0 auto;
    ">
""", unsafe_allow_html=True)

# Tabs for Login/Signup
tab_login, tab_signup = st.tabs(["🔑 Sign In", "✨ Sign Up"])

with tab_login:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Google OAuth Button
    google_url = get_google_oauth_url()
    if google_url:
        st.markdown(f"""
            <a href="{google_url}" target="_self" style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
                background: #ffffff;
                color: #1f2937;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.2s ease;
                margin-bottom: 1.5rem;
            " onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform='translateY(0)'">
                <svg width="20" height="20" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
            </a>
        """, unsafe_allow_html=True)
        
        # Divider
        st.markdown("""
            <div style="display: flex; align-items: center; margin: 1rem 0;">
                <div style="flex: 1; border-bottom: 1px solid rgba(255,255,255,0.1);"></div>
                <span style="padding: 0 1rem; color: #64748b; font-size: 0.8rem;">or</span>
                <div style="flex: 1; border-bottom: 1px solid rgba(255,255,255,0.1);"></div>
            </div>
        """, unsafe_allow_html=True)
    
    # Email Login Form
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="coach@dojo.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Signing in..."):
                    result = sign_in_with_email(email, password)
                    
                    if result['success']:
                        set_user_session(
                            result['user'],
                            result['session'],
                            result.get('is_admin', False)
                        )
                        st.success("✅ Signed in successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

with tab_signup:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Signup Form
    with st.form("signup_form"):
        new_email = st.text_input("Email", placeholder="coach@dojo.com", key="signup_email")
        new_password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="confirm_password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            if not new_email or not new_password:
                st.error("Please fill in all fields")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                with st.spinner("Creating account..."):
                    result = sign_up_with_email(new_email, new_password)
                    
                    if result['success']:
                        set_user_session(
                            result['user'],
                            result['session'],
                            result.get('is_admin', False)
                        )
                        st.success("✅ Account created! Redirecting to setup...")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
    
    st.markdown("""
        <p style="color: #64748b; font-size: 0.75rem; text-align: center; margin-top: 1rem;">
            ⚠️ Only authorized emails can register. Contact the administrator for access.
        </p>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <p style="color: #475569; font-size: 0.75rem;">
            🥋 EntryDesk v1.0 | Secure Tournament Registration
        </p>
    </div>
""", unsafe_allow_html=True)
