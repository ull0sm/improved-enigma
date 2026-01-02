"""
All Athletes Page (Admin)
View all athletes across all dojos
"""

import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="All Athletes - EntryDesk",
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
from src.services.athlete_service import get_athletes
from src.utils.validators import BELT_RANKS, COMPETITION_DAYS
from src.utils.excel_handler import export_athletes_to_excel

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
            🔐 Admin View
        </p>
        <h1 style="
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.25rem 0 0 0;
        ">👥 All Athletes</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            View athletes from all registered dojos
        </p>
    </div>
""", unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    search_query = st.text_input(
        "🔍 Search",
        placeholder="Search by name...",
        label_visibility="collapsed"
    )

with col2:
    filter_day = st.selectbox(
        "Day",
        options=["All Days"] + COMPETITION_DAYS,
        label_visibility="collapsed"
    )

with col3:
    filter_belt = st.selectbox(
        "Belt",
        options=["All Belts"] + BELT_RANKS,
        label_visibility="collapsed"
    )

with col4:
    # Get unique dojos
    all_athletes = get_athletes(all_athletes=True)
    dojos = set()
    for a in all_athletes:
        dojo = a.get('dojos', {})
        if isinstance(dojo, dict) and dojo.get('name'):
            dojos.add(dojo.get('name'))
    
    filter_dojo = st.selectbox(
        "Dojo",
        options=["All Dojos"] + sorted(list(dojos)),
        label_visibility="collapsed"
    )

# Fetch athletes with filters
athletes = get_athletes(
    search_query=search_query if search_query else None,
    filter_day=filter_day if filter_day != "All Days" else None,
    filter_belt=filter_belt if filter_belt != "All Belts" else None,
    all_athletes=True
)

# Apply dojo filter (client-side)
if filter_dojo != "All Dojos":
    athletes = [
        a for a in athletes 
        if isinstance(a.get('dojos'), dict) and a.get('dojos', {}).get('name') == filter_dojo
    ]

# Count and Export row
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"""
        <p style="color: #64748b; font-size: 0.85rem; margin: 1rem 0;">
            Showing <strong style="color: #8b5cf6;">{len(athletes)}</strong> athletes from <strong style="color: #06b6d4;">{len(dojos)}</strong> dojos
        </p>
    """, unsafe_allow_html=True)

with col2:
    if athletes:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        excel_data = export_athletes_to_excel(athletes, f"all_athletes_{timestamp}")
        
        st.download_button(
            label="📥 Export All",
            data=excel_data,
            file_name=f"all_athletes_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

if not athletes:
    st.info("📋 No athletes found matching your filters.")
else:
    # Create DataFrame for display
    display_data = []
    for a in athletes:
        dojo = a.get('dojos', {})
        coach = a.get('coaches', {})
        
        events = []
        if a.get('kata_event'):
            events.append('Kata')
        if a.get('kumite_event'):
            events.append('Kumite')
        
        display_data.append({
            'Name': a.get('full_name', ''),
            'DOB': str(a.get('date_of_birth', ''))[:10],
            'Gender': a.get('gender', ''),
            'Belt': a.get('belt_rank', ''),
            'Weight': a.get('weight_kg', '-'),
            'Day': a.get('competition_day', ''),
            'Events': ', '.join(events),
            'Dojo': dojo.get('name', '') if isinstance(dojo, dict) else '',
            'Coach': coach.get('full_name', '') if isinstance(coach, dict) else '',
            'Registered': str(a.get('created_at', ''))[:10]
        })
    
    df = pd.DataFrame(display_data)
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=500
    )
