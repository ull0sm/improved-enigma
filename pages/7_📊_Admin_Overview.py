"""
Admin Overview Page
Global statistics across all dojos
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Admin Overview - EntryDesk",
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
from src.services.athlete_service import get_athletes, get_athlete_stats
from src.services.config_service import get_tournament_name
from src.auth.supabase_client import get_supabase_client

init_session_state()
require_auth()
require_onboarding()
require_admin()

# Render sidebar
render_sidebar()

# Header
tournament_name = get_tournament_name()
st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <p style="color: #8b5cf6; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 0;">
            🔐 Admin Dashboard
        </p>
        <h1 style="
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.25rem 0 0 0;
        ">📊 Global Overview</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            {tournament_name} - All Dojos Statistics
        </p>
    </div>
""", unsafe_allow_html=True)

# Global Stats
stats = get_athlete_stats(all_dojos=True)

# Main stats row
col1, col2, col3, col4, col5 = st.columns(5)

stats_config = [
    (col1, stats['total'], "Total Athletes", "#6366f1", "#8b5cf6"),
    (col2, stats['by_day'].get('Day 1', 0), "Day 1", "#06b6d4", "#0ea5e9"),
    (col3, stats['by_day'].get('Day 2', 0), "Day 2", "#f59e0b", "#ef4444"),
    (col4, stats['by_day'].get('Both', 0), "Both Days", "#10b981", "#06b6d4"),
    (col5, stats['kata'], "Kata Events", "#ec4899", "#8b5cf6"),
]

for col, value, label, color1, color2 in stats_config:
    with col:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.25rem;
                text-align: center;
            ">
                <p style="
                    font-size: 2rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, {color1} 0%, {color2} 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin: 0;
                ">{value}</p>
                <p style="
                    font-size: 0.7rem;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin: 0.25rem 0 0 0;
                ">{label}</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Fetch dojo breakdown
def get_dojo_breakdown():
    """Get athlete count per dojo."""
    try:
        supabase = get_supabase_client()
        # Get all athletes with dojo info
        result = supabase.table('athletes')\
            .select('dojo_id, dojos(name)')\
            .execute()
        
        if not result.data:
            return {}
        
        breakdown = {}
        for athlete in result.data:
            dojo = athlete.get('dojos', {})
            dojo_name = dojo.get('name', 'Unknown') if isinstance(dojo, dict) else 'Unknown'
            breakdown[dojo_name] = breakdown.get(dojo_name, 0) + 1
        
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))
    except Exception as e:
        st.error(f"Error: {e}")
        return {}

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='color: #e2e8f0;'>🏢 Athletes by Dojo</h3>", unsafe_allow_html=True)
    
    dojo_breakdown = get_dojo_breakdown()
    
    if dojo_breakdown:
        for dojo_name, count in list(dojo_breakdown.items())[:10]:
            percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.5rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="color: #e2e8f0;">{dojo_name}</span>
                    <div>
                        <span style="color: #6366f1; font-weight: 600;">{count}</span>
                        <span style="color: #64748b; font-size: 0.8rem; margin-left: 0.5rem;">({percentage:.1f}%)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        if len(dojo_breakdown) > 10:
            st.info(f"... and {len(dojo_breakdown) - 10} more dojos")
    else:
        st.info("No dojo data available")

with col2:
    st.markdown("<h3 style='color: #e2e8f0;'>🥋 Belt Distribution</h3>", unsafe_allow_html=True)
    
    if stats['by_belt']:
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
        
        for belt, count in sorted(stats['by_belt'].items(), key=lambda x: x[1], reverse=True):
            color = belt_colors.get(belt, '#6366f1')
            percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.03);
                    border-left: 3px solid {color};
                    border-radius: 0 8px 8px 0;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.5rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="color: #e2e8f0;">{belt}</span>
                    <div>
                        <span style="color: {color}; font-weight: 600;">{count}</span>
                        <span style="color: #64748b; font-size: 0.8rem; margin-left: 0.5rem;">({percentage:.1f}%)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No belt data available")

st.markdown("<br>", unsafe_allow_html=True)

# Gender breakdown
st.markdown("<h3 style='color: #e2e8f0;'>👥 Gender Distribution</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

male_count = stats['by_gender'].get('Male', 0)
female_count = stats['by_gender'].get('Female', 0)
total = male_count + female_count

with col1:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <p style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin: 0;">{male_count}</p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Male ({(male_count/total*100) if total > 0 else 0:.1f}%)</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(167, 139, 250, 0.1) 100%);
            border: 1px solid rgba(236, 72, 153, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <p style="font-size: 2rem; font-weight: 700; color: #ec4899; margin: 0;">{female_count}</p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Female ({(female_count/total*100) if total > 0 else 0:.1f}%)</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <p style="font-size: 2rem; font-weight: 700; color: #10b981; margin: 0;">{stats['kumite']}</p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Kumite Events</p>
        </div>
    """, unsafe_allow_html=True)

# Quick links
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #e2e8f0;'>⚡ Quick Admin Actions</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("👥 View All Athletes", use_container_width=True):
        st.switch_page("pages/8_👥_All_Athletes.py")

with col2:
    if st.button("📧 Manage Access", use_container_width=True):
        st.switch_page("pages/9_📧_Manage_Access.py")

with col3:
    if st.button("⚙️ Tournament Settings", use_container_width=True):
        st.switch_page("pages/10_⚙️_Settings.py")

with col4:
    if st.button("📜 Audit Logs", use_container_width=True):
        st.switch_page("pages/11_📜_Audit_Logs.py")
