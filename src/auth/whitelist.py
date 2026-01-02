import streamlit as st
from typing import Dict, Any
from src.auth.supabase_client import get_supabase_client


def check_email_whitelist(email: str) -> Dict[str, Any]:
    """
    Check if email is in the allowed_emails whitelist.
    Returns dict with 'allowed' and 'is_admin' status.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table('allowed_emails')\
            .select('*')\
            .eq('email', email.lower().strip())\
            .execute()
        
        if not result.data:
            return {'allowed': False, 'is_admin': False}
        
        return {
            'allowed': True,
            'is_admin': result.data[0].get('is_admin', False)
        }
    except Exception as e:
        st.error(f"Error checking whitelist: {e}")
        return {'allowed': False, 'is_admin': False}
