"""
Audit Logs Page (Admin)
View immutable audit trail of all data changes
"""

import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Audit Logs - EntryDesk",
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
from src.services.audit_service import get_audit_logs, get_audit_summary, format_audit_log_for_display

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
        ">📜 Audit Logs</h1>
        <p style="color: #64748b; margin-top: 0.5rem;">
            Immutable record of all data changes - the "Black Box"
        </p>
    </div>
""", unsafe_allow_html=True)

# Info banner
st.markdown("""
    <div style="
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <p style="color: #f59e0b; font-weight: 500; margin: 0;">
            🔒 Immutable Records
        </p>
        <p style="color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
            These logs cannot be edited or deleted. Even if an athlete is removed from the main database, 
            their record is preserved here for audit purposes.
        </p>
    </div>
""", unsafe_allow_html=True)

# Summary stats
summary = get_audit_summary()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #6366f1; font-size: 1.75rem; font-weight: 700; margin: 0;">
                {summary.get('total_entries', 0)}
            </p>
            <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Total Entries</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    register_count = summary.get('by_action', {}).get('REGISTER', 0)
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #10b981; font-size: 1.75rem; font-weight: 700; margin: 0;">
                {register_count}
            </p>
            <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Registrations</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    update_count = summary.get('by_action', {}).get('UPDATE', 0)
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #f59e0b; font-size: 1.75rem; font-weight: 700; margin: 0;">
                {update_count}
            </p>
            <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Updates</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    delete_count = summary.get('by_action', {}).get('DELETE', 0)
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #252542 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <p style="color: #ef4444; font-size: 1.75rem; font-weight: 700; margin: 0;">
                {delete_count}
            </p>
            <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Deletions</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Filters
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    action_filter = st.selectbox(
        "Filter by Action",
        options=["All", "REGISTER", "UPDATE", "DELETE", "BULK_REGISTER"],
        label_visibility="collapsed"
    )

with col2:
    coach_filter = st.text_input(
        "Search Coach",
        placeholder="Filter by coach email...",
        label_visibility="collapsed"
    )

with col3:
    dojo_filter = st.text_input(
        "Search Dojo",
        placeholder="Filter by dojo name...",
        label_visibility="collapsed"
    )

# Fetch logs
logs = get_audit_logs(
    limit=200,
    action_filter=action_filter if action_filter != "All" else None,
    coach_filter=coach_filter if coach_filter else None,
    dojo_filter=dojo_filter if dojo_filter else None
)

st.markdown(f"""
    <p style="color: #64748b; font-size: 0.85rem; margin: 1rem 0;">
        Showing <strong style="color: #8b5cf6;">{len(logs)}</strong> log entries
    </p>
""", unsafe_allow_html=True)

if not logs:
    st.info("📋 No audit logs found matching your filters.")
else:
    # Display logs
    for log in logs:
        formatted = format_audit_log_for_display(log)
        
        # Color based on action
        action_colors = {
            'REGISTER': ('#10b981', 'rgba(16, 185, 129, 0.1)'),
            'UPDATE': ('#f59e0b', 'rgba(245, 158, 11, 0.1)'),
            'DELETE': ('#ef4444', 'rgba(239, 68, 68, 0.1)'),
            'BULK_REGISTER': ('#6366f1', 'rgba(99, 102, 241, 0.1)')
        }
        
        action = log.get('action', 'UNKNOWN')
        color, bg_color = action_colors.get(action, ('#64748b', 'rgba(100, 116, 139, 0.1)'))
        
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
            
            with col1:
                st.markdown(f"""
                    <div style="padding: 0.5rem 0;">
                        <span style="
                            background: {bg_color};
                            color: {color};
                            padding: 0.25rem 0.5rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            font-weight: 600;
                        ">{formatted['action']}</span>
                        <p style="color: #e2e8f0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                            {formatted['description']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style="padding: 0.5rem 0;">
                        <p style="color: #64748b; font-size: 0.8rem; margin: 0;">
                            👤 {formatted['coach']}
                        </p>
                        <p style="color: #64748b; font-size: 0.8rem; margin: 0.25rem 0 0 0;">
                            🏢 {formatted['dojo']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <p style="color: #64748b; font-size: 0.8rem; margin: 0.5rem 0;">
                        🕐 {formatted['timestamp']}
                    </p>
                """, unsafe_allow_html=True)
            
            with col4:
                with st.expander("📄"):
                    st.json(formatted['raw_data'])
            
            st.markdown("<hr style='margin: 0.25rem 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

# Export option
if logs:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prepare export data
    export_data = []
    for log in logs:
        export_data.append({
            'Timestamp': log.get('created_at', ''),
            'Action': log.get('action', ''),
            'Coach Email': log.get('coach_email', ''),
            'Dojo': log.get('dojo_name', ''),
            'Data': str(log.get('athlete_data', {}))
        })
    
    df = pd.DataFrame(export_data)
    csv_data = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Export Audit Logs (CSV)",
        data=csv_data,
        file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
