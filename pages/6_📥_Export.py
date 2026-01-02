"""
Export Page
Download athletes data as Excel
"""

import streamlit as st
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Export Data - EntryDesk",
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
from src.services.athlete_service import get_athletes, get_athlete_stats
from src.utils.excel_handler import export_athletes_to_excel

init_session_state()
require_auth()
require_onboarding()

# Render sidebar
render_sidebar()

coach = get_current_coach()
dojo_name = coach.get('dojos', {}).get('name', 'Unknown') if isinstance(coach.get('dojos'), dict) else 'Unknown'

# Header
st.markdown("""
    <h1 style="
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    ">📥 Export Data</h1>
    <p style="color: #64748b; margin-bottom: 1.5rem;">
        Download your athletes data in Excel format
    </p>
""", unsafe_allow_html=True)

# Get stats
stats = get_athlete_stats(all_dojos=False)
athletes = get_athletes()

# Summary Card
st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    ">
        <h3 style="color: #e2e8f0; margin: 0 0 1rem 0;">📊 Export Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
            <div>
                <p style="color: #6366f1; font-size: 1.5rem; font-weight: 700; margin: 0;">{stats['total']}</p>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Total Athletes</p>
            </div>
            <div>
                <p style="color: #06b6d4; font-size: 1.5rem; font-weight: 700; margin: 0;">{stats['by_day'].get('Day 1', 0)}</p>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Day 1</p>
            </div>
            <div>
                <p style="color: #f59e0b; font-size: 1.5rem; font-weight: 700; margin: 0;">{stats['by_day'].get('Day 2', 0)}</p>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Day 2</p>
            </div>
            <div>
                <p style="color: #10b981; font-size: 1.5rem; font-weight: 700; margin: 0;">{stats['by_day'].get('Both', 0)}</p>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Both Days</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if not athletes:
    st.info("📋 No athletes to export. Register some athletes first!")
    if st.button("➕ Register Athletes"):
        st.switch_page("pages/4_➕_Register.py")
else:
    # Export Options
    st.markdown("<h3 style='color: #e2e8f0;'>📁 Export Options</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style="
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
            ">
                <p style="font-size: 2rem; margin: 0;">📊</p>
                <p style="color: #e2e8f0; font-weight: 600; margin: 0.5rem 0;">Full Export</p>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0 0 1rem 0;">
                    All athletes with complete details
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{dojo_name.replace(' ', '_')}_athletes_{timestamp}.xlsx"
        
        excel_data = export_athletes_to_excel(athletes, filename)
        
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.markdown("""
            <div style="
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
            ">
                <p style="font-size: 2rem; margin: 0;">📄</p>
                <p style="color: #e2e8f0; font-weight: 600; margin: 0.5rem 0;">Quick Summary</p>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0 0 1rem 0;">
                    Names and basic info only
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Simple CSV export
        import pandas as pd
        simple_data = []
        for a in athletes:
            simple_data.append({
                'Name': a.get('full_name', ''),
                'Belt': a.get('belt_rank', ''),
                'Day': a.get('competition_day', ''),
                'Events': ('Kata ' if a.get('kata_event') else '') + ('Kumite' if a.get('kumite_event') else '')
            })
        
        df = pd.DataFrame(simple_data)
        csv_data = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{dojo_name.replace(' ', '_')}_summary_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Preview
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>👁️ Data Preview</h3>", unsafe_allow_html=True)
    
    import pandas as pd
    preview_data = []
    for a in athletes[:20]:
        preview_data.append({
            'Name': a.get('full_name', ''),
            'DOB': str(a.get('date_of_birth', ''))[:10],
            'Gender': a.get('gender', ''),
            'Belt': a.get('belt_rank', ''),
            'Weight': a.get('weight_kg', '-'),
            'Day': a.get('competition_day', ''),
            'Kata': '✓' if a.get('kata_event') else '-',
            'Kumite': '✓' if a.get('kumite_event') else '-'
        })
    
    st.dataframe(
        pd.DataFrame(preview_data),
        use_container_width=True,
        hide_index=True
    )
    
    if len(athletes) > 20:
        st.info(f"Showing first 20 of {len(athletes)} athletes. Download the full export for all data.")
