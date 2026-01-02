"""
Settings Page (Admin)
Tournament configuration management
"""

import streamlit as st
import os
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="Settings - EntryDesk",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

from src.auth.session import init_session_state, require_auth, require_onboarding, require_admin
from src.components.sidebar import render_sidebar
from src.services.config_service import (
    get_all_config, 
    update_config, 
    get_tournament_name,
    get_tournament_dates,
    is_registration_open,
    get_registration_deadline
)

init_session_state()
require_auth()
require_onboarding()
require_admin()

# Render sidebar
render_sidebar()

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
        ">⚙️ Tournament Settings</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            Configure tournament name, dates, and registration settings
        </p>
    </div>
""", unsafe_allow_html=True)

# Current config
current_name = get_tournament_name()
current_dates = get_tournament_dates()
reg_open = is_registration_open()
deadline = get_registration_deadline()

# Registration Status Card
st.markdown(f"""
    <div style="
        background: {'rgba(16, 185, 129, 0.1)' if reg_open else 'rgba(239, 68, 68, 0.1)'};
        border: 1px solid {'rgba(16, 185, 129, 0.3)' if reg_open else 'rgba(239, 68, 68, 0.3)'};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <p style="color: {'#10b981' if reg_open else '#ef4444'}; font-weight: 600; margin: 0;">
                {'✅ Registration is OPEN' if reg_open else '🔒 Registration is CLOSED'}
            </p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                {f"Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}" if deadline else 'No deadline set'}
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Settings Tabs
tab_general, tab_dates, tab_registration = st.tabs(["📝 General", "📅 Dates", "🎫 Registration"])

with tab_general:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>Tournament Information</h3>", unsafe_allow_html=True)
    
    with st.form("general_settings"):
        tournament_name = st.text_input(
            "Tournament Name",
            value=current_name,
            help="This will be displayed throughout the application"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("Save Changes", use_container_width=True):
            result = update_config('tournament_name', tournament_name)
            if result['success']:
                st.success("✅ Tournament name updated!")
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")

with tab_dates:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>Tournament Dates</h3>", unsafe_allow_html=True)
    
    with st.form("date_settings"):
        col1, col2 = st.columns(2)
        
        # Parse existing dates
        day1_str = current_dates.get('day1', '')
        day2_str = current_dates.get('day2', '')
        
        try:
            day1_date = datetime.strptime(day1_str, '%Y-%m-%d').date() if day1_str else None
        except:
            day1_date = None
        
        try:
            day2_date = datetime.strptime(day2_str, '%Y-%m-%d').date() if day2_str else None
        except:
            day2_date = None
        
        with col1:
            new_day1 = st.date_input(
                "Day 1",
                value=day1_date,
                help="First day of the tournament"
            )
        
        with col2:
            new_day2 = st.date_input(
                "Day 2",
                value=day2_date,
                help="Second day of the tournament"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("Save Dates", use_container_width=True):
            new_dates = {
                'day1': new_day1.strftime('%Y-%m-%d') if new_day1 else '',
                'day2': new_day2.strftime('%Y-%m-%d') if new_day2 else ''
            }
            result = update_config('tournament_dates', new_dates)
            if result['success']:
                st.success("✅ Tournament dates updated!")
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")

with tab_registration:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>Registration Control</h3>", unsafe_allow_html=True)
    
    # Quick toggle
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 1rem;
            ">
                <p style="color: #e2e8f0; font-weight: 500; margin: 0;">Registration Status</p>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                    Toggle registration on or off immediately
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if reg_open:
            if st.button("🔒 Close Now", use_container_width=True, type="primary"):
                result = update_config('registration_open', False)
                if result['success']:
                    st.success("Registration closed!")
                    st.rerun()
        else:
            if st.button("✅ Open Now", use_container_width=True, type="primary"):
                result = update_config('registration_open', True)
                if result['success']:
                    st.success("Registration opened!")
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Deadline form
    with st.form("deadline_settings"):
        st.markdown("<h4 style='color: #e2e8f0;'>Registration Deadline</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Parse existing deadline
        deadline_date = deadline.date() if deadline else None
        deadline_time = deadline.time() if deadline else None
        
        with col1:
            new_deadline_date = st.date_input(
                "Date",
                value=deadline_date,
                help="Last day to register"
            )
        
        with col2:
            new_deadline_time = st.time_input(
                "Time",
                value=deadline_time or datetime.strptime("23:59", "%H:%M").time(),
                help="Cutoff time"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("Save Deadline", use_container_width=True):
            if new_deadline_date:
                new_deadline = datetime.combine(new_deadline_date, new_deadline_time)
                result = update_config('registration_deadline', new_deadline.isoformat() + 'Z')
                if result['success']:
                    st.success("✅ Deadline updated!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("Please select a date")

st.markdown("<br>", unsafe_allow_html=True)

# Current config summary
with st.expander("📋 Current Configuration"):
    config = get_all_config()
    
    for key, value in config.items():
        st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            ">
                <span style="color: #64748b;">{key}</span>
                <span style="color: #e2e8f0; font-family: monospace;">{value}</span>
            </div>
        """, unsafe_allow_html=True)
