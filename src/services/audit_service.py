"""
Audit Service
Handles immutable audit logging for data safety (the "Black Box")
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from src.auth.supabase_client import get_supabase_client, get_authenticated_client
import json


def create_audit_log(
    action: str,
    athlete_data: Dict[str, Any],
    coach_id: str,
    coach_email: str,
    dojo_name: str
) -> bool:
    """
    Create an immutable audit log entry.
    This is write-only - entries cannot be modified or deleted.
    
    Args:
        action: One of 'REGISTER', 'UPDATE', 'DELETE', 'BULK_REGISTER'
        athlete_data: The athlete data or changes being logged
        coach_id: ID of the coach performing the action
        coach_email: Email of the coach
        dojo_name: Name of the dojo
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not st.session_state.get('session'):
            return False
            
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        log_entry = {
            'action': action,
            'athlete_data': athlete_data,
            'coach_id': coach_id,
            'coach_email': coach_email,
            'dojo_name': dojo_name
        }
        
        result = supabase.table('audit_logs').insert(log_entry).execute()
        return bool(result.data)
        
    except Exception as e:
        # Log error but don't fail the main operation
        print(f"Warning: Failed to create audit log: {e}")
        return False


def get_audit_logs(
    limit: int = 100,
    action_filter: Optional[str] = None,
    coach_filter: Optional[str] = None,
    dojo_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve audit logs (Admin only - enforced by RLS).
    
    Args:
        limit: Maximum number of logs to retrieve
        action_filter: Filter by action type
        coach_filter: Filter by coach email
        dojo_filter: Filter by dojo name
    
    Returns:
        List of audit log entries
    """
    try:
        if not st.session_state.get('session'):
             return []
             
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        query = supabase.table('audit_logs')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)
        
        if action_filter and action_filter != 'All':
            query = query.eq('action', action_filter)
        
        if coach_filter:
            query = query.ilike('coach_email', f'%{coach_filter}%')
        
        if dojo_filter:
            query = query.ilike('dojo_name', f'%{dojo_filter}%')
        
        result = query.execute()
        return result.data if result.data else []
        
    except Exception as e:
        st.error(f"Error fetching audit logs: {e}")
        return []


def get_audit_summary() -> Dict[str, Any]:
    """
    Get a summary of audit log statistics (Admin only).
    """
    try:
        logs = get_audit_logs(limit=1000)
        
        summary = {
            'total_entries': len(logs),
            'by_action': {},
            'by_dojo': {},
            'recent_activity': []
        }
        
        for log in logs:
            # By action
            action = log.get('action', 'Unknown')
            summary['by_action'][action] = summary['by_action'].get(action, 0) + 1
            
            # By dojo
            dojo = log.get('dojo_name', 'Unknown')
            summary['by_dojo'][dojo] = summary['by_dojo'].get(dojo, 0) + 1
        
        # Recent activity (last 10)
        summary['recent_activity'] = logs[:10]
        
        return summary
        
    except Exception as e:
        st.error(f"Error generating audit summary: {e}")
        return {
            'total_entries': 0,
            'by_action': {},
            'by_dojo': {},
            'recent_activity': []
        }


def format_audit_log_for_display(log: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format an audit log entry for user-friendly display.
    """
    from datetime import datetime
    
    # Parse timestamp
    created_at = log.get('created_at', '')
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        formatted_time = created_at
    
    # Format action with emoji
    action_icons = {
        'REGISTER': '➕',
        'UPDATE': '✏️',
        'DELETE': '🗑️',
        'BULK_REGISTER': '📦'
    }
    
    action = log.get('action', 'Unknown')
    action_display = f"{action_icons.get(action, '📋')} {action}"
    
    # Parse athlete data
    athlete_data = log.get('athlete_data', {})
    if isinstance(athlete_data, str):
        try:
            athlete_data = json.loads(athlete_data)
        except:
            pass
    
    # Create description
    if action == 'REGISTER':
        description = f"Registered athlete: {athlete_data.get('full_name', 'Unknown')}"
    elif action == 'UPDATE':
        description = f"Updated athlete ID: {athlete_data.get('athlete_id', 'Unknown')}"
    elif action == 'DELETE':
        description = f"Deleted athlete: {athlete_data.get('full_name', 'Unknown')}"
    elif action == 'BULK_REGISTER':
        count = athlete_data.get('count', 0)
        description = f"Bulk registered {count} athletes"
    else:
        description = "Unknown action"
    
    return {
        'timestamp': formatted_time,
        'action': action_display,
        'description': description,
        'coach': log.get('coach_email', 'Unknown'),
        'dojo': log.get('dojo_name', 'Unknown'),
        'raw_data': athlete_data
    }
