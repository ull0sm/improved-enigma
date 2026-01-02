"""
Registration Page
Single and bulk athlete registration with validation
"""

import streamlit as st
import os
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Register Athletes - EntryDesk",
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
from src.services.athlete_service import register_athlete, bulk_register_athletes, check_duplicate_athlete
from src.services.config_service import is_registration_open
from src.utils.validators import BELT_RANKS, GENDERS, COMPETITION_DAYS, validate_athlete_data
from src.utils.excel_handler import parse_excel_file, generate_excel_template

init_session_state()
require_auth()
require_onboarding()

# Render sidebar
render_sidebar()

coach = get_current_coach()
dojo_id = coach.get('dojo_id') if coach else None

# Header
st.markdown("""
    <h1 style="
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    ">➕ Register Athletes</h1>
    <p style="color: #64748b; margin-bottom: 1.5rem;">
        Add athletes to your dojo's tournament roster
    </p>
""", unsafe_allow_html=True)

# Check if registration is open
if not is_registration_open():
    st.error("🔒 Registration is currently closed")
    st.info("The registration window has ended. Please contact the administrator for assistance.")
    st.stop()

# Registration Methods Tabs
tab_single, tab_bulk = st.tabs(["📝 Single Entry", "📊 Bulk Upload"])

# ===== SINGLE ENTRY TAB =====
with tab_single:
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("single_registration_form", clear_on_submit=True):
        st.markdown("<h3 style='color: #e2e8f0; margin-top: 0;'>Athlete Details</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name *",
                placeholder="Enter athlete's full name"
            )
            
            date_of_birth = st.date_input(
                "Date of Birth *",
                value=None,
                min_value=date(1920, 1, 1),
                max_value=date.today(),
                format="YYYY-MM-DD"
            )
            
            gender = st.selectbox(
                "Gender *",
                options=[""] + GENDERS,
                format_func=lambda x: "Select gender" if x == "" else x
            )
        
        with col2:
            belt_rank = st.selectbox(
                "Belt Rank *",
                options=[""] + BELT_RANKS,
                format_func=lambda x: "Select belt rank" if x == "" else x
            )
            
            weight_kg = st.number_input(
                "Weight (kg)",
                min_value=10.0,
                max_value=200.0,
                value=None,
                step=0.5,
                placeholder="Optional"
            )
            
            competition_day = st.selectbox(
                "Competition Day *",
                options=[""] + COMPETITION_DAYS,
                format_func=lambda x: "Select day" if x == "" else x
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #e2e8f0;'>Events</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            kata_event = st.checkbox("🥋 Kata", value=True)
        with col2:
            kumite_event = st.checkbox("👊 Kumite", value=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Register Athlete", use_container_width=True)
        
        if submitted:
            # Build data
            athlete_data = {
                'full_name': full_name,
                'date_of_birth': str(date_of_birth) if date_of_birth else None,
                'gender': gender,
                'belt_rank': belt_rank,
                'weight_kg': weight_kg,
                'competition_day': competition_day,
                'kata_event': kata_event,
                'kumite_event': kumite_event
            }
            
            # Validate
            is_valid, errors = validate_athlete_data(athlete_data)
            
            if not is_valid:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Check for duplicate
                if check_duplicate_athlete(full_name, str(date_of_birth), dojo_id):
                    st.error(f"⚠️ An athlete named '{full_name}' with this date of birth already exists in your dojo.")
                else:
                    with st.spinner("Registering athlete..."):
                        result = register_athlete(athlete_data)
                        
                        if result['success']:
                            st.success(f"✅ Successfully registered: **{full_name}**")
                            st.balloons()
                        else:
                            st.error(f"❌ {result['error']}")


# ===== BULK UPLOAD TAB =====
with tab_bulk:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download template
    st.markdown("""
        <div style="
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <p style="color: #e2e8f0; font-weight: 500; margin: 0 0 0.5rem 0;">
                📄 Download Template
            </p>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
                Use our Excel template to ensure your data is formatted correctly.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    template_data = generate_excel_template()
    st.download_button(
        label="📥 Download Excel Template",
        data=template_data,
        file_name="athlete_registration_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # File upload
    st.markdown("<h3 style='color: #e2e8f0;'>Upload Your File</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with athlete data"
    )
    
    if uploaded_file:
        with st.spinner("Processing file..."):
            success, athletes, errors = parse_excel_file(uploaded_file)
        
        if errors:
            with st.expander(f"⚠️ {len(errors)} Validation Errors", expanded=True):
                for error in errors[:20]:  # Show first 20 errors
                    st.warning(error)
                if len(errors) > 20:
                    st.info(f"... and {len(errors) - 20} more errors")
        
        if athletes:
            st.success(f"✅ Found {len(athletes)} valid athletes")
            
            # Preview
            with st.expander("👁️ Preview Athletes", expanded=True):
                import pandas as pd
                preview_data = []
                for a in athletes[:10]:  # Show first 10
                    preview_data.append({
                        'Name': a.get('full_name', ''),
                        'DOB': a.get('date_of_birth', ''),
                        'Gender': a.get('gender', ''),
                        'Belt': a.get('belt_rank', ''),
                        'Day': a.get('competition_day', '')
                    })
                st.dataframe(pd.DataFrame(preview_data), hide_index=True, use_container_width=True)
                
                if len(athletes) > 10:
                    st.info(f"... and {len(athletes) - 10} more athletes")
            
            # Confirm upload
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🚀 Register All", use_container_width=True, type="primary"):
                    with st.spinner("Registering athletes..."):
                        result = bulk_register_athletes(athletes)
                        
                        if result['success']:
                            st.success(f"✅ Successfully registered: **{result['successful']}** athletes")
                            
                            if result['failed'] > 0:
                                with st.expander(f"⚠️ {result['failed']} Failed"):
                                    for r in result['results']:
                                        if not r['success']:
                                            st.warning(f"{r['name']}: {r.get('error', 'Unknown error')}")
                            
                            st.balloons()
                        else:
                            st.error(f"❌ {result['error']}")
        elif not errors:
            st.warning("No valid athletes found in the file. Please check the format.")

# Tips section
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("💡 Tips for Successful Registration"):
    st.markdown("""
    **Single Entry:**
    - All fields marked with * are required
    - At least one event (Kata or Kumite) must be selected
    - Weight is optional but recommended
    
    **Bulk Upload:**
    - Use the provided template for best results
    - Required columns: Name, Date of Birth, Gender, Belt Rank, Competition Day
    - Dates can be in formats: YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY
    - Gender accepts: Male/Female, M/F, Boy/Girl
    - For events, use Yes/No, True/False, or 1/0
    
    **Duplicate Prevention:**
    - Duplicates are detected by Name + Date of Birth + Dojo combination
    - Existing athletes cannot be re-registered
    """)
