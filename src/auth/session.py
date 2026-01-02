"""
Session Management
Handles user session state, route protection, and role-based access
"""

import streamlit as st
from typing import Optional, Dict, Any
from src.auth.supabase_client import get_supabase_client
from src.auth.whitelist import check_email_whitelist
import extra_streamlit_components as stx
import datetime
import time

# Cookie Manager
# We must use cache_resource to keep the component instance alive
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager(key="auth_cookie_manager")



def init_session_state():
    """Initialize session state variables if not present."""
    defaults = {
        'user': None,
        'session': None,
        'is_admin': False,
        'coach': None,
        'onboarding_complete': False,
        'current_page': 'login'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_user_session(user: Any, session: Any, is_admin: bool = False):
    """Set user session after successful authentication."""
    st.session_state.user = user
    st.session_state.session = session
    st.session_state.is_admin = is_admin
    
    # Load coach profile if exists
    load_coach_profile()
    
    # Persist session to cookie
    persist_session_to_cookie(session)


def persist_session_to_cookie(session: Any):
    """Save Supabase session tokens to browser cookie (30 days)."""
    try:
        cookie_manager = get_cookie_manager()
        # Save access and refresh tokens
        # Values are typically strings in Supabase session object
        token_data = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token
        }
        
        # Set cookie to expire in 30 days
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        
        cookie_manager.set(
            "supabase_session", 
            token_data, 
            expires_at=expires_at,
            key="set_session_cookie"
        )
    except Exception as e:
        st.warning(f"Failed to save session cookie: {e}")


def restore_session_from_cookie():
    """Attempt to restore session from browser cookie on app load."""
    # If already authenticated, skip
    if is_authenticated():
        return

    try:
        cookie_manager = get_cookie_manager()
        
        # Get cookies (no loop to avoid duplicate key error)
        # The component should trigger a rerun when data is ready
        cookies = cookie_manager.get_all()
        
        token_data = cookies.get("supabase_session") if cookies else None
        
        if not token_data:
            return

        # Restore Supabase session
        supabase = get_supabase_client()
        
        # Check if we have valid dictionary data
        if isinstance(token_data, dict) and 'access_token' in token_data and 'refresh_token' in token_data:
            response = supabase.auth.set_session(
                token_data['access_token'],
                token_data['refresh_token']
            )
            
            if response.user and response.session:
                # Validate whitelist again to be safe
                whitelist = check_email_whitelist(response.user.email)
                if whitelist['allowed']:
                    # Manually set session state without triggering another cookie write (recursion)
                    st.session_state.user = response.user
                    st.session_state.session = response.session
                    st.session_state.is_admin = whitelist['is_admin']
                    load_coach_profile()
                    st.rerun() # Force rerun to reflect login state immediately
                else:
                    clear_session()
            else:
                # Tokens were present but did not produce a valid session; drop any stale cookie
                clear_session()
    except Exception as e:
        print(f"Session restore failed: {e}") 
        clear_session()



def load_coach_profile():
    """Load coach profile from database."""
    if not st.session_state.get('user'):
        return
    
    try:
        supabase = get_supabase_client()
        user_id = st.session_state.user.id
        
        result = supabase.table('coaches')\
            .select('*, dojos(name)')\
            .eq('id', user_id)\
            .execute()
        
        if result.data:
            coach = result.data[0]
            st.session_state.coach = coach
            st.session_state.onboarding_complete = coach.get('onboarding_complete', False)
            st.session_state.is_admin = coach.get('is_admin', False)
        else:
            st.session_state.coach = None
            st.session_state.onboarding_complete = False
    except Exception as e:
        st.error(f"Error loading profile: {e}")


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return st.session_state.get('user') is not None


def is_onboarding_complete() -> bool:
    """Check if user has completed onboarding."""
    return st.session_state.get('onboarding_complete', False)


def is_admin() -> bool:
    """Check if current user is an admin."""
    return st.session_state.get('is_admin', False)


def get_current_user() -> Optional[Any]:
    """Get the current authenticated user object."""
    return st.session_state.get('user')


def get_current_coach() -> Optional[Dict]:
    """Get the current coach profile."""
    return st.session_state.get('coach')


def get_user_dojo_id() -> Optional[str]:
    """Get the current user's dojo ID."""
    coach = get_current_coach()
    return coach.get('dojo_id') if coach else None


def get_user_dojo_name() -> Optional[str]:
    """Get the current user's dojo name."""
    coach = get_current_coach()
    if coach and coach.get('dojos'):
        return coach['dojos'].get('name')
    return None


def require_auth():
    """
    Route protection - require authentication.
    Call this at the TOP of every protected page.
    Redirects to login if not authenticated.
    """
    init_session_state()
    
    if not is_authenticated():
        st.session_state.current_page = 'login'
        st.switch_page("pages/1_🔐_Login.py")


def require_onboarding():
    """
    Route protection - require completed onboarding.
    Call this after require_auth() on protected pages.
    Redirects to onboarding if not complete.
    """
    if not is_onboarding_complete():
        st.session_state.current_page = 'onboarding'
        st.switch_page("pages/2_📝_Onboarding.py")


def require_admin():
    """
    Route protection - require admin role.
    Call this on admin-only pages.
    Shows error and stops if not admin.
    """
    if not is_admin():
        st.error("🚫 Admin access required")
        st.info("You don't have permission to access this page.")
        st.stop()


def clear_session():
    """Clear all session state (for logout)."""
    keys_to_clear = ['user', 'session', 'is_admin', 'coach', 'onboarding_complete']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear cookie
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete("supabase_session", key="delete_session_cookie")
    except Exception as e:
        print(f"Error clearing cookie: {e}")

    st.session_state.current_page = 'login'
