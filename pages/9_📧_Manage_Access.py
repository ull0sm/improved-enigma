"""
Manage Access Page (Admin)
Control email whitelist for authorized users
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Manage Access - EntryDesk",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

from src.auth.session import init_session_state, require_auth, require_onboarding, require_admin, get_current_user
from src.components.sidebar import render_sidebar
from src.auth.supabase_client import get_supabase_client, get_authenticated_client

init_session_state()
require_auth()
require_onboarding()
require_admin()

# Render sidebar
render_sidebar()


def get_allowed_emails():
    """Get all whitelisted emails."""
    try:
        # Checking emails can be done with Anon if public, but safer with auth if possible
        # RLS says "Anyone can check whitelist", so get_supabase_client is fine for READING.
        # But if we want to be consistent, we can use auth.
        supabase = get_supabase_client()
        result = supabase.table('allowed_emails')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        return []


def add_allowed_email(email: str, is_admin: bool):
    """Add email to whitelist."""
    try:
        user = get_current_user()
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        result = supabase.table('allowed_emails').insert({
            'email': email.lower().strip(),
            'is_admin': is_admin,
            'added_by': user.id
        }).execute()
        
        return bool(result.data)
    except Exception as e:
        if 'duplicate' in str(e).lower():
            st.error("This email is already in the whitelist")
        else:
            st.error(f"Error adding email: {e}")
        return False


def remove_allowed_email(email_id: str):
    """Remove email from whitelist."""
    try:
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        supabase.table('allowed_emails').delete().eq('id', email_id).execute()
        return True
    except Exception as e:
        st.error(f"Error removing email: {e}")
        return False


def update_admin_status(email_id: str, is_admin: bool):
    """Update admin status for an email."""
    try:
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        supabase.table('allowed_emails')\
            .update({'is_admin': is_admin})\
            .eq('id', email_id)\
            .execute()
        return True
    except Exception as e:
        st.error(f"Error updating: {e}")
        return False


# Initialize delete confirmation state
if 'delete_email_id' not in st.session_state:
    st.session_state.delete_email_id = None

# Header
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <p style="color: #8b5cf6; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 0;">
            🔐 Admin Settings
        </p>
        <h1 style="
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.25rem 0 0 0;
        ">📧 Manage Access</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            Control who can access the system by managing the email whitelist
        </p>
    </div>
""", unsafe_allow_html=True)

# Info banner
st.markdown("""
    <div style="
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <p style="color: #e2e8f0; margin: 0; font-size: 0.9rem;">
            ℹ️ <strong>How it works:</strong> Only emails in this list can sign in or sign up. 
            Users with <span style="color: #8b5cf6;">Admin</span> access get additional management capabilities.
        </p>
    </div>
""", unsafe_allow_html=True)

# Add new email
st.markdown("<h3 style='color: #e2e8f0;'>➕ Add Authorized Email</h3>", unsafe_allow_html=True)

with st.form("add_email_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        new_email = st.text_input(
            "Email Address",
            placeholder="coach@dojo.com",
            label_visibility="collapsed"
        )
    
    with col2:
        grant_admin = st.checkbox("Admin Access", help="Grant admin privileges")
    
    with col3:
        if st.form_submit_button("Add Email", use_container_width=True):
            if not new_email or '@' not in new_email:
                st.error("Please enter a valid email address")
            else:
                if add_allowed_email(new_email, grant_admin):
                    st.success(f"✅ Added: {new_email}")
                    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Current whitelist
st.markdown("<h3 style='color: #e2e8f0;'>📋 Authorized Emails</h3>", unsafe_allow_html=True)

emails = get_allowed_emails()

if not emails:
    st.info("No emails in whitelist. Add some emails to allow access.")
else:
    # Get current user to prevent self-removal
    current_user = get_current_user()
    
    for email_entry in emails:
        email = email_entry.get('email', '')
        is_admin = email_entry.get('is_admin', False)
        email_id = email_entry.get('id', '')
        is_self = current_user and current_user.email.lower() == email.lower()
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                badge_color = "#8b5cf6" if is_admin else "#64748b"
                badge_text = "🔑 Admin" if is_admin else "👤 Coach"
                
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0;">
                        <span style="color: #e2e8f0; font-weight: 500;">{email}</span>
                        <span style="
                            background: {badge_color}20;
                            color: {badge_color};
                            padding: 0.25rem 0.5rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                        ">{badge_text}</span>
                        {'<span style="color: #10b981; font-size: 0.75rem;">(You)</span>' if is_self else ''}
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                created = str(email_entry.get('created_at', ''))[:10]
                st.markdown(f"""
                    <p style="color: #64748b; font-size: 0.8rem; margin: 0.5rem 0;">
                        Added: {created}
                    </p>
                """, unsafe_allow_html=True)
            
            with col3:
                if not is_self:
                    if is_admin:
                        if st.button("Remove Admin", key=f"demote_{email_id}", use_container_width=True):
                            if update_admin_status(email_id, False):
                                st.rerun()
                    else:
                        if st.button("Make Admin", key=f"promote_{email_id}", use_container_width=True):
                            if update_admin_status(email_id, True):
                                st.rerun()
            
            with col4:
                if not is_self:
                    if st.session_state.delete_email_id == email_id:
                        if st.button("✓ Confirm", key=f"confirm_{email_id}", type="primary"):
                            if remove_allowed_email(email_id):
                                st.session_state.delete_email_id = None
                                st.rerun()
                    else:
                        if st.button("🗑️", key=f"delete_{email_id}", help="Remove access"):
                            st.session_state.delete_email_id = email_id
                            st.rerun()
                else:
                    st.markdown("""
                        <p style="color: #64748b; font-size: 0.75rem; text-align: center; margin: 0.5rem 0;">
                            Can't remove self
                        </p>
                    """, unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 0.5rem 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

# Stats
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

admin_count = len([e for e in emails if e.get('is_admin')])
coach_count = len(emails) - admin_count

with col1:
    st.markdown(f"""
        <div style="
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #8b5cf6; font-size: 1.5rem; font-weight: 700; margin: 0;">{len(emails)}</p>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Total Authorized</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #6366f1; font-size: 1.5rem; font-weight: 700; margin: 0;">{admin_count}</p>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Admins</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #06b6d4; font-size: 1.5rem; font-weight: 700; margin: 0;">{coach_count}</p>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Coaches</p>
        </div>
    """, unsafe_allow_html=True)
