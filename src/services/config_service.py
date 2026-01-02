"""
Configuration Service
Handles dynamic tournament configuration (Admin-managed)
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import json
from src.auth.supabase_client import get_supabase_client, get_authenticated_client
from src.auth.session import get_current_user


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_config(key: str) -> Any:
    """
    Get a configuration value by key.
    Cached for performance.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table('config')\
            .select('value')\
            .eq('key', key)\
            .execute()
        
        if result.data:
            value = result.data[0].get('value')
            # Parse JSON if needed
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except:
                    return value
            return value
        return None
        
    except Exception as e:
        st.error(f"Error fetching config '{key}': {e}")
        return None


def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration values.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table('config')\
            .select('*')\
            .execute()
        
        config = {}
        for row in result.data or []:
            key = row.get('key')
            value = row.get('value')
            # Parse JSON if needed
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    pass
            config[key] = value
        
        return config
        
    except Exception as e:
        st.error(f"Error fetching config: {e}")
        return {}


def update_config(key: str, value: Any) -> Dict[str, Any]:
    """
    Update a configuration value (Admin only).
    """
    user = get_current_user()
    if not user:
        return {'success': False, 'error': 'Not authenticated'}
    
    try:
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        # Convert value to JSON if needed
        if not isinstance(value, str):
            value = json.dumps(value)
        
        result = supabase.table('config')\
            .upsert({
                'key': key,
                'value': value,
                'updated_at': datetime.utcnow().isoformat(),
                'updated_by': user.id
            })\
            .execute()
        
        if result.data:
            # Clear cache
            get_config.clear()
            return {'success': True}
        else:
            return {'success': False, 'error': 'Update failed'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_tournament_name() -> str:
    """Get the tournament name from config."""
    name = get_config('tournament_name')
    return name if name else 'Karate Championship'


def get_tournament_dates() -> Dict[str, str]:
    """Get tournament dates from config."""
    dates = get_config('tournament_dates')
    return dates if dates else {'day1': '', 'day2': ''}


def is_registration_open() -> bool:
    """Check if registration is currently open."""
    # Check the registration_open flag
    is_open = get_config('registration_open')
    if not is_open:
        return False
    
    # Check deadline
    deadline_str = get_config('registration_deadline')
    if deadline_str:
        try:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            if datetime.now(deadline.tzinfo) > deadline:
                return False
        except:
            pass
    
    return True


def get_registration_deadline() -> Optional[datetime]:
    """Get the registration deadline as datetime."""
    deadline_str = get_config('registration_deadline')
    if deadline_str:
        try:
            return datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        except:
            pass
    return None


def get_time_until_deadline() -> Optional[str]:
    """Get human-readable time until registration deadline."""
    deadline = get_registration_deadline()
    if not deadline:
        return None
    
    now = datetime.now(deadline.tzinfo)
    diff = deadline - now
    
    if diff.total_seconds() < 0:
        return "Registration closed"
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h remaining"
    elif hours > 0:
        return f"{hours}h {minutes}m remaining"
    else:
        return f"{minutes}m remaining"
