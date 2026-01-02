
"""
Athlete Service
Handles all athlete-related database operations with audit logging
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from src.auth.supabase_client import get_supabase_client, get_authenticated_client
from src.auth.session import get_current_user, get_current_coach, get_user_dojo_id
from src.services.audit_service import create_audit_log


def check_duplicate_athlete(full_name: str, date_of_birth: str, dojo_id: str) -> bool:
    """
    Check if athlete already exists (Name + DOB + Dojo).
    Returns True if duplicate exists.
    """
    try:
        # Check duplicate logic could be done with anon client if RLS allowed select, 
        # but RLS restricts viewing athletes to own coach/admin.
        # So we MUST use authenticated client.
        if not st.session_state.get('session'):
             return False
             
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        # If dojo_id is None, maybe we can't check? 
        # But RLS enforces we only see our own athletes anyway.
        # Actually duplicate check should ideally be GLOBAL? 
        # No, uniqueness is (Name + DOB + Dojo).
        # So checking our own view is sufficient.
        
        query = supabase.table('athletes')\
            .select('id')\
            .eq('full_name', full_name.strip())\
            .eq('date_of_birth', date_of_birth)
            
        if dojo_id:
            query = query.eq('dojo_id', dojo_id)
            
        result = query.execute()
        
        return len(result.data) > 0
    except Exception as e:
        st.error(f"Error checking duplicate: {e}")
        return False


def register_athlete(athlete_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a single athlete with duplicate check and audit logging.
    """
    user = get_current_user()
    coach = get_current_coach()
    
    if not user or not coach:
        return {'success': False, 'error': 'Not authenticated'}
    
    dojo_id = coach.get('dojo_id')
    if not dojo_id:
        return {'success': False, 'error': 'No dojo associated with your account'}
    
    # Check for duplicate
    if check_duplicate_athlete(
        athlete_data['full_name'],
        athlete_data['date_of_birth'],
        dojo_id
    ):
        return {
            'success': False,
            'error': f"Athlete '{athlete_data['full_name']}' with this date of birth already exists in your dojo."
        }
    
    try:
        if not st.session_state.get('session'):
            return {'success': False, 'error': 'Not authenticated'}
            
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        # Prepare data
        data = {
            'coach_id': user.id,
            'dojo_id': dojo_id,
            'full_name': athlete_data['full_name'].strip(),
            'date_of_birth': athlete_data['date_of_birth'],
            'gender': athlete_data['gender'],
            'belt_rank': athlete_data['belt_rank'],
            'weight_kg': athlete_data.get('weight_kg'),
            'competition_day': athlete_data['competition_day'],
            'kata_event': athlete_data.get('kata_event', False),
            'kumite_event': athlete_data.get('kumite_event', False)
        }
        
        result = supabase.table('athletes').insert(data).execute()
        
        if result.data:
            # Create audit log
            create_audit_log(
                action='REGISTER',
                athlete_data=data,
                coach_id=user.id,
                coach_email=user.email,
                dojo_name=coach.get('dojos', {}).get('name', 'Unknown')
            )
            
            return {'success': True, 'athlete': result.data[0]}
        else:
            return {'success': False, 'error': 'Failed to register athlete'}
            
    except Exception as e:
        error_msg = str(e)
        if 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
            return {
                'success': False,
                'error': f"Athlete '{athlete_data['full_name']}' already exists."
            }
        return {'success': False, 'error': error_msg}


def bulk_register_athletes(athletes_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bulk register multiple athletes with validation and audit logging.
    Returns summary of successful and failed registrations.
    """
    user = get_current_user()
    coach = get_current_coach()
    
    if not user or not coach:
        return {'success': False, 'error': 'Not authenticated', 'results': []}
    
    dojo_id = coach.get('dojo_id')
    dojo_name = coach.get('dojos', {}).get('name', 'Unknown')
    
    if not dojo_id:
        return {'success': False, 'error': 'No dojo associated with your account', 'results': []}
    
    results = []
    successful = 0
    failed = 0

    if not st.session_state.get('session'):
        return {'success': False, 'error': 'Not authenticated', 'results': []}
            
    token = st.session_state.session.access_token
    supabase = get_authenticated_client(token)
    
    for athlete_data in athletes_data:
        # Check duplicate
        if check_duplicate_athlete(
            athlete_data['full_name'],
            athlete_data['date_of_birth'],
            dojo_id
        ):
            results.append({
                'name': athlete_data['full_name'],
                'success': False,
                'error': 'Duplicate - already exists'
            })
            failed += 1
            continue
        
        try:
            data = {
                'coach_id': user.id,
                'dojo_id': dojo_id,
                'full_name': athlete_data['full_name'].strip(),
                'date_of_birth': athlete_data['date_of_birth'],
                'gender': athlete_data['gender'],
                'belt_rank': athlete_data['belt_rank'],
                'weight_kg': athlete_data.get('weight_kg'),
                'competition_day': athlete_data['competition_day'],
                'kata_event': athlete_data.get('kata_event', False),
                'kumite_event': athlete_data.get('kumite_event', False)
            }
            
            result = supabase.table('athletes').insert(data).execute()
            
            if result.data:
                results.append({
                    'name': athlete_data['full_name'],
                    'success': True
                })
                successful += 1
            else:
                results.append({
                    'name': athlete_data['full_name'],
                    'success': False,
                    'error': 'Insert failed'
                })
                failed += 1
                
        except Exception as e:
            results.append({
                'name': athlete_data['full_name'],
                'success': False,
                'error': str(e)
            })
            failed += 1
    
    # Create bulk audit log
    if successful > 0:
        create_audit_log(
            action='BULK_REGISTER',
            athlete_data={
                'count': successful,
                'athletes': [r['name'] for r in results if r['success']]
            },
            coach_id=user.id,
            coach_email=user.email,
            dojo_name=dojo_name
        )
    
    return {
        'success': True,
        'successful': successful,
        'failed': failed,
        'results': results
    }


def get_athletes(
    search_query: str = None, 
    filter_day: str = None,
    filter_belt: str = None,
    all_athletes: bool = False
) -> List[Dict]:
    """
    Get athletes with optional filters.
    Respects RLS policies via authenticated client.
    """
    try:
        if not st.session_state.get('session'):
             return []
             
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        query = supabase.table('athletes')\
            .select('*, dojos(name), coaches(full_name, email)')
        
        # If not fetching all (admin), filter by coach
        # RLS should handle this, but explicit filter can be added for clarity/performance if needed
        # For now, rely on RLS for non-admin users.
        
        # Apply search filter
        if search_query:
            query = query.ilike('full_name', f'%{search_query}%')
        
        # Apply day filter
        if filter_day and filter_day != 'All':
            query = query.eq('competition_day', filter_day)
        
        # Apply belt filter
        if filter_belt and filter_belt != 'All':
            query = query.eq('belt_rank', filter_belt)
        
        # Order by creation date (newest first)
        query = query.order('created_at', desc=True)
        
        result = query.execute()
        return result.data if result.data else []
        
    except Exception as e:
        st.error(f"Error fetching athletes: {e}")
        return []


def update_athlete(athlete_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an athlete's information with audit logging.
    """
    user = get_current_user()
    coach = get_current_coach()
    
    if not user or not coach:
        return {'success': False, 'error': 'Not authenticated'}
    
    try:
        # Use authenticated client
        if not st.session_state.get('session'):
            return {'success': False, 'error': 'Not authenticated'}
            
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        # Add updated timestamp
        updated_data['updated_at'] = datetime.utcnow().isoformat()
        
        result = supabase.table('athletes')\
            .update(updated_data)\
            .eq('id', athlete_id)\
            .execute()
        
        if result.data:
            # Create audit log
            create_audit_log(
                action='UPDATE',
                athlete_data={
                    'athlete_id': athlete_id,
                    'changes': updated_data
                },
                coach_id=user.id,
                coach_email=user.email,
                dojo_name=coach.get('dojos', {}).get('name', 'Unknown')
            )
            
            return {'success': True, 'athlete': result.data[0]}
        else:
            return {'success': False, 'error': 'Update failed'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}


def delete_athlete(athlete_id: str, athlete_name: str) -> Dict[str, Any]:
    """
    Delete an athlete with audit logging.
    The audit log preserves the record even after deletion.
    """
    user = get_current_user()
    coach = get_current_coach()
    
    if not user or not coach:
        return {'success': False, 'error': 'Not authenticated'}
    
    try:
        if not st.session_state.get('session'):
            return {'success': False, 'error': 'Not authenticated'}
            
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        # First, get the athlete data for audit
        athlete_result = supabase.table('athletes')\
            .select('*')\
            .eq('id', athlete_id)\
            .execute()
        
        if not athlete_result.data:
            return {'success': False, 'error': 'Athlete not found'}
        
        athlete_data = athlete_result.data[0]
        
        # Delete the athlete
        result = supabase.table('athletes')\
            .delete()\
            .eq('id', athlete_id)\
            .execute()
        
        # Create audit log (preserves deleted data)
        create_audit_log(
            action='DELETE',
            athlete_data=athlete_data,
            coach_id=user.id,
            coach_email=user.email,
            dojo_name=coach.get('dojos', {}).get('name', 'Unknown')
        )
        
        return {'success': True}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_athlete_stats(all_dojos: bool = False) -> Dict[str, Any]:
    """Get statistics about registered athletes."""
    try:
        if not st.session_state.get('session'):
             return {'total': 0, 'by_day': {}, 'by_belt': {}, 'by_gender': {}, 'kata': 0, 'kumite': 0}
             
        token = st.session_state.session.access_token
        supabase = get_authenticated_client(token)
        
        # Base query
        result = supabase.table('athletes').select('*').execute()
        athletes = result.data or []
        
        stats = {
            'total': len(athletes),
            'by_day': {'Day 1': 0, 'Day 2': 0, 'Both': 0},
            'by_belt': {},
            'by_gender': {'Male': 0, 'Female': 0},
            'kata': 0,
            'kumite': 0
        }
        
        for athlete in athletes:
            # By day
            day = athlete.get('competition_day', 'Unknown')
            if day in stats['by_day']:
                stats['by_day'][day] += 1
            
            # By belt
            belt = athlete.get('belt_rank', 'Unknown')
            stats['by_belt'][belt] = stats['by_belt'].get(belt, 0) + 1
            
            # By gender
            gender = athlete.get('gender', 'Unknown')
            if gender in stats['by_gender']:
                stats['by_gender'][gender] += 1
            
            # Events
            if athlete.get('kata_event'):
                stats['kata'] += 1
            if athlete.get('kumite_event'):
                stats['kumite'] += 1
        
        return stats

    except Exception as e:
        # Return empty stats on error
        return {'total': 0, 'by_day': {}, 'by_belt': {}, 'by_gender': {}, 'kata': 0, 'kumite': 0}
