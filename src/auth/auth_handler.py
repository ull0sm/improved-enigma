"""
Authentication Handler
Manages user authentication via Supabase Auth (Email + Google OAuth)
"""

import streamlit as st
from typing import Optional, Dict, Any
from src.auth.supabase_client import get_supabase_client
from src.auth.session import clear_session
from src.auth.whitelist import check_email_whitelist


def sign_up_with_email(email: str, password: str) -> Dict[str, Any]:
    """
    Sign up a new user with email and password.
    Checks whitelist before allowing signup.
    """
    # Check whitelist first
    whitelist = check_email_whitelist(email)
    if not whitelist['allowed']:
        return {
            'success': False,
            'error': 'Your email is not authorized. Please contact the administrator.'
        }
    
    try:
        supabase = get_supabase_client()
        result = supabase.auth.sign_up({
            'email': email,
            'password': password
        })
        
        if result.user:
            return {
                'success': True,
                'user': result.user,
                'session': result.session,
                'is_admin': whitelist['is_admin']
            }
        else:
            return {
                'success': False,
                'error': 'Signup failed. Please try again.'
            }
    except Exception as e:
        error_msg = str(e)
        if 'already registered' in error_msg.lower():
            return {
                'success': False,
                'error': 'This email is already registered. Please sign in instead.'
            }
        return {'success': False, 'error': error_msg}


def sign_in_with_email(email: str, password: str) -> Dict[str, Any]:
    """
    Sign in user with email and password.
    Checks whitelist before allowing signin.
    """
    # Check whitelist first
    whitelist = check_email_whitelist(email)
    if not whitelist['allowed']:
        return {
            'success': False,
            'error': 'Your email is not authorized. Please contact the administrator.'
        }
    
    try:
        supabase = get_supabase_client()
        result = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if result.user and result.session:
            return {
                'success': True,
                'user': result.user,
                'session': result.session,
                'is_admin': whitelist['is_admin']
            }
        else:
            return {
                'success': False,
                'error': 'Invalid credentials. Please try again.'
            }
    except Exception as e:
        error_msg = str(e)
        if 'invalid login credentials' in error_msg.lower():
            return {
                'success': False,
                'error': 'Invalid email or password.'
            }
        return {'success': False, 'error': error_msg}


def get_google_oauth_url() -> Optional[str]:
    """
    Get the Google OAuth URL for authentication.
    User will be redirected to Google, then back to the app.
    """
    try:
        supabase = get_supabase_client()
        
        # Get the current URL for redirect
        # In production, this should be your deployed URL
        redirect_url = st.secrets.get("app", {}).get("url", "http://localhost:8501")
        
        result = supabase.auth.sign_in_with_oauth({
            'provider': 'google',
            'options': {
                'redirect_to': redirect_url
            }
        })
        
        return result.url if result else None
    except Exception as e:
        st.error(f"Error initiating Google OAuth: {e}")
        return None


def handle_oauth_callback() -> Optional[Dict[str, Any]]:
    """
    Handle OAuth callback when user returns from Google.
    Extracts tokens from URL fragment and validates session.
    """
    try:
        # Check for code (PKCE flow) or access_token (Implicit flow)
        query_params = st.query_params
        
        code = query_params.get('code')
        access_token = query_params.get('access_token')
        refresh_token = query_params.get('refresh_token')
        
        supabase = get_supabase_client()
        session = None
        
        if code:
            # Exchange code for session (PKCE)
            try:
                res = supabase.auth.exchange_code_for_session({"auth_code": code})
                session = res.session
            except Exception as e:
                st.error(f"Error exchanging code: {e}")
                return None
        
        elif access_token:
            # Set session from tokens (Implicit)
            session = supabase.auth.set_session(access_token, refresh_token or "")
            
        if session and session.user:
            # Check whitelist
            whitelist = check_email_whitelist(session.user.email)
            if not whitelist['allowed']:
                # Sign out immediately if not whitelisted
                supabase.auth.sign_out()
                return {
                    'success': False,
                    'error': 'Your email is not authorized. Please contact the administrator.'
                }
            
            # Clear query params to clean up URL
            st.query_params.clear()
            
            return {
                'success': True,
                'user': session.user,
                'session': session,
                'is_admin': whitelist['is_admin']
            }
        
        return None
    except Exception as e:
        st.error(f"Error handling OAuth callback: {e}")
        return None


def sign_out() -> bool:
    """Sign out the current user."""
    supabase_ok = True
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception as e:
        st.error(f"Error signing out: {e}")
        supabase_ok = False
    
    try:
        # Clear session state and cookies
        clear_session()
    except Exception as e:
        st.error(f"Error clearing session: {e}")
    
    return supabase_ok


def get_current_session() -> Optional[Dict[str, Any]]:
    """Get the current authenticated session if valid."""
    try:
        supabase = get_supabase_client()
        session = supabase.auth.get_session()
        
        if session and session.user:
            return {
                'user': session.user,
                'session': session
            }
        return None
    except Exception:
        return None


def refresh_session() -> bool:
    """Refresh the current session to extend validity."""
    try:
        supabase = get_supabase_client()
        session = supabase.auth.refresh_session()
        return session is not None
    except Exception:
        return False
