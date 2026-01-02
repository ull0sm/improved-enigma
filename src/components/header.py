"""
Header Component
Page header with tournament branding
"""

import streamlit as st
from src.services.config_service import get_tournament_name, get_time_until_deadline, is_registration_open


def render_header(title: str = None, subtitle: str = None, show_status: bool = True):
    """
    Render the page header with optional tournament info.
    
    Args:
        title: Page title (defaults to tournament name)
        subtitle: Optional subtitle
        show_status: Whether to show registration status
    """
    tournament_name = get_tournament_name()
    display_title = title or tournament_name
    
    # Header container
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
            <h1 style="
                font-size: 1.75rem;
                font-weight: 700;
                margin: 0;
                background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{display_title}</h1>
        """, unsafe_allow_html=True)
        
        if subtitle:
            st.markdown(f"""
                <p style="color: #64748b; margin-top: 0.25rem; font-size: 0.9rem;">
                    {subtitle}
                </p>
            """, unsafe_allow_html=True)
    
    with col2:
        if show_status:
            render_registration_status()
    
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)


def render_registration_status():
    """Render the registration status badge."""
    is_open = is_registration_open()
    time_remaining = get_time_until_deadline()
    
    if is_open:
        status_color = "#10b981"  # Green
        status_bg = "rgba(16, 185, 129, 0.1)"
        status_text = "Registration Open"
        icon = "✅"
    else:
        status_color = "#ef4444"  # Red
        status_bg = "rgba(239, 68, 68, 0.1)"
        status_text = "Registration Closed"
        icon = "🔒"
    
    st.markdown(f"""
        <div style="
            background: {status_bg};
            border: 1px solid {status_color};
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            text-align: center;
        ">
            <p style="color: {status_color}; font-weight: 600; margin: 0; font-size: 0.8rem;">
                {icon} {status_text}
            </p>
            {f'<p style="color: #64748b; font-size: 0.7rem; margin: 0.25rem 0 0 0;">{time_remaining}</p>' if time_remaining and is_open else ''}
        </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats: dict):
    """
    Render a row of stat cards.
    
    Args:
        stats: Dict with format {'label': value, ...} or list of dicts
    """
    if isinstance(stats, dict):
        stats_list = [{'label': k, 'value': v} for k, v in stats.items()]
    else:
        stats_list = stats
    
    cols = st.columns(len(stats_list))
    
    for col, stat in zip(cols, stats_list):
        with col:
            label = stat.get('label', '')
            value = stat.get('value', 0)
            icon = stat.get('icon', '')
            delta = stat.get('delta', None)
            
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
                        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        margin: 0;
                    ">{icon} {value}</p>
                    <p style="
                        font-size: 0.75rem;
                        color: #94a3b8;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                        margin: 0.25rem 0 0 0;
                    ">{label}</p>
                    {f'<p style="font-size: 0.7rem; color: #10b981; margin: 0.25rem 0 0 0;">{delta}</p>' if delta else ''}
                </div>
            """, unsafe_allow_html=True)
