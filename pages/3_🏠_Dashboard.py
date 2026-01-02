"""
Dashboard Page
Main coach dashboard with stats and quick actions
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Dashboard - EntryDesk",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

from src.auth.session import init_session_state, require_auth, require_onboarding, get_current_coach, is_admin
from src.components.sidebar import render_sidebar
from src.components.header import render_header, render_stat_cards
from src.services.config_service import get_tournament_name, get_tournament_dates, is_registration_open, get_time_until_deadline
from src.services.athlete_service import get_athlete_stats

init_session_state()
require_auth()
require_onboarding()

# Render sidebar
render_sidebar()

# Get coach info
coach = get_current_coach()
dojo_name = coach.get('dojos', {}).get('name', 'Your Dojo') if isinstance(coach.get('dojos'), dict) else 'Your Dojo'

# Page Header
tournament_name = get_tournament_name()
tournament_dates = get_tournament_dates()

st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        ">{tournament_name}</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            Welcome back, <strong style="color: #8b5cf6;">{coach.get('full_name', 'Coach')}</strong> from <strong style="color: #06b6d4;">{dojo_name}</strong>
        </p>
    </div>
""", unsafe_allow_html=True)

# Registration Status Banner
is_open = is_registration_open()
time_remaining = get_time_until_deadline()

if is_open:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <p style="color: #10b981; font-weight: 600; margin: 0; font-size: 1rem;">
                    ✅ Registration is Open
                </p>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                    {time_remaining if time_remaining else 'Register your athletes now'}
                </p>
            </div>
            <div style="color: #10b981; font-size: 1.5rem;">🏆</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
        ">
            <p style="color: #ef4444; font-weight: 600; margin: 0;">
                🔒 Registration is Closed
            </p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                The registration window has ended. Contact the administrator for assistance.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Stats Cards
stats = get_athlete_stats(all_dojos=False)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        ">
            <p style="
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">{stats['total']}</p>
            <p style="
                font-size: 0.75rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin: 0.25rem 0 0 0;
            ">Total Athletes</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        ">
            <p style="
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">{stats['by_day'].get('Day 1', 0)}</p>
            <p style="
                font-size: 0.75rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin: 0.25rem 0 0 0;
            ">Day 1</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        ">
            <p style="
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">{stats['by_day'].get('Day 2', 0)}</p>
            <p style="
                font-size: 0.75rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin: 0.25rem 0 0 0;
            ">Day 2</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        ">
            <p style="
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">{stats['by_day'].get('Both', 0)}</p>
            <p style="
                font-size: 0.75rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin: 0.25rem 0 0 0;
            ">Both Days</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick Actions
st.markdown("<h3 style='color: #e2e8f0;'>⚡ Quick Actions</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style="
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <p style="font-size: 2rem; margin: 0;">➕</p>
            <p style="color: #e2e8f0; font-weight: 600; margin: 0.5rem 0 0.25rem 0;">Register Athletes</p>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Add single or bulk entries</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Register Now", key="quick_register", use_container_width=True):
        st.switch_page("pages/4_➕_Register.py")

with col2:
    st.markdown("""
        <div style="
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <p style="font-size: 2rem; margin: 0;">👥</p>
            <p style="color: #e2e8f0; font-weight: 600; margin: 0.5rem 0 0.25rem 0;">View Athletes</p>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Manage your registrations</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View All", key="quick_view", use_container_width=True):
        st.switch_page("pages/5_👥_Athletes.py")

with col3:
    st.markdown("""
        <div style="
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <p style="font-size: 2rem; margin: 0;">📥</p>
            <p style="color: #e2e8f0; font-weight: 600; margin: 0.5rem 0 0.25rem 0;">Export Data</p>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Download as Excel</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Export", key="quick_export", use_container_width=True):
        st.switch_page("pages/6_📥_Export.py")

st.markdown("<br>", unsafe_allow_html=True)

# Belt Distribution (if athletes exist)
if stats['total'] > 0:
    st.markdown("<h3 style='color: #e2e8f0;'>🥋 Belt Distribution</h3>", unsafe_allow_html=True)
    
    belt_cols = st.columns(len(stats['by_belt']) if stats['by_belt'] else 1)
    
    for i, (belt, count) in enumerate(sorted(stats['by_belt'].items())):
        with belt_cols[i % len(belt_cols)]:
            # Belt color mapping
            belt_colors = {
                'White': '#ffffff',
                'Yellow': '#fbbf24',
                'Orange': '#f97316',
                'Green': '#22c55e',
                'Blue': '#3b82f6',
                'Purple': '#a855f7',
                'Brown': '#92400e',
            }
            color = belt_colors.get(belt, '#6366f1')
            
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-left: 3px solid {color};
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.5rem;
                ">
                    <p style="color: #e2e8f0; font-weight: 600; margin: 0;">{belt}</p>
                    <p style="color: #64748b; font-size: 1.25rem; font-weight: 700; margin: 0;">{count}</p>
                </div>
            """, unsafe_allow_html=True)

# Admin Quick Access
if is_admin():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 1.25rem;
        ">
            <p style="color: #8b5cf6; font-weight: 600; margin: 0 0 0.5rem 0;">
                🔐 Admin Access
            </p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
                You have administrator privileges. Access global stats and settings from the sidebar.
            </p>
        </div>
    """, unsafe_allow_html=True)
