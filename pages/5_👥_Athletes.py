"""
My Athletes Page
View, search, edit, and delete registered athletes
"""

import streamlit as st
import os
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="My Athletes - EntryDesk",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

from src.auth.session import init_session_state, require_auth, require_onboarding, get_current_coach
from src.components.sidebar import render_sidebar
from src.services.athlete_service import get_athletes, update_athlete, delete_athlete
from src.utils.validators import BELT_RANKS, GENDERS, COMPETITION_DAYS

init_session_state()
require_auth()
require_onboarding()

# Render sidebar
render_sidebar()

# Initialize session state for editing
if 'editing_athlete' not in st.session_state:
    st.session_state.editing_athlete = None
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

coach = get_current_coach()

# Header
st.markdown("""
    <h1 style="
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    ">👥 My Athletes</h1>
    <p style="color: #64748b; margin-bottom: 1.5rem;">
        Manage your registered athletes
    </p>
""", unsafe_allow_html=True)

# Filters
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input(
        "🔍 Search",
        placeholder="Search by name...",
        label_visibility="collapsed"
    )

with col2:
    filter_day = st.selectbox(
        "Filter by Day",
        options=["All"] + COMPETITION_DAYS,
        label_visibility="collapsed"
    )

with col3:
    filter_belt = st.selectbox(
        "Filter by Belt",
        options=["All"] + BELT_RANKS,
        label_visibility="collapsed"
    )

# Fetch athletes
athletes = get_athletes(
    search_query=search_query if search_query else None,
    filter_day=filter_day if filter_day != "All" else None,
    filter_belt=filter_belt if filter_belt != "All" else None
)

# Count display
st.markdown(f"""
    <p style="color: #64748b; font-size: 0.85rem; margin: 1rem 0;">
        Showing <strong style="color: #8b5cf6;">{len(athletes)}</strong> athletes
    </p>
""", unsafe_allow_html=True)

if not athletes:
    st.info("📋 No athletes found. Register some athletes to see them here!")
    if st.button("➕ Register Athletes"):
        st.switch_page("pages/4_➕_Register.py")
else:
    # Edit Modal (using expander as a workaround)
    if st.session_state.editing_athlete:
        athlete = st.session_state.editing_athlete
        
        st.markdown("""
            <div style="
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            ">
        """, unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='color: #e2e8f0; margin-top: 0;'>✏️ Edit: {athlete.get('full_name')}</h3>", unsafe_allow_html=True)
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_belt = st.selectbox(
                    "Belt Rank",
                    options=BELT_RANKS,
                    index=BELT_RANKS.index(athlete.get('belt_rank')) if athlete.get('belt_rank') in BELT_RANKS else 0
                )
                
                edit_weight = st.number_input(
                    "Weight (kg)",
                    value=float(athlete.get('weight_kg') or 0),
                    min_value=0.0,
                    max_value=200.0,
                    step=0.5
                )
            
            with col2:
                edit_day = st.selectbox(
                    "Competition Day",
                    options=COMPETITION_DAYS,
                    index=COMPETITION_DAYS.index(athlete.get('competition_day')) if athlete.get('competition_day') in COMPETITION_DAYS else 0
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                edit_kata = st.checkbox("🥋 Kata", value=athlete.get('kata_event', False))
            with col2:
                edit_kumite = st.checkbox("👊 Kumite", value=athlete.get('kumite_event', False))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes", use_container_width=True, type="primary"):
                    updated_data = {
                        'belt_rank': edit_belt,
                        'weight_kg': edit_weight if edit_weight > 0 else None,
                        'competition_day': edit_day,
                        'kata_event': edit_kata,
                        'kumite_event': edit_kumite
                    }
                    
                    result = update_athlete(athlete['id'], updated_data)
                    
                    if result['success']:
                        st.success("✅ Athlete updated successfully!")
                        st.session_state.editing_athlete = None
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.editing_athlete = None
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Delete Confirmation
    if st.session_state.delete_confirm:
        athlete = st.session_state.delete_confirm
        
        st.markdown("""
            <div style="
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            ">
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <h3 style='color: #ef4444; margin-top: 0;'>🗑️ Confirm Delete</h3>
            <p style="color: #e2e8f0;">Are you sure you want to delete <strong>{athlete.get('full_name')}</strong>?</p>
            <p style="color: #64748b; font-size: 0.85rem;">This action cannot be undone, but the record will be preserved in audit logs.</p>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
                result = delete_athlete(athlete['id'], athlete.get('full_name', ''))
                
                if result['success']:
                    st.success("✅ Athlete deleted successfully")
                    st.session_state.delete_confirm = None
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.delete_confirm = None
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Athletes Table
    for athlete in athletes:
        events = []
        if athlete.get('kata_event'):
            events.append('🥋 Kata')
        if athlete.get('kumite_event'):
            events.append('👊 Kumite')
        events_str = ' • '.join(events) if events else 'No events'
        
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1.5, 1])
            
            with col1:
                st.markdown(f"""
                    <p style="font-weight: 600; color: #e2e8f0; margin: 0.5rem 0;">
                        {athlete.get('full_name', 'Unknown')}
                    </p>
                    <p style="color: #64748b; font-size: 0.8rem; margin: 0;">
                        DOB: {str(athlete.get('date_of_birth', ''))[:10]}
                    </p>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <p style="color: #94a3b8; margin: 0.5rem 0; font-size: 0.9rem;">
                        {athlete.get('gender', '-')}
                    </p>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <p style="color: #94a3b8; margin: 0.5rem 0; font-size: 0.9rem;">
                        {athlete.get('belt_rank', '-')}
                    </p>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <p style="color: #94a3b8; margin: 0.5rem 0; font-size: 0.9rem;">
                        {athlete.get('competition_day', '-')}
                    </p>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                    <p style="color: #64748b; margin: 0.5rem 0; font-size: 0.8rem;">
                        {events_str}
                    </p>
                """, unsafe_allow_html=True)
            
            with col6:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"edit_{athlete['id']}", help="Edit"):
                        st.session_state.editing_athlete = athlete
                        st.session_state.delete_confirm = None
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"del_{athlete['id']}", help="Delete"):
                        st.session_state.delete_confirm = athlete
                        st.session_state.editing_athlete = None
                        st.rerun()
            
            st.markdown("<hr style='margin: 0.25rem 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
