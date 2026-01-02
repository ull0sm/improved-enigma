"""
Sidebar Component
Navigation sidebar with role-based menu items
"""

import streamlit as st
from src.auth.session import is_authenticated, is_admin, get_current_coach, is_onboarding_complete
from src.auth.auth_handler import sign_out
from src.services.config_service import get_tournament_name


def render_sidebar():
    """Render the navigation sidebar."""
    
    with st.sidebar:
        # App Title/Logo
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0 2rem 0;">
                <h1 style="
                    font-size: 1.5rem; 
                    font-weight: 700;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin: 0;
                ">🥋 EntryDesk</h1>
                <p style="color: #64748b; font-size: 0.75rem; margin-top: 0.25rem;">
                    Tournament Manager
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Only show navigation if authenticated and onboarded
        if is_authenticated() and is_onboarding_complete():
            # User info
            coach = get_current_coach()
            if coach:
                dojo_name = coach.get('dojos', {}).get('name', 'Unknown Dojo') if isinstance(coach.get('dojos'), dict) else 'Unknown Dojo'
                st.markdown(f"""
                    <div style="
                        background: rgba(99, 102, 241, 0.1);
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        border-radius: 8px;
                        padding: 0.75rem;
                        margin-bottom: 1.5rem;
                    ">
                        <p style="color: #e2e8f0; font-weight: 500; margin: 0; font-size: 0.9rem;">
                            {coach.get('full_name', 'Coach')}
                        </p>
                        <p style="color: #64748b; font-size: 0.75rem; margin: 0.25rem 0 0 0;">
                            🏢 {dojo_name}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Main Navigation
            st.markdown('<p style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">Main Menu</p>', unsafe_allow_html=True)
            
            if st.button("🏠 Dashboard", use_container_width=True, key="nav_dashboard"):
                st.switch_page("pages/3_🏠_Dashboard.py")
            
            if st.button("➕ Register Athletes", use_container_width=True, key="nav_register"):
                st.switch_page("pages/4_➕_Register.py")
            
            if st.button("👥 My Athletes", use_container_width=True, key="nav_athletes"):
                st.switch_page("pages/5_👥_Athletes.py")
            
            if st.button("📥 Export Data", use_container_width=True, key="nav_export"):
                st.switch_page("pages/6_📥_Export.py")
            
            # Admin Section
            if is_admin():
                st.markdown("---")
                st.markdown('<p style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">🔐 Admin</p>', unsafe_allow_html=True)
                
                if st.button("📊 Global Overview", use_container_width=True, key="nav_admin_overview"):
                    st.switch_page("pages/7_📊_Admin_Overview.py")
                
                if st.button("👥 All Athletes", use_container_width=True, key="nav_admin_athletes"):
                    st.switch_page("pages/8_👥_All_Athletes.py")
                
                if st.button("📧 Manage Access", use_container_width=True, key="nav_admin_access"):
                    st.switch_page("pages/9_📧_Manage_Access.py")
                
                if st.button("⚙️ Settings", use_container_width=True, key="nav_admin_settings"):
                    st.switch_page("pages/10_⚙️_Settings.py")
                
                if st.button("📜 Audit Logs", use_container_width=True, key="nav_admin_audit"):
                    st.switch_page("pages/11_📜_Audit_Logs.py")
            
            # Logout
            st.markdown("---")
            if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
                clear_session()
                st.rerun()
                st.switch_page("pages/1_🔐_Login.py")
        
        # Footer
        st.markdown("""
            <div style="
                position: fixed;
                bottom: 1rem;
                left: 1rem;
                right: 1rem;
                text-align: center;
            ">
                <p style="color: #475569; font-size: 0.65rem; margin: 0;">
                    EntryDesk v1.0
                </p>
            </div>
        """, unsafe_allow_html=True)
